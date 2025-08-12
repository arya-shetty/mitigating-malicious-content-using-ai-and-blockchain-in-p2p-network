from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import fixed_p2p_code2 as p2p
from flask import session
from datetime import datetime



app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Start networking services
import os

if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    p2p.start_services()


@app.route('/')
def index():
    return render_template('index1.html', peers=p2p.discovered_peers, log=[])

@app.route('/send', methods=['POST'])
def send():
    peer_ip = request.form['peer_ip']
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    log = []

    if p2p.is_malicious_file(filepath):
        msg = f"⚠️ File '{filename}' flagged as malicious. Not sent."
        flash(msg, 'error')
        log.append(msg)
        with open("malicious_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()}: {msg}\n")
    else:
        p2p.send_file(peer_ip, p2p.LISTEN_PORT, filepath)
        msg = f"✅ File '{filename}' sent to {peer_ip}."
        flash(msg, 'success')
        log.append(msg)

    return render_template('index.html', peers=p2p.discovered_peers, log=log)


@app.route('/blockchain')
def blockchain():
    chain = p2p.request_blockchain_from_host()
    return render_template('blockchain1.html', chain=chain)

if __name__ == '__main__':
    app.run(debug=True)
