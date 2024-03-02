FROM ultralytics/yolov5:latest-cpu
ENV BUCKET_NAME="jihadar"
ENV SQS_QUEUE_NAME="https://sqs.us-west-1.amazonaws.com/352708296901/jihad"
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN curl -L https://github.com/ultralytics/yolov5/releases/download/v6.1/yolov5s.pt -o yolov5s.pt

COPY . .

CMD ["python3", "app.py"]

