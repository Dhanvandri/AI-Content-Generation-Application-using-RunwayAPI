import os
import sqlite3
import time
import requests
from runwayml import RunwayML

DB_PATH = r"/home/devil/Documents/python/flaskproject/app/database/content.db"
RUNWAY_API_KEY = "YOUR_API_KEY" # Enter your api key to work on

def generate_image(prompt, image_path):
    """
    Generate an image using the RunwayML HTTP API and save it locally.
    """
    endpoint = "https://api.runwayml.com/v1/models/stable-diffusion-v1-5/infer"
    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt
    }

    try:
        print("Requesting image generation from RunwayML (HTTP)...")
        response = requests.post(endpoint, headers=headers, json=payload)

        if response.status_code == 200:
            output_url = response.json()["output"][0]  
            download_file(output_url, image_path)
            print(f"Image saved to {image_path}")
            return image_path
        else:
            print(f"Image generation failed: {response.text}")
    except Exception as e:
        print(f"Error generating image: {e}")
    return None

def generate_video(prompt, video_path, image_path):
    """
    Generate a video using the RunwayML SDK based on an uploaded image.
    """
    client = RunwayML(api_key=RUNWAY_API_KEY)
    try:
        print("Uploading image for video generation...")
        uploaded_image = client.files.upload(image_path)  
        print("Requesting video generation from RunwayML...")
        task = client.image_to_video.create(
            model="gen3a_turbo",
            prompt_text=prompt,
            prompt_image=uploaded_image.url  
        )
        task_id = task.id

        while task.status not in ["SUCCEEDED", "FAILED"]:
            time.sleep(5)
            task = client.tasks.retrieve(task_id)

        if task.status == "SUCCEEDED":
            output_url = task.output['url']
            download_file(output_url, video_path)
            print(f"Video saved to {video_path}")
            return video_path
        else:
            print("Video generation failed.")
    except Exception as e:
        print(f"Error generating video: {e}")
    return None

def download_file(file_url, save_path):
    """
    Download a file from a given URL and save it locally.
    """
    try:
        print(f"Downloading file from {file_url}...")
        with requests.get(file_url, stream=True) as response:
            if response.status_code == 200:
                with open(save_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"File successfully saved: {save_path}")
            else:
                print(f"Failed to download file: {response.text}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def generate_content(user_id, prompt):
    """
    Generate images and videos using RunwayML HTTP API and SDK.
    """
    user_dir = os.path.join("generated_content", user_id)
    video_dir = os.path.join(user_dir, "videos")
    image_dir = os.path.join(user_dir, "images")
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    video_paths = []
    image_paths = []

    # Generate Image
    for i in range(1):
        image_path = os.path.join(image_dir, f"image_{i + 1}.png")
        result = generate_image(prompt, image_path)
        if result:
            image_paths.append(result)

    if image_paths:
        video_path = os.path.join(video_dir, "video_1.mp4")
        result = generate_video(prompt, video_path, image_paths[0])
        if result:
            video_paths.append(result)

    # Update database
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO content_generation 
            (user_id, prompt, video_paths, image_paths, status, generated_at) 
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (user_id, prompt, ','.join(video_paths), ','.join(image_paths), 'Completed'))
    print(f"Content generation completed for user {user_id}")
