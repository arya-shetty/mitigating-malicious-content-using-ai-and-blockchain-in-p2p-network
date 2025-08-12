import socket
import threading
import os
import json
import platform
import time
from datetime import datetime

import pickle

def get_local_ip():
    """Get the actual local IP address of the current machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # Connect to a public server (no data sent)
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# Load AI model
try:
    with open("ai_model.pkl", "rb") as f:
        ai_model = pickle.load(f)
except Exception as e:
    ai_model = None
    print(f"[AI] Warning: model could not be loaded - {e}")

# Map common extensions to integers for ML
EXT_MAP = {
    ".exe": 1,
    ".txt": 2,
    ".jpg": 3,
    ".zip": 4,
    ".pdf": 5
}

def extract_features(filename):
    ext = os.path.splitext(filename)[1].lower()
    extension_code = EXT_MAP.get(ext, 0)
    name_length = len(os.path.basename(filename))
    try:
        size_mb = os.path.getsize(filename) / (1024 * 1024)
    except:
        size_mb = 0
    return [name_length, size_mb, extension_code]

def is_malicious_file(filename):
    if not ai_model:
        return False  # Fail open if model is missing
    features = extract_features(filename)
    prediction = ai_model.predict([features])[0]
    return prediction == 1


LISTEN_PORT = 5001
BROADCAST_PORT = 5002
BROADCAST_INTERVAL = 5  # seconds
BROADCAST_IP = '255.255.255.255'

# IP and port of the blockchain host (replace with your host's IP)
HOST_IP = '192.168.211.76'        # <-- set your blockchain host IP here
HOST_BLOCKCHAIN_PORT = 9000    # Port host listens on for blockchain metadata & queries

PEER_NAME = platform.node() or socket.gethostname()
discovered_peers = {}

# === Receiver Thread ===
def listen_for_incoming():
    server = socket.socket()
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(5)
    print(f"[Receiver] Listening on port {LISTEN_PORT}...")

    while True:
        conn, addr = server.accept()
        print(f"[Receiver] Connected by {addr}")

        filename = conn.recv(1024).decode()
        conn.send(b'FILENAME_RECEIVED')

        received_file_path = f"received_{filename}"
        with open(received_file_path, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)

        print(f"[Receiver] File received: {received_file_path}")
        conn.close()

# === Broadcast Presence ===
def broadcast_presence():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp.settimeout(0.2)

    while True:
        msg = json.dumps({
            "name": PEER_NAME,
            "ip": get_local_ip(),
            "port": LISTEN_PORT
        }).encode()
        udp.sendto(msg, (BROADCAST_IP, BROADCAST_PORT))
        time.sleep(BROADCAST_INTERVAL)

# === Listen for Broadcasts ===
def listen_for_broadcasts():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("", BROADCAST_PORT))
    while True:
        try:
            data, addr = udp.recvfrom(1024)
            peer_info = json.loads(data.decode())
            ip = peer_info.get("ip")
            name = peer_info.get("name")
            if ip != get_local_ip():
                discovered_peers[ip] = name
        except:
            continue

# === Send metadata to blockchain host before file transfer ===
def send_metadata_to_host(filename, receiver_ip):
    metadata = {
        'sender': get_local_ip(),
        'receiver': receiver_ip,
        'filename': os.path.basename(filename),
        'timestamp': datetime.utcnow().isoformat()
    }
    try:
        s = socket.socket()
        s.connect((HOST_IP, HOST_BLOCKCHAIN_PORT))
        s.send(json.dumps({'type': 'metadata', 'data': metadata}).encode())
        print(f"[Metadata] Sent to host for file: {filename}")
        s.close()
    except Exception as e:
        print(f"[Metadata] Error sending to host: {e}")

# === Request full blockchain from host ===
def request_blockchain_from_host():
    try:
        s = socket.socket()
        s.connect((HOST_IP, HOST_BLOCKCHAIN_PORT))
        s.send(json.dumps({'type': 'get_blockchain'}).encode())
        blockchain_data = b''
        while True:
            part = s.recv(4096)
            if not part:
                break
            blockchain_data += part
        s.close()
        response = json.loads(blockchain_data.decode())
        return response.get('chain', [])
    except Exception as e:
        print(f"[Blockchain] Error requesting from host: {e}")
        return []


# === Sender ===
def send_file(target_ip, target_port, filename):
    s = None  # Initialize the socket variable for safe closure
    try:
        # ✅ Step 1: AI-based malicious file detection
        if is_malicious_file(filename):
            print(f"[AI] ❌ File '{filename}' flagged as malicious. Aborting.")
            return

        # ✅ Step 2: Send metadata to blockchain host
        send_metadata_to_host(filename, target_ip)

        # ✅ Step 3: Establish connection and send file
        s = socket.socket()
        s.connect((target_ip, target_port))

        file_basename = os.path.basename(filename)
        s.send(file_basename.encode())

        ack = s.recv(1024).decode()
        if ack != 'FILENAME_RECEIVED':
            print("[Sender] ❌ Handshake failed.")
            return

        with open(filename, 'rb') as f:
            data = f.read(1024)
            while data:
                s.send(data)
                data = f.read(1024)

        print(f"[Sender] ✅ File sent: {filename} → {target_ip}")

    except Exception as e:
        print(f"[Sender] ❌ Error: {e}")
    finally:
        if s:
            s.close()


# === Main Logic ===
def main():
    threading.Thread(target=listen_for_incoming, daemon=True).start()
    threading.Thread(target=broadcast_presence, daemon=True).start()
    threading.Thread(target=listen_for_broadcasts, daemon=True).start()

    while True:
        print("\n[Discovered Peers]")
        for idx, (ip, name) in enumerate(discovered_peers.items(), start=1):
            print(f"{idx}. {name} ({ip})")

        cmd = input("\n[COMMAND] Enter: send <#> <filename>, getchain or 'exit': ").strip()
        if cmd.lower() == 'exit':
            print("[System] Exiting...")
            break
        elif cmd.startswith("send"):
            try:
                _, index, filename = cmd.split()
                index = int(index) - 1
                ip = list(discovered_peers.keys())[index]
                send_file(ip, LISTEN_PORT, filename)
            except (ValueError, IndexError):
                print("[!] Usage: send <peer_number> <filename>")
        elif cmd.lower() == 'getchain':
            request_blockchain_from_host()
        else:
            print("[!] Unknown command.")

if __name__ == "__main__":
    main()
