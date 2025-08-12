# app.py
from flask import Flask, render_template, request, redirect, flash
import os
from fixed_p2p_code import discovered_peers, send_file, request_blockchain_from_host

app = Flask(__name__)
app.secret_key = 'super_secret'

@app.route('/')
def home():
    peers = list(discovered_peers.items())
    return render_template('index.html', peers=peers)

@app.route('/send', methods=['POST'])
def send():
    try:
        peer_index = int(request.form['peer_index'])
        filename = request.form['filename'].strip()

        if not filename or not os.path.exists(filename):
            flash(f"❌ File '{filename}' not found.")
            return redirect('/')

        peer_list = list(discovered_peers.items())
        if 0 <= peer_index < len(peer_list):
            ip, _ = peer_list[peer_index]
            send_file(ip, 5001, filename)
            flash(f"✅ File '{filename}' sent to {ip}")
        else:
            flash("❌ Invalid peer selected.")
    except Exception as e:
        flash(f"❌ Error: {e}")
    return redirect('/')

@app.route('/blockchain')
def blockchain():
    try:
        blockchain_data = request_blockchain_from_host()
    except Exception as e:
        flash(f"Error retrieving blockchain: {e}")
        blockchain_data = []
    return render_template('blockchain.html', chain=blockchain_data)

if __name__ == '__main__':
    app.run(debug=True)
