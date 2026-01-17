FROM python:3.12-slim-bookworm

WORKDIR /app

# প্রয়োজনীয় সিস্টেম টুলস এবং প্রি-বিল্ট mp4decrypt ইনস্টল
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg aria2 wget unzip gcc g++ make cmake \
    && wget https://github.com/axiomatic-systems/Bento4/releases/download/v1.6.0-641/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && unzip Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && cp Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/mp4decrypt /usr/local/bin/ \
    && rm -rf Bento4-SDK* \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ডিপেন্ডেন্সি ইনস্টল
COPY itsgolubots.txt .
RUN pip install --no-cache-dir -r itsgolubots.txt

COPY . .

# মেইন ফাইল রান করা
CMD ["python3", "main.py"]
