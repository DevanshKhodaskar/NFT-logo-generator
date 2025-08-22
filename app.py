from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import base64

# Load environment variables
load_dotenv()
app = Flask(__name__)

try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    print("🔴 Error: GOOGLE_API_KEY not found in .env file")
    exit()

# Initialize model
model = genai.GenerativeModel(model_name="gemini-2.0-flash-preview-image-generation")

generation_config = {
    "response_modalities": ["TEXT", "IMAGE"]
}

@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        event_name = data.get("event_name", "TechXperts 2025")
        event_description = data.get(
            "event_description",
            "A national-level hackathon bringing together innovators."
        )

        # Prompt
        text_input = (
            f"A futuristic, collectible NFT memento token for the event: '{event_name}'.\n\n"
            f"**Core Concept:** '{event_description}'.\n\n"
            "**Object & Form:** 2D illustrated token, futuristic emblem.\n"
            "**Style:** Futuristic, Web3, cyberpunk, neon gradients.\n"
            f"**Text:** Include '{event_name}' subtly.\n"
            "Avoid: 3D renders, photorealism, blurry, cartoonish, watermark."
        )

        response = model.generate_content(
            contents=[text_input],
            generation_config=generation_config
        )

        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                image_data = part.inline_data.data
                image = Image.open(BytesIO(image_data))

                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                return jsonify({
                    "event_name": event_name,
                    "image_base64": img_base64
                })

        return jsonify({"error": "No image data found"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Flask Gemini Image Generator is running"})
