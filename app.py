from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

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
            "**Object & Form:** A distinct 2D illustrated token, symbolic coin, crystal, holographic card, or futuristic emblem.\n"
            "**Style:** Futuristic, Web3, cyberpunk, neon gradients, vector-style, flat geometric.\n"
            "**Background:** Minimalist dark abstract background.\n"
            f"**Text:** Include '{event_name}' subtly.\n"
            "Avoid: 3D renders, photorealism, blurry, cartoonish, watermark."
        )

        # Generate response
        response = model.generate_content(
            contents=[text_input],
            generation_config=generation_config
        )

        # Extract image
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                image_data = part.inline_data.data
                image = Image.open(BytesIO(image_data))

                # Keep everything in memory
                img_io = BytesIO()
                image.save(img_io, format="PNG")
                img_io.seek(0)

                return send_file(img_io, mimetype="image/png")

        return jsonify({"error": "No image data found in response."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Flask Gemini Image Generator is running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
