# Use the official Python image with the latest version of Python installed
FROM python:latest

# Set the working directory in the container
WORKDIR /atsuko

# Copy the entire 'atsuko' project folder into the container at /atsuko
COPY ./atsuko /atsuko

# Copy the config.json and key.pem
COPY ./config.json /
COPY ./key.pem /

# Install Git
RUN apt-get update && \
    apt-get install -y git

# Install dependencies from both requirements.txt files
RUN pip install --no-cache-dir -r ./web/requirements.txt
RUN pip install --no-cache-dir -r ./bot/requirements.txt

# Debug for directories
RUN ls -la /atsuko

# Run main.py when the container launches
CMD ["python3", "runtime/main.py"]