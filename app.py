from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, session
import os
import hashlib
import uuid

# Directory to store uploaded files
data_dir = "evidence_files"
os.makedirs(data_dir, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

# Home page route (hhh.html)
@app.route('/')
def home():
    return render_template('hhh.html')

# Login page route (login.html)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        investigator_id = request.form.get('investigator-id')
        password = request.form.get('password')

        # For simplicity, print the login info. In a real app, you'd validate it.
        print(f"Investigator ID: {investigator_id}")
        print(f"Password: {password}")

        # Store investigator_id in session
        session['investigator_id'] = investigator_id

        return redirect(url_for('index'))  # Redirect to the main page after login

    return render_template('login.html')

# Main page route (index.html)
@app.route('/index')
def index():
    if 'investigator_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('index.html')

# Collect evidence route
@app.route('/collect', methods=['POST'])
def collect_evidence():
    if 'evidence-file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['evidence-file']
    file_id = str(uuid.uuid4())
    file_path = os.path.join(data_dir, file_id + "_" + file.filename)
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully", "file_id": file_id, "filename": file.filename}), 200

# Preserve evidence route
@app.route('/preserve', methods=['POST'])
def preserve_evidence():
    data = request.get_json()
    if not data or 'file_id' not in data or 'algorithm' not in data:
        return jsonify({"error": "Invalid input"}), 400

    file_id = data['file_id']
    algorithm = data['algorithm']
    files = [f for f in os.listdir(data_dir) if f.startswith(file_id)]

    if not files:
        return jsonify({"error": "File not found"}), 404

    file_path = os.path.join(data_dir, files[0])
    hash_function = getattr(hashlib, algorithm, None)

    if not hash_function:
        return jsonify({"error": "Unsupported hashing algorithm"}), 400

    with open(file_path, 'rb') as f:
        file_hash = hash_function(f.read()).hexdigest()

    return jsonify({"file_id": file_id, "hash": file_hash, "algorithm": algorithm}), 200

# Analyze evidence route
@app.route('/analyze', methods=['POST'])
def analyze_evidence():
    data = request.get_json()
    if not data or 'file_id' not in data or 'analysis_type' not in data:
        return jsonify({"error": "Invalid input"}), 400

    file_id = data['file_id']
    analysis_type = data['analysis_type']
    files = [f for f in os.listdir(data_dir) if f.startswith(file_id)]

    if not files:
        return jsonify({"error": "File not found"}), 404

    file_path = os.path.join(data_dir, files[0])
    analysis_result = ""

    if analysis_type == "file":
        analysis_result = os.stat(file_path)
    elif analysis_type == "logs":
        with open(file_path, 'r') as f:
            analysis_result = f.readlines()
    else:
        return jsonify({"error": "Unsupported analysis type"}), 400

    return jsonify({"file_id": file_id, "analysis_type": analysis_type, "result": str(analysis_result)}), 200

# Generate report route
@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.get_json()
    if not data or 'file_id' not in data or 'format' not in data:
        return jsonify({"error": "Invalid input"}), 400

    file_id = data['file_id']
    report_format = data['format']

    # Mocked report generation for demonstration purposes
    report_content = f"Report for file_id: {file_id}\nGenerated in format: {report_format}\n\n[Analysis Results Here]"
    report_filename = f"report_{file_id}.{report_format}"
    report_path = os.path.join(data_dir, report_filename)

    with open(report_path, 'w') as f:
        f.write(report_content)

    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
