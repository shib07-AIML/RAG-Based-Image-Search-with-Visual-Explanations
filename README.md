
# RAG-Based Semantic Image Search with CLIP and OpenAI


## How It Works

1. User types a query in the Streamlit UI.
2. The query is converted into a vector using CLIP.
3. Pinecone returns the top 5 matching image vectors.
4. For each image, a short explanation is generated using OpenAI (GPT-4o-mini).
5. The image and explanation are displayed in the UI.

---

## Pre-Request

These keys are required for:
- **OpenAI** – to generate descriptions
- **Pinecone** – to search embeddings
- **AWS** – for listening to S3 events and fetching data via SQS

## Project Structure

searchimageproject/
│
├── image_search/ 
│ ├── api.py # FastAPI backend (runs on port 8089)
│ ├── streamlit_ui.py # Streamlit frontend (runs on port 8501)
│ ├── pinecone_search.py # Search logic using CLIP + Pinecone + OpenAI
│ └── .env # Your API keys for OpenAI and Pinecone
│
├── s3_to_pinecone/
│ ├── s3_polling.py # Listens to SQS messages (triggered by S3 uploads) and starts the image insertion process
│ ├── data_insertion.py # Downloads a CSV from S3, processes each row to download images, generate embeddings, and prepare batches
│ ├── pinecone_operations.py# Responsible for upserting image vectors into Pinecone in batch
│ └── .env # AWS + Pinecone configuration for the ingestion pipeline


## Performance-Oriented Design Highlights
1.Asynchronous LLM Calls
2 Parallel processing of user request.
2.Batch Insertion into Pinecone
3.Decoupled Data Ingestion Pipeline
