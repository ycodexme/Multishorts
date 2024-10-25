from app import app
from flask import request, jsonify, send_file
from shorts import create_shorts
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
@app.route('/')
def index():
    return "Le serveur est en cours d'exécution. Utilisez l'API pour créer des shorts."
    
@app.route('/create-shorts', methods=['POST'])
def handle_create_shorts():
    video_source = request.form.get('videoSource')
    
    if video_source == 'youtube':
        youtube_url = request.form.get('youtubeUrl')
        output_path = os.path.join(UPLOAD_FOLDER, 'output_youtube_short')
        shorts = create_shorts(youtube_url, output_path)
    elif video_source == 'local':
        if 'videoFile' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['videoFile']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            output_path = os.path.join(UPLOAD_FOLDER, 'output_local_short')
            shorts = create_shorts(file_path, output_path)
    else:
        return jsonify({'error': 'Invalid video source'}), 400

    return jsonify({'message': 'Shorts created successfully', 'shorts': shorts}), 200

@app.route('/download-short/<path:filename>')
def download_short(filename):
    return send_file(filename, as_attachment=True)