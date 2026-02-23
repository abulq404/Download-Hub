import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    video_url = request.form.get('url')
    if not video_url:
        return jsonify({"error": "লিংক দিতে হবে!"}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # ফেসবুকের জন্য উন্নত লিংক এক্সট্রাকশন
            video_link = info.get('url')
            if not video_link and info.get('formats'):
                for f in reversed(info.get('formats')):
                    if f.get('vcodec') != 'none' and f.get('url'):
                        video_link = f.get('url')
                        break
            
            if not video_link:
                raise Exception("ডাউনলোড লিংক পাওয়া যায়নি।")

            return jsonify({
                "title": info.get('title', 'Unknown Title'),
                "thumbnail": info.get('thumbnail', ''),
                "url": video_link
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render-এর জন্য ডাইনামিক পোর্ট সেটআপ
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
