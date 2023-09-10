FROM python:3.10.9

RUN pip install --upgrade pip


# Select working directory
WORKDIR /code

# Copy requirements.txt to working directory
COPY requirements.txt requirements.txt


# Copy source code to working directory
COPY . /code

# Create data directory
RUN mkdir -p /data/logs
# Install dependencies
RUN pip install -r requirements.txt
RUN apt-get install PortAudio -y

# Run the application
CMD ["python3", "api.py"]