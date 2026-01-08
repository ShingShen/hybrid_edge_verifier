use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::sync::mpsc;
use tokio::process::Command;
use std::sync::Arc;
use serde::{Deserialize, Serialize};
use sysinfo::System;

// --- Data Structures ---

/// Represents a job request coming from SSH, Telnet, or Serial interfaces.
#[derive(Debug, Deserialize, Serialize)]
struct JobRequest {
    source: String,      // e.g., "SSH", "Serial", "Telnet"
    command: String,     // The operation to perform
    params: Vec<f64>,    // Parameters for calculation
}

/// The core system protector that manages the M/M/c/K queue.
struct SystemProtector {
    tx: mpsc::Sender<JobRequest>,
}

impl SystemProtector {
    /// Initializes the protector with M/M/c/K parameters.
    /// # Arguments
    /// * `max_latency_ms` - The maximum acceptable wait time for a request in the queue.
    /// * `avg_service_time_ms` - The estimated average time Python takes to process one task.
    fn new(max_latency_ms: u64, avg_service_time_ms: f64) -> Self {
        let mut sys = System::new_all();
        sys.refresh_cpu();
        
        // --- 1. Determine 'c' (Number of Consumers/Workers) ---
        // Strategy: Leave 1 core free for OS/IO tasks to prevent system freeze.
        let logical_cpus = sys.cpus().len();
        let c = if logical_cpus > 1 { logical_cpus - 1 } else { 1 };
        
        // --- 2. Determine 'K' (System Capacity) ---
        // Formula: Buffer = c * (Max Wait Time / Average Service Time)
        // This ensures the queue length doesn't exceed the latency budget.
        let processing_rate = 1.0 / avg_service_time_ms; // tasks per ms per core
        let max_waiting_tasks = (c as f64 * (max_latency_ms as f64 * processing_rate)) as usize;
        
        // Set a minimum buffer size to handle burst traffic safely.
        let buffer_size = std::cmp::max(10, max_waiting_tasks);

        println!("--- System Initialization ---");
        println!("CPU Cores Available: {}", logical_cpus);
        println!("Active Workers (c): {}", c);
        println!("Queue Capacity (K-c): {}", buffer_size);
        println!("Max Latency Budget: {} ms", max_latency_ms);
        println!("-----------------------------");

        // Create the MPSC (Multi-Producer, Single-Consumer) channel acting as the Queue.
        let (tx, rx) = mpsc::channel(buffer_size);
        let rx = Arc::new(tokio::sync::Mutex::new(rx));

        // --- 3. Spawn Worker Pool ---
        for i in 0..c {
            let rx_clone = rx.clone();
            tokio::spawn(async move {
                worker_loop(i, rx_clone).await;
            });
        }

        SystemProtector { tx }
    }
}

/// The worker loop running in a dedicated thread (Green Thread).
/// It pulls jobs from the queue and spawns a Python subprocess to execute them.
async fn worker_loop(worker_id: usize, rx: Arc<tokio::sync::Mutex<mpsc::Receiver<JobRequest>>>) {
    loop {
        // 1. Fetch job from the queue (Thread-safe lock)
        let job = {
            let mut lock = rx.lock().await;
            lock.recv().await
        };

        match job {
            Some(req) => {
                log::info!("[Worker {}] Processing request from: {}", worker_id, req.source);
                
                // 2. Prepare arguments for Python
                // Serialize parameters to JSON string to pass via CLI arguments
                let args_json = serde_json::to_string(&req.params).unwrap_or_default();
                
                // 3. Spawn Python Subprocess (Isolation)
                // Using 'python3' (ensure it's in your PATH) and the worker script.
                // Note: In production, consider using full paths for robustness.
                let start_time = std::time::Instant::now();
                
                let output = Command::new("python3")
                    .arg("utils/worker.py") 
                    .arg(&req.command)
                    .arg(&args_json)
                    .output()
                    .await;

                let duration = start_time.elapsed();

                match output {
                    Ok(out) => {
                        if out.status.success() {
                            let result = String::from_utf8_lossy(&out.stdout);
                            log::info!("[Worker {}] Success ({:?}): {}", worker_id, duration, result.trim());
                        } else {
                            let error = String::from_utf8_lossy(&out.stderr);
                            log::error!("[Worker {}] Python Error: {}", worker_id, error);
                        }
                    }
                    Err(e) => {
                        log::error!("[Worker {}] Failed to spawn python process: {}", worker_id, e);
                    }
                }
            }
            None => break, // Channel closed, exit worker
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logger (Run with RUST_LOG=info cargo run)
    env_logger::init();

    // Configuration:
    // - Max Latency: 500ms (Interactive feel)
    // - Avg Service Time: 100ms (Estimated calculation time per task)
    let protector = Arc::new(SystemProtector::new(500, 100.0));
    
    // Start TCP Listener (Simulating a Gateway Entry Point)
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    log::info!("Gateway listening on 127.0.0.1:8080");

    loop {
        let (mut socket, addr) = listener.accept().await?;
        let protector_clone = protector.clone();

        tokio::spawn(async move {
            let mut buf = [0; 1024];
            
            // Read incoming request
            match socket.read(&mut buf).await {
                Ok(n) if n > 0 => {
                    let body = String::from_utf8_lossy(&buf[0..n]);
                    
                    // Parse JSON request
                    if let Ok(job) = serde_json::from_str::<JobRequest>(&body) {
                        
                        // --- Critical Section: M/M/c/K Admission Control ---
                        match protector_clone.tx.try_send(job) {
                            Ok(_) => {
                                // Accepted: Queue has space
                                let _ = socket.write_all(b"{\"status\": \"Accepted\"}").await;
                            }
                            Err(_) => {
                                // Rejected: Queue is full (Load Shedding)
                                // This protects the CPU from overload.
                                log::warn!("Dropped request from {} due to overload!", addr);
                                let _ = socket.write_all(b"{\"status\": \"Rejected\", \"reason\": \"Server Busy\"}").await;
                            }
                        }
                    } else {
                        let _ = socket.write_all(b"{\"status\": \"Error\", \"reason\": \"Invalid JSON\"}").await;
                    }
                }
                _ => {}
            }
        });
    }
}