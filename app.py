from flask import Flask
import os
from vars import BOT_USERNAME  # vars.py থেকে বটের নাম নিয়ে আসবে

app = Flask(__name__)

@app.route('/')
def home():
    # এখানে আপনার বটের ইউজারনেম ব্যবহার করা হয়েছে
    display_name = "@MyMyMyMyisnothingbhaibot"
    return f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_name} - Authorized Access</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #050505, #111111);
            color: #fff;
            font-family: 'Courier New', monospace;
            text-align: center;
            padding-top: 50px;
        }}
        .ascii-art {{
            font-size: 12px;
            color: #00ffcc;
            text-shadow: 0 0 10px #00ffcc;
            transition: transform 0.3s ease;
        }}
        .bot-title {{
            font-size: 35px;
            font-weight: bold;
            color: #ff3366;
            margin-top: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        .status-badge {{
            background-color: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
        }}
        footer {{
            margin-top: 100px;
            padding: 30px;
            background: #000;
            border-top: 1px solid #333;
        }}
        .owner-credit {{
            color: #888;
            font-size: 13px;
        }}
    </style>
</head>

<body>
    <div class="container">
        <pre class="ascii-art">
  __  __         __  __         __  __         ____   ____  _______ 
 |  \/  |       |  \/  |       |  \/  |       |  _ \ / __ \|__   __|
 | \  / |_   _  | \  / |_   _  | \  / |_   _  | |_) | |  | |  | |   
 | |\/| | | | | | |\/| | | | | | |\/| | | | | |  _ <| |  | |  | |   
 | |  | | |_| | | |  | | |_| | | |  | | |_| | | |_) | |__| |  | |   
 |_|  |_|\__, | |_|  |_|\__, | |_|  |_|\__, | |____/ \____/   |_|   
          __/ |          __/ |          __/ |                       
         |___/          |___/          |___/                        
        </pre>

        <h1 class="bot-title">{display_name}</h1>
        <div class="mt-3">
            <span class="status-badge">System Online</span>
        </div>
        <p class="mt-4">Authorized Link Downloader Bot Engine v2.0.0</p>
    </div>

    <footer>
        <center>
            <div class="owner-credit">
                <p>© 2026 <b>@MyMyMyMyisnothingbhaibot</b> | All Rights Reserved.</p>
                <p>Powered by Your Private Server</p>
            </div>
        </center>
    </footer>
</body>
</html>
"""

if __name__ == "__main__":
    # Render-এর জন্য সঠিক পোর্ট ব্যবহার করা হয়েছে
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
