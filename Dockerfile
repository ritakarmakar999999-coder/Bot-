FROM python:3.10-slim

# প্রয়োজনীয় সিস্টেম প্যাকেজ ইনস্টল
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# N_m3u8DL-RE ইনস্টল করা (DRM এর জন্য মাস্ট)
RUN curl -L https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.2.0-beta/N_m3u8DL-RE_v0.2.0-beta_linux-x64.tar.gz -o downloader.tar.gz \
    && tar -xzf downloader.tar.gz \
    && mv N_m3u8DL-RE_v0.2.0-beta_linux-x64/N_m3u8DL-RE /usr/local/bin/ \
    && chmod +x /usr/local/bin/N_m3u8DL-RE

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# আপনার মেইন ফাইল রান করার কমান্ড
CMD ["python", "nath.py"]

