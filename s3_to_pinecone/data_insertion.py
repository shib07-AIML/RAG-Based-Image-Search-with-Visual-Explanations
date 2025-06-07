# data_insertion.py

import torch
import clip
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from pinecone_operations import insert_image_batch_to_pinecone

# Init CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def download_and_embed_image(idx, url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            img_input = preprocess(img).unsqueeze(0).to(device)

            with torch.no_grad():
                embedding = model.encode_image(img_input)
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
                return {
                    "id": f"image_{idx}",
                    "values": embedding.cpu().numpy().tolist()[0],
                    "metadata": {"url": url}
                }
    except Exception as e:
        print(f"Error processing image {idx}: {e}")
    return None

def insert_vectordatabase(file_obj):
    print("now download the files in batches and then inserting into pinecone")
    df = pd.read_csv(file_obj)
    total = 50 #len(df)

    for start in range(0, total, 2):
        end = min(start + 2, total)
        batch_df = df.iloc[start:end]
        batch = []

        for idx, row in batch_df.iterrows():
            image_url = row['photo_image_url']
            image_data = download_and_embed_image(idx, image_url)
            if image_data:
                batch.append(image_data)

        if batch:
            insert_image_batch_to_pinecone(batch)
