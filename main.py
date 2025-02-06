from fastapi import FastAPI, HTTPException
import os
import subprocess
import json
import requests
import shutil
import sqlite3
import markdown
from bs4 import BeautifulSoup
from PIL import Image
import speech_recognition as sr

app = FastAPI()

data_dir = "/data"

def validate_path(path):
    """Ensure path is within /data and not attempting deletion."""
    if not path.startswith(data_dir):
        raise HTTPException(status_code=400, detail="Access outside /data is forbidden.")
    if "delete" in path.lower():
        raise HTTPException(status_code=400, detail="File deletion is not allowed.")

@app.post("/run")
def run_task(task: str):
    try:
        if "install uv" in task.lower() and "run datagen" in task.lower():
            subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)
            subprocess.run(["python", "datagen.py", "user@example.com"], check=True)
            return {"status": "Success"}
        
        elif "fetch data from an api" in task.lower():
            response = requests.get("https://api.example.com/data")
            with open(f"{data_dir}/api_data.json", "w") as f:
                json.dump(response.json(), f)
            return {"status": "Success"}

        elif "clone a git repo" in task.lower():
            subprocess.run(["git", "clone", "https://github.com/example/repo.git", f"{data_dir}/repo"], check=True)
            return {"status": "Success"}
        
        elif "run sql query" in task.lower():
            conn = sqlite3.connect(f"{data_dir}/database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(price) FROM tickets WHERE type='Gold'")
            result = cursor.fetchone()
            with open(f"{data_dir}/ticket-sales-gold.txt", "w") as f:
                f.write(str(result[0]))
            conn.close()
            return {"status": "Success"}
        
        elif "extract data from website" in task.lower():
            response = requests.get("https://example.com")
            soup = BeautifulSoup(response.text, "html.parser")
            with open(f"{data_dir}/scraped_data.txt", "w") as f:
                f.write(soup.get_text())
            return {"status": "Success"}
        
        elif "compress image" in task.lower():
            image = Image.open(f"{data_dir}/image.png")
            image.save(f"{data_dir}/compressed.jpg", "JPEG", quality=50)
            return {"status": "Success"}
        
        elif "transcribe audio" in task.lower():
            recognizer = sr.Recognizer()
            with sr.AudioFile(f"{data_dir}/audio.mp3") as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
            with open(f"{data_dir}/transcription.txt", "w") as f:
                f.write(text)
            return {"status": "Success"}
        
        elif "convert markdown to html" in task.lower():
            with open(f"{data_dir}/file.md", "r") as f:
                md_text = f.read()
            html_text = markdown.markdown(md_text)
            with open(f"{data_dir}/file.html", "w") as f:
                f.write(html_text)
            return {"status": "Success"}
        
        elif "filter csv file" in task.lower():
            import pandas as pd
            df = pd.read_csv(f"{data_dir}/data.csv")
            filtered_df = df[df["column"] == "value"]
            filtered_df.to_json(f"{data_dir}/filtered_data.json", orient="records")
            return {"status": "Success"}

        else:
            raise HTTPException(status_code=400, detail="Unknown task.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
def read_file(path: str):
    try:
        validate_path(path)
        with open(path, "r") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found.")
