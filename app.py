"""
Flask Web Application for Smart Data Importer
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import sys

sys.path.append('src')
from data_cleaner import process_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CLEANED_FOLDER'] = 'cleaned'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CLEANED_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Home page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Data Importer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input[type="file"],
            input[type="password"],
            input[type="text"] {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            button {
                background: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #45a049;
            }
            .status {
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                display: none;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧹 Smart Data Importer</h1>
            <p style="text-align: center; color: #666;">
                AI-powered data cleaning and schema mapping
            </p>
            
            <form id="uploadForm">
                <div class="form-group">
                    <label>📁 Upload CSV File</label>
                    <input type="file" id="csvFile" accept=".csv" required>
                </div>
                
                <div class="form-group">
                    <label>🔑 Gemini API Key</label>
                    <input type="password" id="apiKey" placeholder="Enter your Gemini API key" required>
                    <small style="color: #999;">Get your key from <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a></small>
                </div>
                
                <button type="submit">🚀 Clean & Standardize Data</button>
            </form>
            
            <div id="status" class="status"></div>
            
            <div id="downloadSection" style="display:none; margin-top: 20px;">
                <h3>✅ Processing Complete!</h3>
                <button onclick="downloadFile()" style="background:#2196F3;">📥 Download Cleaned CSV</button>
                <button onclick="downloadReport()" style="background:#FF9800;">📊 Download Quality Report</button>
            </div>
        </div>
        
        <script>
            let cleanedFilename = '';
            
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                formData.append('file', document.getElementById('csvFile').files[0]);
                formData.append('api_key', document.getElementById('apiKey').value);
                
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = '⏳ Processing... This may take a minute.';
                statusDiv.className = 'status';
                statusDiv.style.display = 'block';
                statusDiv.style.background = '#fff3cd';
                statusDiv.style.color = '#856404';
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        statusDiv.textContent = '✅ ' + data.message;
                        statusDiv.className = 'status success';
                        
                        cleanedFilename = data.output_file;
                        document.getElementById('downloadSection').style.display = 'block';
                    } else {
                        statusDiv.textContent = '❌ Error: ' + data.error;
                        statusDiv.className = 'status error';
                    }
                } catch (error) {
                    statusDiv.textContent = '❌ Error: ' + error.message;
                    statusDiv.className = 'status error';
                }
            });
            
            function downloadFile() {
                window.location.href = '/download/' + cleanedFilename;
            }
            
            function downloadReport() {
                window.location.href = '/download/' + cleanedFilename.replace('.csv', '_report.txt');
            }
        </script>
    </body>
    </html>
    """


@app.route('/process', methods=['POST'])
def process():
    """Process uploaded CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    api_key = request.form.get('api_key', '')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    
    if not api_key:
        return jsonify({'error': 'Gemini API key required'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Process file
        output_filename = f"cleaned_{filename}"
        output_path = os.path.join(app.config['CLEANED_FOLDER'], output_filename)
        
        process_file(input_path, output_path, api_key)
        
        return jsonify({
            'success': True,
            'message': 'Data cleaned and standardized successfully!',
            'output_file': output_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    """Download cleaned file"""
    file_path = os.path.join(app.config['CLEANED_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    print("="*80)
    print("SMART DATA IMPORTER - WEB INTERFACE")
    print("="*80)
    print("\n🚀 Starting server...")
    print("📡 Access at: http://localhost:5000")
    print("\n💡 Upload heterogeneous CSV files and get standardized output!")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
