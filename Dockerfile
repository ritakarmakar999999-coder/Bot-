FROM python:3.10-slim-bullseye

# ১. সিস্টেম প্যাকেজ ইনস্টল
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    wget \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ২. ডিরেক্টরি সেটআপ
WORKDIR /app

# ৩. ফাইল কপি করা
COPY . .

# ৪. পাইথন লাইব্রেরি ইনস্টল
RUN pip install --no-cache-dir -r requirements.txt

# ৫. বট স্টার্ট (আপনার ফাইলের নাম অনুযায়ী)
CMD ["python3", "main (1).py"]
