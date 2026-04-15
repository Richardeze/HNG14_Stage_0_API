from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This handles Access-Control-Allow-Origin: *

@app.route("/api/classify", methods=["GET"])
def classify_name():
    name = request.args.get("name")

    if not name:
        return jsonify({
            "status": "error",
            "message": "Missing or empty name parameter"
        }), 400

    if not isinstance(name, str):
        return jsonify({
            "status": "error",
            "message": "Name must be a string"
        }), 422

    try:
        response = requests.get(
            "https://api.genderize.io",
            params = {"name": name},
            timeout=5
        )

        if response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": "Failed to fetch data from external API"
            }), 502

        data = response.json()

    except requests.exceptions.RequestException:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch data from external API"
        }), 502

    gender = data.get("gender")
    probability = data.get("probability")
    count = data.get("count")

    if gender is None or count == 0:
        return jsonify({
            "status": "error",
            "message": "No prediction available for the following name"
        }), 422

    sample_size = count

    is_confident = (
        probability >= 0.7 and sample_size >= 100
    )

    processed_at = datetime.now(timezone.utc).isoformat()

    return jsonify({
        "status": "success",
        "data": {
            "name": name,
            "gender": gender,
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": is_confident,
            "processed_at": processed_at
        }
    }), 200

if __name__ == "__main__":
    app.run(debug=True)