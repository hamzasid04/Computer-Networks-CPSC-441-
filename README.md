# Assignbment 1 CPSC 441. Advanced Palindrome Check (Server-Client Application)

## Overview
This project is a server-client application that uses Python socket programming to carry out advanced palindrome verification. It is able to:
- **Simple Palindrome Check:** By disregarding case, spaces, and special characters, the Simple Palindrome Check determines if a given string is a palindrome.
- **Complex Palindrome Check:** Determines the complexity score (the bare minimum of swaps needed) and determines whether the string can be rearranged into a palindrome.
- **Multithreading:** The server can manage several clients at once thanks to multithreading.
- **Logging:** In 'server_logging_info.txt' , the server records client requests, answers, and connection information.
- **Timeout & Retry Mechanism:** The client retries up to **3 times** if the server does not respond.
- **Encryption:** All communication between the client and server is encrypted using a simple **XOR cipher**

## Requirements
- Python 3.x

## Installation
1. **Clone or Download the Repository**
   ```bash
   git clone <repository_link>
   cd <repository_folder>
   ```
2. **Ensure Python is Installed**
   ```bash
   python --version
   ```

## Running the Server and Client
### 1️⃣ Start the Server
Run the following command to start the server:
```bash
python server.py
```
The server will start and listen for client connections on **localhost:12345**.

### 2️⃣ Start the Client
In a separate terminal, run:
```bash
python client.py
```
The client will display a menu where you can select a palindrome check type.

**Encryption**

The client and server **encrypt all messages** using a basic **XOR cipher** with a fixed key (ENCRYPTION_KEY = 23).
This ensures that messages sent over the network are not in plain text.
**Decryption** occurs automatically before processing any request or response

## Usage
### Menu Options
The client provides the following menu:
```
Menu:
1. Simple Palindrome Check
2. Complex Palindrome Check
3. Exit
```
### Example Inputs & Outputs
#### ✅ **Simple Palindrome Check**
Input:
```
A man, a plan, a canal, Panama
```
Processed as: `amanaplanacanalpanama`
Output:
```
Is palindrome: True
```

#### ✅ **Complex Palindrome Check**
Input:
```
ivicc
```
Processed as: `ivicc`
Output:
```
Can form a palindrome: True
Complexity score: 2
```

#### ❌ **Invalid Input Format**
Input:
```
random text
```
Output:
```
Error: Invalid request format. Use: type|string
```

## Logging
- The server logs requests in `server_logging_info.txt`, including:
  - Client IP address
  - Check type (simple/complex)
  - Input string
  - Result (true/false + complexity score if applicable)

## Assumptions & Limitations
- **Only alphanumeric characters are considered** (spaces & punctuation are ignored).
- **Strings with multiple odd-count characters cannot be rearranged into a palindrome.**
- **Minimum swap calculation assumes arbitrary swaps are allowed.**
- **Timeout Handling:** If the server is unresponsive, the client retries up to **3 times**.
- **Encryption** is basic (XOR-based) and not suitable for secure applications.

## Submission Checklist
✔ Server and Client scripts (`server.py`, `client.py`)
✔ `server_logging_info.txt` log file
✔ README documentation (this file)
✔ Demo video showing server-client interaction

## Author
**Hamza Siddiqui**
**UCID: 30183881**
