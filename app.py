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

    # 'best' ফরম্যাট সেট করলে এটি নিজে থেকেই সেরা কোয়ালিটির লিংক আনবে
    ydl_opts = {
        'format': 'best'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # আসল ডাউনলোড লিংক খুঁজে বের করার লজিক
            video_link = info.get('url')
            if not video_link and 'formats' in info:
                video_link = info['formats'][-1].get('url')
            
            video_data = {
                "title": info.get('title', 'No Title'),
                "thumbnail": info.get('thumbnail'),
                "url": video_link
            }
            return jsonify(video_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
