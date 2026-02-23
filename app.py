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
            seen_resolutions = set()

            # ফরম্যাট লিস্ট থেকে MP4 এবং নির্দিষ্ট রেজোলিউশন ফিল্টার করা
            for f in reversed(formats):
                res = f.get('height')
                ext = f.get('ext')
                url = f.get('url')
                
                # শুধুমাত্র ভিডিওসহ (vcodec != none) এবং MP4 ফরম্যাটগুলো নেবে
                if url and res and ext == 'mp4' and f.get('vcodec') != 'none':
                    res_label = f"{res}p"
                    if res_label not in seen_resolutions:
                        download_options.append({
                            "quality": res_label,
                            "url": url,
                            "ext": ext
                        })
                        seen_resolutions.add(res_label)

            # যদি কোনো রেজোলিউশন না পায়, তবে ডিফল্ট বেস্ট লিংকটি দেবে
            if not download_options:
                best_url = info.get('url') or (formats[-1].get('url') if formats else None)
                if best_url:
                    download_options.append({"quality": "Default (Best)", "url": best_url, "ext": "mp4"})

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
