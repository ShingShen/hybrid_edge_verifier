# import subprocess
# import os

# def run_ssh_command_with_expect(config, command_to_run):
#     """
#     A helper function to run a single command via SSH using an expect script in Docker.
#     This encapsulates the logic of creating a script, running it in a container, and cleaning up.

#     Returns a tuple: (success, output_string)
#     """
#     ip = config.get('ip')
#     username = config.get('user')
#     password = config.get('password')
#     # Go up two levels from `utils` directory to get the project root
#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
#     # Use the system's temporary directory for the script for better cleanup
#     # and to avoid cluttering the project directory.
#     temp_dir = os.environ.get("TMPDIR", "/tmp")
#     script_path = os.path.join(temp_dir, f"temp_ssh_script_{os.getpid()}.sh")

#     # Escape special Tcl characters in the password to prevent script injection
#     # or syntax errors. The main characters to escape are $, ", and [.
#     escaped_password = password.replace('$', '\\$').replace('"', '\\"').replace('[', '\\[').replace('{', '\\{')

#     # The expect script is now more robust.
#     # - It uses a raw f-string (fr) to avoid complex backslash escaping.
#     # - `set password` now uses the escaped password.
#     # - Timeouts provide more specific error messages.
#     # - `stty -echo` is used to prevent the command from being echoed in the output.
#     expect_script_content = fr"""
# #!/usr/bin/expect -f
# # This script is generated and executed by the test framework.

# # We pass the password in quotes to handle most special characters.
# set password "{escaped_password}"
# set prompt {{[>#]\s*$}}
# set timeout 20

# # Start the SSH connection
# # -tt is used to force a pseudo-terminal, which is often required for interactive sessions.
# spawn ssh -tt -o HostKeyAlgorithms=+ssh-rsa -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {username}@{ip}

# # Expect a password prompt
# expect {{
#   timeout {{ send_user "FAIL: Timeout waiting for password prompt.\n"; exit 1 }}
#   "password:"
# }}

# # Send the password
# send "$password\r"

# # Expect the shell prompt, handling the "change password" message
# expect {{
#   timeout {{ send_user "FAIL: Timeout waiting for shell prompt after login.\n"; exit 1 }}
#   "please change the default password" {{ exp_continue }}
#   -re $prompt
# }}

# # Disable terminal echo to prevent the command from appearing in the output
# send "stty -echo\r"
# expect -re $prompt

# # Send the actual command to run
# send "{command_to_run}\r"

# # Expect the prompt again. The lines between the command and the next prompt
# # are the actual output of the command.
# expect -re $prompt

# # Re-enable echo and then exit
# send "stty echo\r"
# expect -re $prompt
# send "exit\r"
# expect eof
# """

#     # The Docker volume mount path MUST use forward slashes for cross-platform compatibility.
#     project_root_docker = project_root.replace('\\', '/')
#     temp_dir_docker = temp_dir.replace('\\', '/')

#     docker_command = [
#         "docker", "run", "--rm", "-i",
#         "-v", f"{project_root_docker}:/usr/src/app",
#         # Mount the temp dir to make the script accessible
#         "-v", f"{temp_dir_docker}:{temp_dir_docker}",
#         "hybrid_edge_verifier",
#         # Use 'expect' directly to run the script, which is more direct.
#         "/usr/bin/expect", "-f", script_path
#     ]

#     try:
#         # Write the temporary script file to the host filesystem using UTF-8 and LF line endings
#         with open(script_path, "w", newline='\n', encoding='utf-8') as f:
#             f.write(expect_script_content)

#         # Run the docker command
#         process = subprocess.run(
#             docker_command,
#             capture_output=True,
#             text=True,
#             timeout=60,
#             encoding='utf-8'
#         )
        
#         # Check for non-zero return code, which indicates a script failure (e.g., timeout)
#         if process.returncode != 0:
#             # The error message from `send_user` in the script will be in stdout
#             error_message = process.stdout.strip() or process.stderr.strip()
#             return False, f"Docker/Expect script failed. Output: {error_message}"

#         # If successful, the output of the executed command is in stdout.
#         return True, process.stdout

