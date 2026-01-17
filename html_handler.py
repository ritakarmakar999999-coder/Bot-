import os
import requests
import subprocess
from vars import CREDIT, BOT_USERNAME  # vars.py থেকে তথ্য নেওয়া হয়েছে
from pyrogram import Client, filters
from pyrogram.types import Message

# ==================================================================================================================================

# টেক্সট ফাইল থেকে নাম এবং URL বের করার ফাংশন
def extract_names_and_urls(file_content):
    lines = file_content.strip().split("\n")
    data = []
    for line in lines:
        if ":" in line:
            name, url = line.split(":", 1)
            data.append((name.strip(), url.strip()))
    return data

# ==================================================================================================================================

# URL গুলোকে ভিডিও, পিডিএফ এবং অন্যান্য ক্যাটাগরিতে ভাগ করার ফাংশন
def categorize_urls(urls):
    videos = []
    pdfs = []
    others = []

    for name, url in urls:
        new_url = url
        # বিভিন্ন স্ট্রিমিং সাইটের জন্য প্লেয়ার লিঙ্ক সেটআপ
        if "akamaized.net/" in url or "1942403233.rsc.cdn77.org/" in url:
            new_url = f"https://www.khanglobalstudies.com/player?src={url}"
            videos.append((name, new_url))

        elif "d1d34p8vz63oiq.cloudfront.net/" in url:
            # এখানে আপনার টোকেন প্রয়োজন হতে পারে
            new_url = f"https://anonymouspwplayer-0e5a3f512dec.herokuapp.com/pw?url={url}"
            videos.append((name, new_url))
                    
        elif "youtube.com/embed" in url:
            yt_id = url.split("/")[-1]
            new_url = f"https://www.youtube.com/watch?v={yt_id}"
            videos.append((name, new_url))

        elif ".m3u8" in url or ".mp4" in url:
            videos.append((name, url))
        elif "pdf" in url:
            pdfs.append((name, url))
        else:
            others.append((name, url))

    return videos, pdfs, others

# =================================================================================================================================

