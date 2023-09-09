FROM python:3.11.2-buster

RUN pip install --upgrade pip
RUN 

# Select working directory
WORKDIR /code

# Copy requirements.txt to working directory
COPY requirements.txt requirements.txt


# Install dependencies
RUN pip install -r requirements.txt

# Copy source code to working directory
COPY . /code
RUN chmodx a+x /code/run.sh

# Create data directory
RUN mkdir -p /data/logs

# Run the application
CMD ["./code/run.sh"]