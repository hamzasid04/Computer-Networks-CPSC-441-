# Hamza Siddiqui
# 30183881

import socket
import threading # to handle multiple clients using multi threading
import logging #to record all the messages and information into server_log.txt
import re #to be able to remove the spaces, punctuation and make it lowercase in the palidndrome check
from collections import Counter

# Encryption Helper Functions 
ENCRYPTION_KEY = 23  # A fixed key for the simple XOR cipher

#Cipher implmentation to encrypt and decrypt message
def encrypt_message(message, key=ENCRYPTION_KEY):
    return ''.join(chr(ord(c) ^ key) for c in message)

def decrypt_message(message, key=ENCRYPTION_KEY):
    return ''.join(chr(ord(c) ^ key) for c in message)

# Set up logging to document all messages in 'server_log_info.txt'
logging.basicConfig(filename='server_log_info.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Server configuration constants
HOST = 'localhost'
PORT = 12345

def handle_client(client_socket, client_address):
    """
    Handles incoming client connections.
    Receives a request, processes it, and sends back a response.
    """
    logging.info(f"Connection from {client_address}")
    try:
        while True:
            # Receive data (up to 1024 bytes) from the client
            encrypted_data = client_socket.recv(1024)
            if not encrypted_data:
                break  # No data means the client closed the connection

            # Decrypt the received message
            request_data = decrypt_message(encrypted_data.decode())
            logging.info(f"Received request: {request_data}")
            response = process_request(request_data, client_address)
            # Encrypt the response before sending it
            encrypted_response = encrypt_message(response)
            client_socket.send(encrypted_response.encode())
            logging.info(f"Sent response: {response}")
    finally:
        client_socket.close()
        logging.info(f"Closed connection with {client_address}")

def process_request(request_data, client_address):
    """
    Processes the client's request.
    Expects request_data in the format: <check_type>|<input_string>
    
    For a 'simple' or option '2' check, cleans the input and it determines if the input string is a palindrome.
    For a 'complex' or option '2' checks if the cleaned input can be rearranged into a palindrome and calculates the minimum swaps which is the complexity score.

    Logs all the details: the client IP, simple or complex check, input string, result, and complexity score if possible
    """
    try:
        # We split the message sent from the client and server then splits it with whatever was before the '|' indicates cehck type weather it's 'simple' or 'complex' palindrome and after the '|' represetns the input client gave us
        check_type, input_string = request_data.split('|', 1)   
    except ValueError:
        logging.info(f"Client {client_address} sent invalid format: {request_data}")
        return "Error: Invalid request format. Use: type|string"

    # clean_string: is our private function used to be able to clean the string and remove remove non-alphanumeric characters and convert to lowercase 
    def clean_string(input_string):
        return re.sub(r'[^a-zA-Z]', '', input_string).lower()#We use the re library to be able to use it's function adn clean the string
    
     # Clean the input string once so cleaned string is availble on both complex and simple.
    cleaned_string = clean_string(input_string)
    
    if check_type == 'simple':
        result = is_palindrome(cleaned_string)
        logging.info(f"Client {client_address} requested SIMPLE check. Input: '{input_string}'. Result: {result}")
        return f"Is palindrome: {result}"
    elif check_type == 'complex':
        can_form, swaps = complex_palindrome_check(cleaned_string)
        if can_form:
            # Log details for the complex check when it  succeeds.
            logging.info(f"Client {client_address} requested COMPLEX check. Input: '{input_string}'. Result: True, Complexity score: {swaps}")
            return f"Can form a palindrome: True\nComplexity score: {swaps}"
        else:
            # Log details for the complex check that fails.
            logging.info(f"Client {client_address} requested COMPLEX check. Input: '{input_string}'. Result: False")
            return "Can form a palindrome: False"
    else:
        logging.info(f"Client {client_address} sent unknown check type: {check_type}")
        return "Error: Unknown check type."

def is_palindrome(input_string):
    """
    Returns True if input_string is a palindrome; otherwise, returns False.
    """
    return input_string == input_string[::-1]

def complex_palindrome_check(s):
    """
    Checks whether the cleaned string can be rearranged into a palidondrome at least once and if so, the complexity score will tell us the min num of swaps to be able to accomplish it 
    Steps:
      1. Count character frequencies. For 's' (cleaned string we had inserted) to be rearrangeable into a palindrome,
         sicne there can be at most one character with an odd count.
      2. If possible, construct a target palindrome:
         - Build the left half by taking each character (in sorted order) count//2 times.
         - If a character has an odd count, assign it it as the middle character.
         - The target palindrome is left_half + middle + reversed(left_half).
      3. Compute the number of swaps needed to transform 's' into the target arrangement.
         (This greedy algorithm that we are using and it scans left to right and swaps s[i] with the first later
          occurrence of the character that should be at position i. For example, with
          "ivicc" transforming into "civic", the algorithm will find 2 swaps.)
    """
    # Step 1: Check possibility
    #If odd_count is more than 1, it means that there are too many characters with an odd count to rearrange the string into a palindrome.
    # Ex: civic, freq = {'i': 2, 'v': 1, 'c': 2} which means that there still is a chance that word can be reaaranged into a plaidonrome as num of odd character is just 1 right now not greater than 1.
    # If odd_count was greater than 1, it will naturally mean that there are too many odd numbers of a character to be rearranged into a palindrome.
    # In that case, the function returns (False, 0), where False indicates that the string cannot be rearranged into a palindrome and 0 is a placeholder for the complexity score (num of swaps = 0).
    freq = Counter(s)
    odd_count = sum(1 for count in freq.values() if count % 2 != 0)
    if odd_count > 1:
        return (False, 0)  # Cannot form a palindrome
    
    # Step 2: Construct one possible target palindrome (deterministic using sorted order)
    left_half = []
    middle = ""
    for char in sorted(freq.keys()):
        left_half.append(char * (freq[char] // 2))
        if freq[char] % 2 != 0:
            middle = char  # If more than one odd exists, we would have returned already
    left_half = "".join(left_half)
    target = left_half + middle + left_half[::-1]
    
    # Step 3: Compute minimum swaps needed 
    # Greedy algorithm: for each index, if the character does not match the target,
    # swap it with the first occurrence later in the string that does.
    s_list = list(s)
    t_list = list(target)
    swaps = 0
    for i in range(len(s_list)):
        if s_list[i] == t_list[i]:
            continue
        for j in range(i + 1, len(s_list)):
            if s_list[j] == t_list[i]:
                # Swap s_list[i] and s_list[j]
                s_list[i], s_list[j] = s_list[j], s_list[i]
                swaps += 1
                break
    return (True, swaps)

def start_server():
    """
    Creates the server socket, binds to HOST and PORT,
    and listens for incoming client connections.
    Each client is handled concurrently using a separate thread.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)  # Up to 5 queued connections
        logging.info(f"Server started and listening on {HOST}:{PORT}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client,
                             args=(client_socket, client_address)).start()

if __name__ == '__main__':
    start_server()
