import os
import pinecone
import torch
import clip
import asyncio
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import Pinecone
from langchain_openai import ChatOpenAI

load_dotenv()

device = "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("imagesearch")


async def search_images(query, top_k=5):
    print("request came for search")
    with torch.no_grad():
        text_tokens = clip.tokenize([query]).to(device)
        text_embedding = model.encode_text(text_tokens)[0]
        text_embedding /= text_embedding.norm()

    results = index.query(
        vector=text_embedding.cpu().numpy().tolist(),
        top_k=top_k,
        include_metadata=True
    )
    print("pinecone search results",results)


    tasks = []
    for match in results.matches:
     image_url = match.metadata.get("url") or match.metadata.get("image_url")
     metadata = match.metadata
     tasks.append(generate_description(query, image_url, metadata))
    explanations = await asyncio.gather(*tasks)
    

    final_results = []
    for match, explanation in zip(results.matches, explanations):
        image_url = match.metadata.get("url") or match.metadata.get("image_url")
        final_results.append({
            "image_url": image_url,
            "explanation": explanation
        })
    print("Search completed")
    return final_results


async def generate_description(query, image_url, metadata):
   
    visual_info = ", ".join(f"{k}: {v}" for k, v in metadata.items())

    prompt = (
        f"You are an AI assistant tasked with explaining why an image is relevant to a user's search.\n\n"
        f"Search query: '{query}'\n"
        f"Image URL: {image_url}\n"
        f"Visual elements and metadata available: {visual_info}\n\n"
        f"Write a 30–50 word business-appropriate explanation describing the image’s key visual features and "
        f"why they match the search query. Use metadata hints. Do not hallucinate content."
    )

    try:
        llm = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.7)
        result = await llm.ainvoke(prompt)
        return result.content.strip()
    except Exception as e:
        return f"Failed to generate description: {str(e)}"

