FROM ubuntu

RUN apt update && apt install -y python3

COPY counter.py /home/counter.py

CMD ["python3", "-u", "/home/counter.py"]
