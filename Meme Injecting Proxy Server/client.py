import socket
import os
from urllib.parse import urlparse

def send_request(proxy_host, proxy_port, target_url):
    # Parse the URL to extract the hostname for the Host header.
    parsed = urlparse(target_url)
    host_header = parsed.hostname

    # Create a socket to connect to the proxy server.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((proxy_host, proxy_port))
    
    # Prepare an HTTP GET request.
    request = f"GET {target_url} HTTP/1.1\r\nHost: {host_header}\r\nConnection: close\r\n\r\n"
    client_socket.sendall(request.encode('utf-8'))
    
    # Receive the full response.
    response = b""
    while True:
        part = client_socket.recv(4096)
        if not part:
            break
        response += part
    client_socket.close()
    
    # Split headers from body.
    header_end = response.find(b"\r\n\r\n")
    if header_end != -1:
        headers = response[:header_end]
        body = response[header_end + 4:]
        headers_str = headers.decode('utf-8', errors='replace')
        print("Received headers:")
        print(headers_str)
        
        # Determine file extenrsion based on Content-Type header.
        content_type = None
        for line in headers_str.splitlines():
            if line.lower().startswith("content-type:"):
                content_type = line.split(":", 1)[1].strip().lower()
                break

        if content_type:
            if "image/png" in content_type:
                filename = "output.png"
            elif "image/jpeg" in content_type:
                filename = "output.jpg"
            elif "image/gif" in content_type:
                filename = "output.gif"
            elif "text/html" in content_type:
                filename = "output.html"
            else:
                filename = "output.dat"
        else:
            # Fallback to URL-based filename if content-type is not found.
            filename = os.path.basename(target_url)
            if not filename or '.' not in filename:
                filename = "output.html"
        
        # Save the response body to the determined file.
        with open(filename, "wb") as f:
            f.write(body)
        print(f"Response body saved to {filename}")
    else:
        print("Unexpected response format:")
        print(response.decode('utf-8', errors='replace'))

if __name__ == "__main__":
    PROXY_HOST = "127.0.0.1"
    PROXY_PORT = 8080
    # Ensure this is an HTTP URL (not HTTPS) for proper testing.
    TARGET_URL = "http://httpbin.org/image/png"
    send_request(PROXY_HOST, PROXY_PORT, TARGET_URL)
