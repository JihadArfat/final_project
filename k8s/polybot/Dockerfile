FROM python:3.10

# Set environment variable
ENV TELEGRAM_APP_URL=https://polybotjihad.devops-int-college.com/

# Set the working directory in the container
WORKDIR /app

# Copy both the application files (app.py, bot.py) and requirements file
COPY app.py bot.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run on container start
CMD ["python3", "app.py"]

