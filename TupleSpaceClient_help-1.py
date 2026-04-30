import socket
import sys
import os

def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((hostname, port))
    except socket.error as e:
        print(f"Error: Failed to connect to server {hostname}:{port} - {e}")
        sys.exit(1)
        

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.


    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            cmd = parts[0]
            message = ""
            valid = True
            error_msg = ""
            if cmd not in ["R", "G", "P"]:
                valid = False
                error_msg = "ERR Unknown operation"
            elif len(parts) < 2:
                valid = False
                error_msg = "ERR Invalid request format"
            else:
                key = parts[1]
            if len(key) > 999:
                    valid = False
                    error_msg = "ERR Key too long"
            if cmd in ["R", "G"]:
                    if len(parts) != 2:
                        valid = False
                        error_msg = "ERR Invalid READ/GET format"
                        if len(key) > 970:
                        valid = False
                        error_msg = "ERR Collated size exceeds 970 characters"
                        cmd_str = f"{cmd} {key}"
                        total_len = 4 + len(cmd_str)
                        if total_len > 999:
                        valid = False
                        error_msg = "ERR Message too long"
                        message = f"{total_len:03d} {cmd_str}"
                    elif cmd == "P":
                    if len(parts) < 3:
                        valid = False
                        error_msg = "ERR Invalid PUT format"
                    else:
                        value = parts[2]
                        if len(value) > 999:
                            valid = False
                            error_msg = "ERR Value too long"
                        collated_str = f"{key} {value}"
                        if len(collated_str) > 970:
                            valid = False
                            error_msg = "ERR Collated size exceeds 970 characters"
                        cmd_str = f"P {key} {value}"
                        total_len = 4 + len(cmd_str)
                        if total_len > 999:
                            valid = False
                            error_msg = "ERR Message too long"
                        message = f"{total_len:03d} {cmd_str}"

            if not valid:
                print(f"{line}: {error_msg}")
                continue
                    

            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            sock.sendall(message.encode("utf-8"))
            size_bytes = receive_n(sock, 3)
            if len(size_bytes) != 3:
                print(f"{line}: ERR Server disconnected unexpectedly")
                break
            try:
                resp_total_size = int(size_bytes.decode("utf-8"))
            except ValueError:
                print(f"{line}: ERR Invalid response size from server")
                break
            remaining_bytes = receive_n(sock, resp_total_size - 3)
            if len(remaining_bytes) != resp_total_size - 3:
                print(f"{line}: ERR Incomplete response from server")
                break
            response_buffer = remaining_bytes
            response = response_buffer.decode().strip()
            print(f"{line}: {response}")


            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.


            response = response_buffer.decode().strip()
            print(f"{line}: {response}")

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # TASK 4: Close the socket when done (already called for you — explain why
        # finally: is the right place to do this even if an error occurs above).
        sock.close()

if __name__ == "__main__":
    main()
