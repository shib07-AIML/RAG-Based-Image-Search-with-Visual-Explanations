FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 8089 8501

CMD ["sh", "-c", "uvicorn image_search.api:app --host 0.0.0.0 --port 8089 & streamlit run image_search/streamlit_ui.py --server.port 8501"]
