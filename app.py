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

    # কোনো নির্দিষ্ট ফরম্যাট ফোর্স না করে ডিফল্ট রাখা হলো যেন ক্র্যাশ না করে
    ydl_opts = {} 
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # ফেসবুক অনেক সময় ভিডিওগুলোকে 'entries' বা প্লেলিস্ট হিসেবে পাঠায়
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]
            
            video_link = info.get('url')
            
            # যদি সরাসরি লিংক না থাকে, তবে নিরাপদে 'formats' থেকে লিংক খোঁজা
            if not video_link and info.get('formats'):
                formats = info.get('formats')
                for f in reversed(formats): # উল্টো দিক থেকে খুঁজবে যেন ভালো কোয়ালিটি পাওয়া যায়
                    if f.get('url') and 'm3u8' not in f.get('url'):
                        video_link = f.get('url')
                        break
                
                # যদি উপরের নিয়মেও না পায়, তবে একেবারে শেষের লিংকটি নিয়ে নেবে
                if not video_link and len(formats) > 0:
                    video_link = formats[-1].get('url')
            
            # যদি কোনোভাবেই লিংক না পায়
            if not video_link:
                raise Exception("ভিডিওর মূল ফাইলটি সার্ভার থেকে পাওয়া যায়নি।")

            video_data = {
                "title": info.get('title', 'Unknown Title'),
                "thumbnail": info.get('thumbnail'),
                "url": video_link
            }
            return jsonify(video_data)
            
    except Exception as e:
        return jsonify({"error": "সার্ভার এরর: " + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
