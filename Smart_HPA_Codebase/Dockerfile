# Declare base image for this image 
# Use Python 3.11 to avoid issue with Numpy version
# error: https://stackoverflow.com/questions/77555315/i-am-unable-to-build-a-docker-image-because-of-requirements-txt-file-can-anyone
FROM python:3.11

# Working directory - the path where files will be copied and commands will be executed  
WORKDIR /usr/src/app

# Copy requirement file, the path is the current directory of this Dockerfile
COPY requirements.txt ./
# Install requirements by running Unix command
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code to the working directory
COPY . . 

# provides a command and arguments for starting a container, there's only one CMD
CMD [ "python", "./Microservice_Capacity_Analyzer.py" ]
