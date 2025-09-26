# Meme-Generating Proxy Server

## Overview

This project implements a **Meme-Generating Proxy Server** that intercepts **HTTP** requests (not HTTPS) and modifies responses by replacing some images with random memes from a predefined folder. Additionally, it includes a fun **Easter Egg feature** where visiting `http://google.ca` displays a surprise meme.

## Features

- **Proxy Server:** Listens on `127.0.0.1:8080` and forwards HTTP requests.
- **Meme Injection:** Replaces 50% of image requests (`.jpg`, `.png`, `.gif`) with memes from a specified folder ('Memes' folder).
- **Custom Easter Egg:** Redirects requests to `http://google.ca` to a special page displaying a meme.
- **Error Handling:** Manages unsupported requests (e.g., HTTPS) and missing resources gracefully. Enables HTTPS websites to load without crashing or any issues on the proxy server.
- **Multi-Client Support:** Uses threading to handle multiple clients simultaneously.

## Prerequisites

Ensure you have the following installed:

- **Python 3.x**

## Setup Instructions

### 1. Clone the Repository

```sh
 git clone <repository_url>
 cd Meme-Generating-Proxy
```

### 2. Place Memes in the Folder

- Create a folder containing **at least 15 memes**.
- Update the path to your meme folder in `server.py`:

```python
MEME_FOLDER = "C:\CPSC 441\Assignment 2\Memes"
```

### 3. Run the Proxy Server

Execute the following command in the terminal:

```sh
python server.py
```

The proxy server will start and listen on **127.0.0.1:8080**.

### 4. Configure Firefox to Use the Proxy

1. Open Firefox.
2. Navigate to `Settings > Network Settings`.
3. Select `Manual Proxy Configuration`.
4. Set **HTTP Proxy** to `127.0.0.1` and **Port** to `8080`.
5. Check **"Use this proxy server for all protocols"**.
6. Click **OK** to save settings.

### 5. Run the Client (Optional for Testing)

To test the proxy manually, run the client script:

```sh
python client.py
```

The client will request an image from `http://httpbin.org/image/png` and display the modified response.

## Testing the Proxy

### 1. Check Meme Injection

- Visit `http://httpbin.org/` via Firefox.
- Verify that **50% of images** are replaced with memes.

### 2. Easter Egg Test

- Visit `http://google.ca`.
- The page should display a **full-screen meme** with a fun message.

### 3. Error Handling

- Try accessing an HTTPS website, e.g., `https://www.google.ca`.
- The proxy should return loading HTTPS websites without crashing when a proxy server is running.

## File Structure

```
├── server.py       # Proxy server implementation
├── client.py       # Client to test proxy behavior
├── README.md       # Setup instructions
├── Memes/          # Folder containing at least 15 meme images
```

## Notes

- The proxy **does not support HTTPS** due to encryption, and so then it will load the HTTPS website, but will not replace image https requests to be replaced by meme images.
- If the meme folder is empty, images will not be replaced.
- Make sure to **test on Firefox**, as some browsers enforce stricter network settings.

---

**Author: Hamza Siddiqui**

**UCID: 30183881**
