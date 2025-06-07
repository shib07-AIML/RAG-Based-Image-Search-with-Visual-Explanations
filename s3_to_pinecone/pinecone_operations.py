# pinecone_operations.py
#import  src.db_storage as db
#from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from pinecone import Pinecone
#from pinecone.core.client.models import ServerlessSpec
from  langchain_openai import ChatOpenAI,OpenAIEmbeddings
#from langchain_pinecone import PineconeVectorStore
import uuid
import os
from dotenv import load_dotenv
load_dotenv()
import hashlib
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import os
from dotenv import load_dotenv
load_dotenv()


index = pc.Index("imagesearch")

def insert_image_batch_to_pinecone(batch):
    try:
        print("Inserting batch to Pinecone...")
        index.upsert(batch)
        print("Insertion successful.")
        return True
    except Exception as e:
        print("Error inserting to Pinecone:", e)
        return False