# HTML ফাইল জেনারেট করার ফাংশন (আপনার ব্র্যান্ডিং সহ)
def generate_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)[0]
    display_bot = "@MyMyMyMyisnothingbhaibot"

    video_links = "".join(f'<a href="#" onclick="playVideo(\'{url}\')">🎬 {name}</a>' for name, url in videos)
    pdf_links = "".join(f'<a href="{url}" target="_blank">📄 {name}</a>' for name, url in pdfs)
    other_links = "".join(f'<a href="{url}" target="_blank">🌐 {name}</a>' for name, url in others)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_name_without_extension} - {display_bot}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px; }}
        body {{ background: #0f0f0f; color: #fff; line-height: 1.4; }}
        header {{ background: linear-gradient(90deg, #ff3366, #ff00cc); color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; border-bottom: 2px solid #333; }}
        header p {{ font-size: 12px; color: #eee; margin-top: 5px; }}
        #video-player {{ margin: 20px auto; width: 95%; max-width: 800px; border: 2px solid #333; border-radius: 10px; overflow: hidden; }}
        .search-bar {{ margin: 15px auto; width: 95%; max-width: 500px; }}
        .search-bar input {{ width: 100%; padding: 10px; border: 2px solid #ff3366; background: #222; color: #fff; border-radius: 8px; outline: none; }}
        .container {{ display: flex; justify-content: center; gap: 10px; margin: 15px auto; width: 95%; max-width: 700px; }}
        .tab {{ flex: 1; padding: 12px; background: #222; cursor: pointer; border-radius: 8px; text-align: center; transition: 0.3s; border: 1px solid #333; }}
        .tab:hover {{ background: #ff3366; }}
        .content {{ display: none; margin: 15px auto; width: 95%; max-width: 700px; background: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }}
        .content h2 {{ font-size: 16px; margin-bottom: 15px; color: #ff3366; text-transform: uppercase; }}
        .video-list a, .pdf-list a, .other-list a {{ display: block; padding: 10px; margin: 5px 0; background: #262626; border-radius: 6px; text-decoration: none; color: #ddd; transition: 0.2s; }}
        .video-list a:hover {{ background: #ff3366; color: white; padding-left: 15px; }}
        footer {{ margin-top: 30px; padding: 20px; background: #000; color: #888; text-align: center; border-top: 1px solid #333; }}
        footer b {{ color: #ff3366; }}
    </style>
</head>
<body>
    <header>
        📚 {file_name_without_extension}
        <p>📊 {len(videos)} Videos • {len(pdfs)} PDFs • {len(others)} Others</p>
    </header>

    <div id="video-player">
        <video id="bot-player" class="video-js vjs-default-skin vjs-big-play-centered" controls preload="auto" width="640" height="360"></video>
    </div>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search lessons, PDFs or notes..." oninput="filterContent()">
    </div>

    <div class="container">
        <div class="tab" onclick="showContent('videos')"><i class="fas fa-play"></i> Videos</div>
        <div class="tab" onclick="showContent('pdfs')"><i class="fas fa-file-pdf"></i> PDFs</div>
        <div class="tab" onclick="showContent('others')"><i class="fas fa-link"></i> Others</div>
    </div>

    <div id="videos" class="content">
        <h2>🎬 Video Lectures</h2>
        <div class="video-list">{video_links}</div>
    </div>

    <div id="pdfs" class="content">
        <h2>📄 PDF Notes</h2>
        <div class="pdf-list">{pdf_links}</div>
    </div>

    <div id="others" class="content">
        <h2>🔗 External Resources</h2>
        <div class="other-list">{other_links}</div>
    </div>

    <footer>
        <p>Powered By <b>{display_bot}</b></p>
        <p>© 2026 Private Educational Engine</p>
    </footer>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script>
        const player = videojs('bot-player', {{
            controls: true, autoplay: false, preload: 'auto', fluid: true
        }});
        function playVideo(url) {{
            if (url.includes('.m3u8')) {{
                player.src({{ src: url, type: 'application/x-mpegURL' }});
                player.play().catch(() => window.open(url, '_blank'));
            }} else {{
                window.open(url, '_blank');
            }}
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        function showContent(tabName) {{
            document.querySelectorAll('.content').forEach(c => c.style.display = 'none');
            document.getElementById(tabName).style.display = 'block';
            filterContent();
        }}
        function filterContent() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const categories = ['videos','pdfs','others'];
            categories.forEach(cat => {{
                const items = document.querySelectorAll(`#${{cat}} .${{cat}}-list a`);
                let hasMatch = false;
                items.forEach(item => {{
                    if (item.textContent.toLowerCase().includes(searchTerm)) {{
                        item.style.display = 'block'; hasMatch = true;
                    }} else item.style.display = 'none';
                }});
            }});
        }}
        document.addEventListener('DOMContentLoaded', () => showContent('videos'));
    </script>
</body>
</html>
    """
    return html_template

# ==================================================================================================================================

async def html_handler(bot: Client, message: Message):
    editable = await message.reply_text("<b>👋 স্বাগতম!</b>\n\nলিঙ্ক সম্বলিত <code>.txt</code> ফাইলটি এখানে আপলোড করুন।")
    
    # ইউজার থেকে ফাইল নেওয়ার জন্য অপেক্ষা
    input: Message = await bot.listen(editable.chat.id)
    
    if input.document and input.document.file_name.endswith('.txt'):
        file_path = await input.download()
        file_name, ext = os.path.splitext(os.path.basename(file_path))
        b_name = file_name.replace('_', ' ')
    else:
        await message.reply_text("<b>❌ এরর:</b> শুধুমাত্র <code>.txt</code> ফাইল আপলোড করুন।")
        return
           
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    # ডাটা প্রসেসিং
    urls = extract_names_and_urls(file_content)
    videos, pdfs, others = categorize_urls(urls)

    # HTML জেনারেট করা
    html_content = generate_html(file_name, videos, pdfs, others)
    html_file_path = file_path.replace(".txt", ".html")
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # ফাইলটি ইউজারকে পাঠানো
    await message.reply_document(
        document=html_file_path, 
        caption=f"🌐 <b>𝐇𝐓𝐌𝐋 𝐅𝐢𝐥𝐞 𝐂𝐫𝐞𝐚𝐭𝐞𝐝!</b>\n\n📌 ফাইল: <code>{b_name}</code>\n🌟 ক্রেডিট: {BOT_USERNAME}"
    )
    
    # টেম্পোরারি ফাইল ডিলিট করা
    if os.path.exists(file_path): os.remove(file_path)
    if os.path.exists(html_file_path): os.remove(html_file_path)
