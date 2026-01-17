FROM python:3.10-slim-buster

# সিস্টেম টুলস ইনস্টল
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    wget \
    git \
    && apt-get clean

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# আপনার মেইন ফাইলের নাম main.py হলে এটি ঠিক আছে
CMD ["python3", "main (1).py"] 
