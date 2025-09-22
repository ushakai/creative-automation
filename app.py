from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from config import Config
from campaign_processor import CampaignProcessor

app = Flask(__name__)
app.config.from_object(Config)

# Initialize campaign processor
campaign_processor = CampaignProcessor()


@app.route("/")
def index():
    """Main page with upload form"""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_brief():
    """Handle campaign brief upload and processing"""
    try:
        # Get JSON data from form
        brief_data = request.get_json()

        if not brief_data:
            return jsonify({"error": "No campaign brief provided"}), 400

        # Validate required fields
        required_fields = [
            "product_name",
            "target_region",
            "target_audience",
            "campaign_message",
        ]
        for field in required_fields:
            if field not in brief_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Save campaign brief
        brief_filename = f"brief_{brief_data['product_name'].replace(' ', '_')}.json"
        brief_path = os.path.join(app.config["UPLOAD_FOLDER"], brief_filename)

        with open(brief_path, "w") as f:
            json.dump(brief_data, f, indent=2)

        # Process the campaign
        result = campaign_processor.process_campaign(brief_data)

        if "error" in result:
            return jsonify({"error": result["error"]}), 500

        return jsonify(
            {
                "success": True,
                "message": "Campaign processed successfully",
                "result": result,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results/<product_name>")
def show_results(product_name):
    """Display generated assets for a product"""
    return render_template("results.html", product_name=product_name)


@app.route("/assets/<product_name>/<ratio>/<filename>")
def serve_asset(product_name, ratio, filename):
    """Serve generated asset files"""
    try:
        file_path = os.path.join(Config.OUTPUTS_FOLDER, product_name, ratio, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return "Asset not found", 404
    except Exception as e:
        return f"Error serving asset: {str(e)}", 500


@app.route("/api/assets/<product_name>")
def get_assets_info(product_name):
    """Get information about generated assets for a product"""
    try:
        assets = []
        product_dir = os.path.join(Config.OUTPUTS_FOLDER, product_name)

        if os.path.exists(product_dir):
            for ratio in Config.ASPECT_RATIOS.keys():
                ratio_dir = os.path.join(product_dir, ratio)
                if os.path.exists(ratio_dir):
                    for filename in os.listdir(ratio_dir):
                        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                            assets.append(
                                {
                                    "ratio": ratio,
                                    "filename": filename,
                                    "url": f"/assets/{product_name}/{ratio}/{filename}",
                                    "dimensions": f"{Config.ASPECT_RATIOS[ratio][0]}x{Config.ASPECT_RATIOS[ratio][1]}",
                                }
                            )

        return jsonify({"assets": assets})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Create required directories
    for folder in [
        app.config["UPLOAD_FOLDER"],
        Config.ASSETS_FOLDER,
        Config.OUTPUTS_FOLDER,
    ]:
        os.makedirs(folder, exist_ok=True)

    app.run(debug=True)
