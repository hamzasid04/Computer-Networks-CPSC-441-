import socket
import threading
import re
import random
import base64
import os
import time
from urllib.parse import urlparse

# Configuration
HOST = '127.0.0.1'  # Proxy will listen on localhost on this certain IP adress and the IP that we set firefox to use 
PORT = 8080         # Proxy port that browser will listen to on  
CHUNK_SIZE = 1024   # Data chunk size when receiving responses
DELAY = 0.0         # Delay in seconds per chunk (set to 0 for no delay)
#Path to my meme folder that contains at least 15 meme images
MEME_FOLDER = "C:\\CPSC 441\\Assignment 2\\Memes"

def inject_memes(html_content, meme_folder):
    """
    For HTML responses, find <img> tags and, with a 50% chance of reaplacing them, and then we replace their src attribute
    with meme image from the specified folder.
    """
    try:
        #Lists all files in the meme fodler
        meme_files = os.listdir(meme_folder)
    except Exception as e:
        print(f"Error accessing meme folder: {e}")
        return html_content #return orignal html page if error occurs

    if not meme_files:
        return html_content  # If no memes found, return the original HTML page

    def replace_img(match):
        original_tag_start = match.group(1)  # e.g., <img ... src="
        original_src = match.group(2)          # Original image URL
        original_tag_end = match.group(3)      # e.g., " ... >
        # Ensures that all images be replaced by a meme with a 50% chance
        if random.random() < 0.5:
            chosen_meme = random.choice(meme_files) #randomly selects a meme file
            meme_path = os.path.join(meme_folder, chosen_meme) #construct a full path to meme file
            try:
                with open(meme_path, "rb") as f:
                    meme_data = f.read()
                meme_b64 = base64.b64encode(meme_data).decode('utf-8')
                # Determine MIME type from file extension
                ext = chosen_meme.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg']:
                    mime_type = 'image/jpeg'
                elif ext == 'png':
                    mime_type = 'image/png'
                elif ext == 'gif':
                    mime_type = 'image/gif'
                else:
                    mime_type = 'application/octet-stream'
                # Create a new src attribute using a data URL containing the meme image
                new_src = f"data:{mime_type};base64,{meme_b64}"
                # Return the modified <img> tag with the meme image in it 
                return original_tag_start + new_src + original_tag_end
            except Exception as e:
                print(f"Error reading meme file: {e}")
                return match.group(0) # if error, return orignal tag
        else:
            return match.group(0) #With 50% chance, do not replace the meme

    pattern = r'(<img\s+[^>]*src=["\'])([^"\']+)(["\'][^>]*>)'
    modified_html = re.sub(pattern, replace_img, html_content, flags=re.IGNORECASE)
    return modified_html

