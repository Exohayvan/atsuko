# Use the official Python image with the latest version of Python installed
FROM python:latest

# Set the working directory in the container
WORKDIR /atsuko

# Copy the entire 'atsuko' project folder into the container at /atsuko
COPY . /atsuko

# Install dependencies from both requirements.txt files
RUN pip install --no-cache-dir -r /atsuko/web/requirements.txt
RUN pip install --no-cache-dir -r /atsuko/bot/requirements.txt

# Run main.py when the container launches
CMD ["python3", "/atsuko/runtime/main.py"]