FROM nvidia/cuda:12.2.2-base-ubuntu22.04

# Set frontend to noninteractive to avoid prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for adding PPAs and then Python itself
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Make python3.12 the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Install pip using the new python version
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Set the working directory in the container
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install PyTorch with CUDA support to ensure GPU acceleration for embedding models
# This version is compatible with the CUDA version in the base image.
RUN python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the application source code and documentation
COPY src/ ./src/
COPY docs/ ./docs/

# Expose the port the app runs on
EXPOSE 7860

# Define the default command to run the application
CMD ["python3", "src/app.py"]