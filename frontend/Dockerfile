# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
ENV PORT=8501
EXPOSE 8501

# Run Streamlit
CMD streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