def handle_client(client_socket):
    """
    Handles a client connection: reads the request, processes it,
    retrieves the content from the target server, modifies the response if necessary,
    and sends the final response back to the client.
    """
    try:
        # Receive the client's request.
        request = client_socket.recv(4096)
        if not request:
            client_socket.close()
            return

        # Extract the first line and get the requested HTTP method and URL.
        first_line = request.split(b'\r\n')[0]
        parts = first_line.split(b' ')
        if len(parts) < 2 or parts[1] is None:
            client_socket.close()
            return
        url = parts[1]
        try:
            decoded_url = url.decode('utf-8')
        except Exception as e:
            print(f"URL decode error: {e}")
            client_socket.close()
            return

        # --- Easter Egg Handling ---
        # If the requested URL contains "google.ca", return a custom meme page

        if "google.ca" in decoded_url:
            try:
                meme_files = os.listdir(MEME_FOLDER)
            except Exception as e:
                print(f"Easter egg folder error: {e}")
                meme_files = []
            if meme_files:
                chosen_meme = random.choice(meme_files)
                meme_path = os.path.join(MEME_FOLDER, chosen_meme)
                try:
                    with open(meme_path, "rb") as f:
                        meme_data = f.read() # Read the meme image data
                    meme_b64 = base64.b64encode(meme_data).decode('utf-8')
                    ext = chosen_meme.split('.')[-1].lower()
                    if ext in ['jpg', 'jpeg']:
                        mime_type = 'image/jpeg'
                    elif ext == 'png':
                        mime_type = 'image/png'
                    elif ext == 'gif':
                        mime_type = 'image/gif'
                    else:
                        mime_type = 'application/octet-stream'
                    # Construct a custom HTML page for the Easter Egg
                    easter_html = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html\r\n\r\n"
                        "<html><head><title>Surprise!</title></head>"
                        "<body style='margin:0; padding:0;'>"
                        f"<img src='data:{mime_type};base64,{meme_b64}' style='width:100%; height:100vh; object-fit:cover;'>"
                        "<h1 style='position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); "
                        "color:grey; font-size:3em;'>Not so fast Mochi!<br>\n</h1>"
                        "<p >hehehehe</p>"
                        "</body></html>"
                    )
                     # Send the custom Easter Egg HTML response to the client

                    client_socket.sendall(easter_html.encode('utf-8'))
                except Exception as e:
                    print(f"Easter egg error: {e}")
            else:
             # If the meme folder is empty, send a simple text response
                client_socket.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nMeme folder is empty.")
            client_socket.close()
            return

        # --- HTTPS Check ---
        # If the URL starts with "https://", do not process it and send an error response
        if decoded_url.startswith("https://"):
            error_response = (
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: text/plain\r\n\r\n"
                "HTTPS requests are not supported by this proxy."
            )
            client_socket.sendall(error_response.encode('utf-8'))
            client_socket.close()
            return

        # Parse URL components.
        parsed_url = urlparse(decoded_url)
        host = parsed_url.hostname
        if host is None:
            client_socket.close()
            return
        # Use the provided port if any; otherwise, default to port 80 for HTTP
        port = parsed_url.port if parsed_url.port else 80
        path = parsed_url.path if parsed_url.path else '/'
        if parsed_url.query:
            path += "?" + parsed_url.query

        # Create a socket to connect to the remote server.
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((host, port))
        # Forward the original client request to the target server

        remote_socket.sendall(request)

        # Bufer the entire response from the remote server.
        full_response = b""
        while True:
            chunk = remote_socket.recv(CHUNK_SIZE)
            if not chunk:
                break
            full_response += chunk
            if DELAY > 0:
                time.sleep(DELAY)
        remote_socket.close()

        # Split response into haeder's and body.
        header_end = full_response.find(b"\r\n\r\n")
        if header_end != -1:
            headers = full_response[:header_end]
            body = full_response[header_end + 4:]
            
            # Check for HTML responses.
            if b"Content-Type: text/html" in headers:
                try:
                    html_content = body.decode('utf-8', errors='replace')
                    modified_html = inject_memes(html_content, MEME_FOLDER)
                    body = modified_html.encode('utf-8')
                    full_response = headers + b"\r\n\r\n" + body
                except Exception as e:
                    print(f"Error modifying HTML: {e}")
            
            # Check for direct image responses.
            elif b"Content-Type: image/" in headers:
                if random.random() < 0.5:  # Replace with a meme 50% of the time.
                    try:
                        meme_files = os.listdir(MEME_FOLDER)
                        if meme_files:
                            chosen_meme = random.choice(meme_files)
                            meme_path = os.path.join(MEME_FOLDER, chosen_meme)
                            with open(meme_path, "rb") as f:
                                meme_data = f.read()
                            # Determine MIME type based on the meme file extension.
                            ext = chosen_meme.split('.')[-1].lower()
                            if ext in ['jpg', 'jpeg']:
                                mime_type = 'image/jpeg'
                            elif ext == 'png':
                                mime_type = 'image/png'
                            elif ext == 'gif':
                                mime_type = 'image/gif'
                            else:
                                mime_type = 'application/octet-stream'
                            # Construct new headers with updated Content-Length and Content-Type.
                            new_headers = b"HTTP/1.1 200 OK\r\n"
                            new_headers += f"Content-Type: {mime_type}\r\n".encode('utf-8')
                            new_headers += f"Content-Length: {len(meme_data)}\r\n".encode('utf-8')
                            new_headers += b"Connection: close\r\n\r\n"
                            full_response = new_headers + meme_data
                        # Else: If no meme files, leave the response unchanged.
                    except Exception as e:
                        print(f"Error replacing image: {e}")
        # Send the (possibly modified) response back to the client.
        client_socket.sendall(full_response)
    except Exception as e:
        print(f"Error in handle_client: {e}")
    finally:
        client_socket.close()

def start_proxy():
    """
    Initializes the proxy server socket, binds to the specified HOST and PORT,
    and continuously listens for incoming client connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow the socket to reuse the address to avoid "address already in use" errors
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5) # Listen to up to 5 connections 
    print(f"Proxy server running on {HOST}:{PORT}...")
    try:
        while True:
            # Accept incoming client connections
            client_sock, addr = server_socket.accept()
            print(f"Connection from {addr}")
            # Start a new thread to handle the client connection
            client_thread = threading.Thread(target=handle_client, args=(client_sock,))
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down proxy server.")
    finally:
        server_socket.close() # Close the server socket when finished

if __name__ == "__main__":
    start_proxy() # Start the proxy server when this script is run
