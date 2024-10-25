import os
import re
import logging
import json
import shutil
import warnings
import ast
import numpy as np
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip
from mistralai import Mistral
import yt_dlp
import whisper

# Chargement des variables d'environnement
load_dotenv()

# Configuration de logging
logging.basicConfig(level=logging.DEBUG)

def initialize_client():
    api_key = os.getenv("MISTRAL_API_KEY")
    return Mistral(api_key=api_key)

def is_youtube_link(input_string):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
    return re.match(youtube_regex, input_string) is not None

def download_youtube_video(url, output_path):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(output_path, 'temp_video.%(ext)s'),
            'verbose': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        logging.exception("Erreur lors du téléchargement de la vidéo YouTube")
        return None

def extract_transcript(video_path):
    transcript_file = video_path + '.transcript.json'
    if os.path.exists(transcript_file):
        with open(transcript_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    model = whisper.load_model("base", device="cpu")
    result = model.transcribe(video_path, fp16=False)

    with open(transcript_file, 'w', encoding='utf-8') as f:
        json.dump(result["segments"], f, ensure_ascii=False, indent=2)

    return result["segments"]

def create_shorts(input_path, output_path, target_width=1080, target_height=1920, num_shorts=4):
    client = initialize_client()
    is_youtube = is_youtube_link(input_path)

    try:
        if is_youtube:
            temp_video_path = download_youtube_video(input_path, output_path)
            if temp_video_path is None:
                return []

            input_path = temp_video_path

        clip = VideoFileClip(input_path)
        transcript = extract_transcript(input_path)

        segments = [{"start": 0, "end": clip.duration}]  # Remplacez par votre logique d'analyse des segments

        created_shorts = []
        for i, segment in enumerate(segments):
            subclip = clip.subclip(segment['start'], segment['end'])
            output_file = os.path.join(output_path, f"short_{i+1}.mp4")
            subclip.write_videofile(output_file, codec="libx264", audio_codec="aac")
            created_shorts.append(output_file)

        return created_shorts
    except Exception as e:
        logging.exception(f"Erreur lors du traitement de la vidéo : {e}")
        return []
    finally:
        clip.close()

if __name__ == "__main__":
    # Pour les tests locaux, vous pouvez ajouter une logique ici si nécessaire
    pass