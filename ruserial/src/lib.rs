use libc::{c_char, c_int};
use pyo3::exceptions::{PyValueError, PyRuntimeError};
use pyo3::prelude::*;
use std::ffi::CString;


unsafe extern "C" {
    fn start_serial_terminal(dev: *const c_char, baud: i32) -> c_int;
}

#[pyfunction]
#[pyo3(name = "start_serial")]
fn py_start_serial_terminal(dev_path: String, baud: i32) -> PyResult<()> {    
    let c_dev = CString::new(dev_path).map_err(|e| PyValueError::new_err(format!("Invalid device path string: {}", e)))?;    
    
    let result = unsafe {
        start_serial_terminal(c_dev.as_ptr(), baud as c_int)
    };

    if result == 0 {
        Ok(())
    } else {
        Err(PyRuntimeError::new_err(format!(
            "Failed to start serial terminal. Return code: {}", result
        )))    
    }
}

#[pymodule]
fn ruserial(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(py_start_serial_terminal, m)?)?;
    Ok(())
}

// main.rs
// use std::ffi::{CString, c_int};

// unsafe extern "C" {
//     fn start_serial_terminal(dev: *const libc::c_char, baud: i32) -> c_int;
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
//             let ret = start_serial_terminal(dev.as_ptr(), baud);
//             if ret != 0 {
//                 eprintln!("C function returned error code: {}", ret);
//             } else {
//                 println!("Terminal session ended gracefully.");
//             }
//         }
    
//         println!("Serial terminal exited.");
//     }
// }