#     except FileNotFoundError:
#         return False, "Docker command not found. Is Docker installed and in the PATH?"
#     except subprocess.TimeoutExpired:
#         return False, "Command execution timed out after 60 seconds."
#     except Exception as e:
#         return False, f"An unexpected error occurred: {e}"
#     finally:
#         # Clean up the temporary script
#         if os.path.exists(script_path):
#             os.remove(script_path)

import subprocess
import os

def run_ssh_command_with_expect(config, command_to_run):
    """
    A helper function to run a single command via SSH using an expect script in Docker.
    This encapsulates the logic of creating a script, running it in a container, and cleaning up.

    Returns a tuple: (success, output_string)
    """
    ip = config.get('ip')
    username = config.get('user')
    password = config.get('password')
    # Go up two levels from `utils` directory to get the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Use the system's temporary directory for the script for better cleanup
    # and to avoid cluttering the project directory.
    temp_dir = os.environ.get("TMPDIR", "/tmp")
    script_path = os.path.join(temp_dir, f"temp_ssh_script_{os.getpid()}.sh")

    # Escape special Tcl characters in the password to prevent script injection
    # or syntax errors. The main characters to escape are $, ", and [.
    escaped_password = password.replace('$', '\\$').replace('"', '\\"').replace('[', '\\[').replace('{', '\\{')

    # The expect script is now more robust.
    # - It uses a raw f-string (fr) to avoid complex backslash escaping.
    # - `set password` now uses the escaped password.
    # - Timeouts provide more specific error messages.
    # - `stty -echo` is used to prevent the command from being echoed in the output.
    
    prompt_regex = r"(?n)^.*[#$]\s*$"
    
    expect_script_content = fr"""
#!/usr/bin/expect -f
# This script is generated and executed by the test framework.

# We pass the password in quotes to handle most special characters.
set password "{escaped_password}"
set prompt {{[{prompt_regex}}}
set timeout 20

# Start the SSH connection
# -tt is used to force a pseudo-terminal, which is often required for interactive sessions.
spawn ssh -tt -o HostKeyAlgorithms=+ssh-rsa -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {username}@{ip}

# Expect a password prompt
expect {{
  timeout {{ send_user "FAIL: Timeout waiting for password prompt.\n"; exit 1 }}
  "password:"
}}

# Send the password
send "$password\r"

# Expect the shell prompt, handling the "change password" message
expect {{
  timeout {{ send_user "FAIL: Timeout waiting for shell prompt after login.\n"; exit 1 }}
  -re $prompt
}}

# Disable terminal echo to prevent the command from appearing in the output
send "stty -echo\r"
expect -re $prompt

# Send the actual command to run
send "{command_to_run}\r"

# Expect the prompt again. The lines between the command and the next prompt
# are the actual output of the command.
expect -re $prompt

set output $expect_out(buffer)

regsub -all $prompt $output "" output

send "exit\r"
expect eof
"""

    # The Docker volume mount path MUST use forward slashes for cross-platform compatibility.
    project_root_docker = project_root.replace('\\', '/')
    temp_dir_docker = temp_dir.replace('\\', '/')

    docker_command = [
        "docker", "run", "--rm", "-i",
        "-v", f"{project_root_docker}:/usr/src/app",
        # Mount the temp dir to make the script accessible
        "-v", f"{temp_dir_docker}:{temp_dir_docker}",
        "hybrid_edge_verifier",
        # Use 'expect' directly to run the script, which is more direct.
        "/usr/bin/expect", "-f", script_path
    ]

    try:
        # Write the temporary script file to the host filesystem using UTF-8 and LF line endings
        with open(script_path, "w", newline='\n', encoding='utf-8') as f:
            f.write(expect_script_content)

        # Run the docker command
        process = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )
        
        # Check for non-zero return code, which indicates a script failure (e.g., timeout)
        if process.returncode != 0:
            # The error message from `send_user` in the script will be in stdout
            error_message = process.stdout.strip() or process.stderr.strip()
            return False, f"SSH script failed. Output: {error_message}"

        # If successful, the output of the executed command is in stdout.
        print(process.stdout.strip())
        return True, process.stdout.strip()

    except FileNotFoundError:
        return False, "Docker command not found. Is Docker installed and in the PATH?"
    except subprocess.TimeoutExpired:
        return False, "Command execution timed out after 60 seconds."
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"
    finally:
        # Clean up the temporary script
        if os.path.exists(script_path):
            os.remove(script_path)