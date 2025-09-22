import os
from image_processor import ImageProcessor
from config import Config


class CampaignProcessor:
    def __init__(self):
        self.image_processor = ImageProcessor()

    def process_campaign(self, brief_data):
        """Main campaign processing logic"""
        try:
            product_name = brief_data["product_name"]
            campaign_message = brief_data["campaign_message"]
            target_audience = brief_data["target_audience"]

            # Create product output directory
            product_output_dir = os.path.join(Config.OUTPUTS_FOLDER, product_name)
            os.makedirs(product_output_dir, exist_ok=True)

            # Get or generate base image
            base_image_path = self._get_or_generate_image(product_name, target_audience)

            if not base_image_path:
                return {"error": "Failed to generate base image"}

            # Generate assets for all aspect ratios
            generated_assets = []

            for ratio_name in Config.ASPECT_RATIOS.keys():
                # Create ratio-specific directory
                ratio_dir = os.path.join(product_output_dir, ratio_name)
                os.makedirs(ratio_dir, exist_ok=True)

                # Generate asset for this ratio
                output_path = os.path.join(
                    ratio_dir, f"{product_name}_{ratio_name}.png"
                )

                success_path = self.image_processor.create_canvas_asset(
                    base_image_path, campaign_message, ratio_name, output_path
                )

                if success_path:
                    generated_assets.append(
                        {
                            "ratio": ratio_name,
                            "path": success_path,
                            "dimensions": f"{Config.ASPECT_RATIOS[ratio_name][0]}x{Config.ASPECT_RATIOS[ratio_name][1]}",
                        }
                    )

            return {
                "product": product_name,
                "assets_generated": len(generated_assets),
                "assets": generated_assets,
                "status": "success",
            }

        except Exception as e:
            return {"error": str(e)}

    def _get_or_generate_image(self, product_name, target_audience):
        """Get existing image or generate new one"""
        # Check for existing assets first
        input_path = os.path.join(Config.ASSETS_FOLDER, product_name)
        if os.path.exists(input_path):
            for file in os.listdir(input_path):
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    return os.path.join(input_path, file)

        # Generate new image using DALL-E
        return self.image_processor.generate_dalle_image(product_name, target_audience)
