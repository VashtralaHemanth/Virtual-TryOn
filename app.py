from flask import Flask, request, jsonify, render_template
import requests
import base64
import os

app = Flask(__name__)

# Load API key from environment variable or hardcode for testing (not recommended for production)
API_KEY = "SG_780c9ce77c7158bb"
API_URL = "https://api.segmind.com/v1/try-on-diffusion"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process_outfit():
    if 'model_image' not in request.files or 'cloth_image' not in request.files:
        return jsonify({"error": "No images provided"}), 400

    model_image = request.files['model_image']
    cloth_image = request.files['cloth_image']

    # Convert images to base64
    model_image_base64 = base64.b64encode(model_image.read()).decode('utf-8')
    cloth_image_base64 = base64.b64encode(cloth_image.read()).decode('utf-8')

    # Prepare request payload
    data = {
        "model_image": model_image_base64,
        "cloth_image": cloth_image_base64,
        "category": "Upper body",
        "num_inference_steps": 35,
        "guidance_scale": 2,
        "seed": 12467,
        "base64": True
    }

    headers = {'x-api-key': API_KEY}
    response = requests.post(API_URL, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        image_base64 = result.get("image", "")
        if image_base64:
            output_path = os.path.join('static', "generated_tryon.png")
            save_base64_image(image_base64, output_path)
            print(f"Image saved at: {output_path}")  # Debugging statement
            return jsonify({"image_url": '/static/generated_tryon.png'})  # Return the image URL as JSON
        else:
            print("No image data received from API")  # Debugging statement
            return jsonify({"error": "No image data received from API"}), 500
    else:
        print(f"API Error: {response.status_code}, {response.text}")  # Debugging statement
        return jsonify({"error": "API Error", "status_code": response.status_code}), response.status_code

def save_base64_image(base64_string, output_path):
    image_data = base64.b64decode(base64_string)
    with open(output_path, 'wb') as f:
        f.write(image_data)

@app.route('/result')
def result():
    image_url = request.args.get('image_url')
    if image_url is None:
        return "No image URL provided", 400  # Handle the case where no image URL is passed
    print(f"Redirecting to result page with image URL: {image_url}")  # Debugging statement
    return render_template('result.html', image_url=image_url)

if __name__ == '__main__':
    app.run(debug=True)