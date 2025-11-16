# Use an offical python image as the base image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the contents of the current directory to /app in the container
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip
# install any needed packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pandas
RUN pip install pygal
RUN pip install requests
RUN pip install datetime

# set the defulat command to run when starting the container
CMD ["python", "main.py"]