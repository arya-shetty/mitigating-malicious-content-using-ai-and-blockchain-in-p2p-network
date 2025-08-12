# P2P File Sharing with AI Malware Detection & Blockchain Logging

This project is a Python-based peer-to-peer (P2P) file sharing system featuring:
- Automatic peer discovery on the local network
- AI-powered malware detection for files before transfer
- Blockchain logging of file transfer metadata for auditability
- Web interface (Flask) for easy file sharing and blockchain viewing

## Features

- **Peer Discovery:** Peers broadcast their presence and listen for others, forming a dynamic network.
- **File Transfer:** Send files to discovered peers via the web UI or CLI.
- **Malware Detection:** Uses a trained AI model ([ai_model.pkl](ai_model.pkl)) to flag suspicious files before sending.
- **Blockchain Logging:** Metadata of each transfer is sent to a blockchain host for immutable logging.
- **Web UI:** User-friendly interface for sending files and viewing blockchain records.

## Getting Started

### 1. Install Requirements

```sh
pip install flask scikit-learn cryptography

### 2. Train the AI Model

Run the following to generate `ai_model.pkl`:

```sh
python train_model.py
```

### 3. Start the Blockchain Host

You need a blockchain server running and listening on the configured IP/port
(see `HOST_IP` and `HOST_BLOCKCHAIN_PORT` in `fixed_p2p_code2.py`).

### 4. Run the P2P Node (Web UI)

```sh
python app1.py
```

Access the web interface at:
[http://localhost:5000](http://localhost:5000)
Send files to discovered peers and view blockchain logs.

### 5. CLI Usage

You can also run `fixed_p2p_code2.py` directly for a command-line interface:

```sh
python fixed_p2p_code2.py
```

---

## 📂 File Structure

```
app1.py               # Flask web app for file sharing and blockchain viewing
fixed_p2p_code2.py    # Main P2P logic (peer discovery, file transfer, AI detection)
train_model.py        # Trains and saves the AI malware detection model
ai_model.pkl          # Saved AI model
templates/            # HTML templates for the web UI
static/styles.css     # CSS for the web UI
uploads/              # Uploaded files
malicious_log.txt     # Log of flagged malicious files
```

---

## ⚙ Configuration

* **Blockchain Host:** Set `HOST_IP` and `HOST_BLOCKCHAIN_PORT` in
  `fixed_p2p_code2.py` and `app1.py` to match your blockchain server.
* **AI Model:** Retrain using `train_model.py` if needed.

---

## 🔒 Security

* Files flagged as malicious by the AI model are **not sent** and are logged in `malicious_log.txt`.
* All file transfers are logged to the blockchain for transparency.

---

## 📜 License

This project is for **educational purposes** only.




