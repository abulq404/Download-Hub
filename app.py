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

    ydl_opts = {}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ভিডিওর তথ্য বের করা (ডাউনলোড না করে)
            info = ydl.extract_info(video_url, download=False)
            
            # আমরা শুধু টাইটেল এবং ভিডিওর ডাউনলোড ইউআরএল নিচ্ছি
            video_data = {
                "title": info.get('title', 'No Title'),
                "thumbnail": info.get('thumbnail'),
                "url": info.get('url') # সরাসরি ডাউনলোড লিংক
            }
            return jsonify(video_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
