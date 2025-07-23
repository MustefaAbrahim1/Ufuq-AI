import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from pytrends.request import TrendReq
import traceback

# Load .env API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Gemini Config
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

# PyTrends (real-time)
pytrends = TrendReq(hl="en-US", tz=360)

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# ========== Function: Get Related Trending Keywords ==========
def get_trending_keywords(niche):
    try:
        trending_searches = pytrends.trending_searches(pn='united_states')
        trends = trending_searches[0].tolist()
        filtered = [t for t in trends if niche.lower() in t.lower()]
        return filtered[:10]
    except Exception as e:
        print("Trend Error:", e)
        return []

# ========== Function: Generate Content Ideas ==========
def generate_ideas(niche, audience, past_topics, platform, language):
    trends = get_trending_keywords(niche)
    trend_text = ", ".join(trends) if trends else "None"

    prompt = f"""
You're a multilingual expert AI assistant specialized in generating social media content ideas for creators using the {platform} platform in the {language} language.

Niche: {niche}  
Target Audience: {audience}  
Preferred Platform: {platform}  
Past Topics: {past_topics or "N/A"}  
Trending Keywords to include: {trend_text}

🎯 Generate 2 to 3 creative and engaging content ideas **strictly in this format and nothing else**:

1. [Title]  
   Description: [2 – 3 lines]  
   Hashtags: #[hashtag1] #[hashtag2] #[hashtag3]

❌ Do not include any explanations, introductions (like "Sure!" or "Here are some ideas"), or closing statements.  
✅ Only return the ideas in the exact format above — no extra text before or after.

Make the ideas fresh, relevant to current trends, optimized for {platform}, and highly engaging for the target audience.
"""


    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini Error:", traceback.format_exc())
        return "⚠️ Failed to generate content. Try again later."


# ========== Route: /generate ==========
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        niche = data.get("niche", "").strip()
        audience = data.get("audience", "").strip()
        past_topics = data.get("topics", "").strip()
        platform = data.get("platform", "").strip()
        language = data.get("language", "").strip()

        if not niche or not audience or not platform:
            return jsonify({"error": "Missing required fields."}), 400

        result = generate_ideas(niche, audience, past_topics, platform, language)
        return jsonify({"ideas": result})

    except Exception as e:
        print("Request Error:", traceback.format_exc())
        return jsonify({"error": "Internal server error."}), 500


# ========== Start Flask ==========
if __name__ == "__main__":
    app.run(debug=True)
