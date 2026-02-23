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

    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            
            download_options = []
            seen_video_res = set()
            audio_added = False

            # ফরম্যাট লিস্ট থেকে ভিডিও এবং অডিও আলাদা করা
            for f in reversed(formats):
                url = f.get('url')
                ext = f.get('ext')
                vcodec = f.get('vcodec')
                acodec = f.get('acodec')
                height = f.get('height')

                if not url:
                    continue

                # ১. ভিডিও ফরম্যাট (MP4 এবং ভিডিও কোডেক আছে এমন)
                if ext == 'mp4' and vcodec != 'none' and vcodec is not None:
                    res_label = f"{height}p" if height else "Video (MP4)"
                    if res_label not in seen_video_res:
                        download_options.append({
                            "type": "video",
                            "quality": res_label,
                            "url": url,
                            "ext": "mp4"
                        })
                        seen_video_res.add(res_label)
                
                # ২. অডিও/MP3 ফরম্যাট (শুধুমাত্র অডিও কোডেক আছে এমন)
                if acodec != 'none' and vcodec == 'none':
                    if not audio_added: # শুধুমাত্র সেরা কোয়ালিটির একটি অডিও অপশন দেখাবে
                        download_options.append({
                            "type": "audio",
                            "quality": "Audio (MP3)",
                            "url": url,
                            "ext": "mp3"
                        })
                        audio_added = True # চাইলে এটি তুলে দিলে আরও অডিও অপশন দেখাবে

            # যদি কোনোভাবেই আলাদা অপশন না পায়, তবে ডিফল্ট লিংক দেবে
            if not download_options:
                best_url = info.get('url')
                if best_url:
                    download_options.append({"type": "video", "quality": "Best Quality", "url": best_url})

            return jsonify({
                "title": info.get('title', 'Unknown Title'),
                "thumbnail": info.get('thumbnail', ''),
                "options": download_options
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
