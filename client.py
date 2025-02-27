# Hamza Siddiqui
# 30183881

import socket

# Server configuration constants
SERVER_HOST = 'localhost'
SERVER_PORT = 12345
RETRY_LIMIT = 3 #  Retry limit is set to 3
TIMEOUT = 5  # seconds

#Encryption Helper Functions 
ENCRYPTION_KEY = 23  # Must match the server's key

def encrypt_message(message, key=ENCRYPTION_KEY):
    return ''.join(chr(ord(c) ^ key) for c in message)

def decrypt_message(message, key=ENCRYPTION_KEY):
    return ''.join(chr(ord(c) ^ key) for c in message)

def start_client():
    """Starts the client and provides a menu to select the palindrome check type."""
    while True:
        # Display the menu
        print("\nMenu:")
        print("1. Simple Palindrome Check")
        print("2. Complex Palindrome Check")
        print("3. Exit")
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice == '1':
            input_string = input("Enter the string to check: ")
            message = f"simple|{input_string}"
        elif choice == '2':
            input_string = input("Enter the string to check: ")
            message = f"complex|{input_string}"
        elif choice == '3':
            print("Exiting the client...")
            break
        else:
            print("Invalid choice. Please try again.")
            continue

        # Encrypt the message before sending
        encrypted_message = encrypt_message(message)

        # Try connecting to the server and send the message with a retry mechanism.
        attempts = 0
        while attempts < RETRY_LIMIT:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.settimeout(TIMEOUT)
                    client_socket.connect((SERVER_HOST, SERVER_PORT))
                    client_socket.send(encrypted_message.encode())
                    encrypted_response = client_socket.recv(1024).decode()
                    # Decrypt the response received from the server
                    response = decrypt_message(encrypted_response)
                    print(f"Server response:\n\n{response}")
                    break  # Successful communication, exit retry loop
            except socket.timeout:
                attempts += 1
                print(f"Timeout occurred. Attempt {attempts} of {RETRY_LIMIT}.")
                if attempts == RETRY_LIMIT:
                    print("Server did not respond after multiple attempts. Please try again later.")
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    start_client()
