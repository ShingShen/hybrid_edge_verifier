# M/M/c/K Queue Test (Rust + Python)

## 🛠 Prerequisites

* **Rust Toolchain:** (latest stable version)
* Install via: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`


* **Python 3.x:** Ensure `python3` is in your system PATH.

## 📂 Project Structure

```text
.
├── Cargo.toml                 # Rust dependencies (tokio, serde, sysinfo, etc.)
├── src/
│   └── main.rs                # Core logic: M/M/c/K calculation & Process management
├── python/
│   ├── worker.py              # The heavy computation script invoked by Rust
│   └── client_simulator.py    # Simulation tool for stress testing
└── README.md

```

## ⚙️ Configuration

The M/M/c/K parameters are configured in `src/main.rs`. You can tune these values based on your QoS requirements:

```rust
// src/main.rs

// max_latency_ms: Maximum time a request is allowed to wait in the queue.
// avg_service_time_ms: Estimated time for Python to finish one task.
let protector = Arc::new(SystemProtector::new(500, 100.0));

```

* **Latency Budget (500ms):** If the queue is too long such that a new request would wait >500ms, the queue capacity () limits further additions.
* **Service Time (100ms):** Used to calculate the throughput rate ().

## 🚀 Usage

### 1. Start the Gateway Server (Rust)

Open a terminal and run the Rust server. We recommend enabling logging to see the worker status.

```bash
# Linux / macOS
export RUST_LOG=info
cargo run

# Windows (PowerShell)
$env:RUST_LOG="info"
cargo run

```

You should see initialization logs indicating the calculated Queue Capacity () based on your CPU cores:

```text
--- System Initialization ---
CPU Cores Available: 8
Active Workers (c): 7
Queue Capacity (K-c): 35
Max Latency Budget: 500 ms
Gateway listening on 127.0.0.1:8080

```

### 2. Run the Traffic Simulator (Python)

Open a **second terminal** to simulate a burst of traffic (SSH, Telnet, Serial requests).

```bash
python3 python/client_simulator.py

```

### 3. Observe the Protection Mechanism

* **Under Normal Load:** You will see "Request Accepted" in the client terminal and execution logs in the Rust terminal.
* **Under Heavy Load:** The Rust server will enforce admission control. You will see logs indicating **rejected requests**:
* **Rust Log:** `WARN: Dropped request from 127.0.0.1... due to overload!`
* **Client Log:** `[SSH] Request BLOCKED (System Protected)`



## 🧮 Theoretical Background: M/M/c/K

This system uses Little's Law to determine the Buffer Size ():

$$ K_{buffer} = c \times \frac{T_{max_wait}}{T_{service}} $$

Where:

* : Number of active workers (Logical Cores - 1).
* : Your defined latency budget (e.g., 500ms).
* : Average time to process a task (e.g., 100ms).

This ensures that the queue never grows beyond a length that would cause a timeout, effectively preventing **Bufferbloat**.