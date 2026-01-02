// use std::ffi::CString;

// unsafe extern "C" {
//     fn start_serial_terminal(dev: *const libc::c_char, baud: i32);
// }

// fn main() {
//     let args: Vec<String> = std::env::args().collect();
//     if args.len() == 3 {
//         let dev = CString::new(args[1].clone()).expect("CString::new failed");
//         let baud: i32 = args[2].parse().unwrap_or_else(|_| {
//             eprintln!("Invalid baudrate.");
//             std::process::exit(1);
//         });
    
//         unsafe {
//             start_serial_terminal(dev.as_ptr(), baud);
//         }
    
//         println!("Serial terminal exited.");
//     }
// }

use std::ffi::{CString, c_int};

unsafe extern "C" {
    fn start_serial_terminal(dev: *const libc::c_char, baud: i32) -> c_int;
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() == 3 {
        let dev = CString::new(args[1].clone()).expect("CString::new failed");
        let baud: i32 = args[2].parse().unwrap_or_else(|_| {
            eprintln!("Invalid baudrate.");
            std::process::exit(1);
        });
    
        unsafe {
            let ret = start_serial_terminal(dev.as_ptr(), baud);
            if ret != 0 {
                eprintln!("C function returned error code: {}", ret);
            } else {
                println!("Terminal session ended gracefully.");
            }
        }
    
        println!("Serial terminal exited.");
    }
}

