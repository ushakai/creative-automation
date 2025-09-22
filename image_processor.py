import os
import requests
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from config import Config


class ImageProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def generate_dalle_image(self, product_name, target_audience):
        """Generate base image using OpenAI DALL-E"""
        try:
            prompt = f"Professional product photography of {product_name.replace('_', ' ')} for {target_audience}, clean background, high quality, commercial style"

            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            # Download and save the generated image
            image_url = response.data[0].url
            image_response = requests.get(image_url)

            if image_response.status_code == 200:
                # Save to assets folder
                product_asset_dir = os.path.join(Config.ASSETS_FOLDER, product_name)
                os.makedirs(product_asset_dir, exist_ok=True)

                image_path = os.path.join(
                    product_asset_dir, f"generated_{product_name}.png"
                )
                with open(image_path, "wb") as f:
                    f.write(image_response.content)

                return image_path

        except Exception as e:
            print(f"Error generating DALL-E image: {e}")
            return None

    def create_canvas_asset(self, base_image_path, message, ratio_name, output_path):
        """Create asset using canvas extension method"""
        try:
            width, height = Config.ASPECT_RATIOS[ratio_name]

            with Image.open(base_image_path) as base_img:
                if base_img.mode != "RGB":
                    base_img = base_img.convert("RGB")

                # Create smart background instead of plain color
                canvas = self._create_smart_background(
                    base_img, width, height, ratio_name
                )

                # Position base image on canvas
                positioned_img = self._position_image_on_canvas(
                    base_img, ratio_name, width, height
                )

                # Paste the positioned image onto canvas
                canvas.paste(
                    positioned_img,
                    self._get_paste_position(positioned_img, ratio_name, width, height),
                )

                # Add text overlay
                self._add_professional_text(canvas, message, ratio_name)

                # Save final asset
                canvas.save(output_path, "PNG", quality=95)
                return output_path

        except Exception as e:
            print(f"Error creating canvas asset: {e}")
            return None

    def _create_smart_background(self, base_img, width, height, ratio_name):
        """Create intelligent background based on original image"""
        # Extract dominant color from base image
        base_img_small = base_img.resize((50, 50))
        pixels = list(base_img_small.getdata())

        # Get average color
        r = sum([pixel[0] for pixel in pixels]) // len(pixels)
        g = sum([pixel[1] for pixel in pixels]) // len(pixels)
        b = sum([pixel[2] for pixel in pixels]) // len(pixels)

        # Create subtle gradient background
        canvas = Image.new("RGB", (width, height))

        # Create gradient effect
        for y in range(height):
            # Vary color slightly across height
            factor = y / height
            new_r = int(r * (0.7 + factor * 0.3))
            new_g = int(g * (0.7 + factor * 0.3))
            new_b = int(b * (0.7 + factor * 0.3))

            # Ensure values stay in valid range
            new_r = min(255, max(0, new_r))
            new_g = min(255, max(0, new_g))
            new_b = min(255, max(0, new_b))

            color = (new_r, new_g, new_b)

            # Draw line across width
            for x in range(width):
                canvas.putpixel((x, y), color)

        return canvas

    def _position_image_on_canvas(
        self, base_img, ratio_name, canvas_width, canvas_height
    ):
        """Position and resize image based on ratio"""
        base_width, base_height = base_img.size

        if ratio_name == "1x1":
            # Keep original size for square
            return base_img

        elif ratio_name == "9x16":
            # Vertical format - scale to fit width, position in upper portion
            scale = canvas_width / base_width
            new_height = int(base_height * scale)
            return base_img.resize((canvas_width, new_height), Image.Resampling.LANCZOS)

        elif ratio_name == "16x9":
            # Horizontal format - scale to fit height, center horizontally
            scale = canvas_height / base_height
            new_width = int(base_width * scale)
            return base_img.resize((new_width, canvas_height), Image.Resampling.LANCZOS)

        return base_img

    def _get_paste_position(self, img, ratio_name, canvas_width, canvas_height):
        """Get position to paste image on canvas"""
        img_width, img_height = img.size

        if ratio_name == "1x1":
            return (0, 0)

        elif ratio_name == "9x16":
            # Center horizontally, position in upper 60%
            x = (canvas_width - img_width) // 2
            y = int(canvas_height * 0.1)  # 10% from top
            return (x, y)

        elif ratio_name == "16x9":
            # Center both axes
            x = (canvas_width - img_width) // 2
            y = (canvas_height - img_height) // 2
            return (x, y)

        return (0, 0)

    def _add_professional_text(self, canvas, message, ratio_name):
        """Add professionally styled text overlay"""
        draw = ImageDraw.Draw(canvas)
        canvas_width, canvas_height = canvas.size

        # Calculate font size based on canvas and ratio
        font_size = self._calculate_font_size(canvas_width, canvas_height, ratio_name)

        # Try to use bold font
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)  # Bold Arial
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Get text dimensions
        bbox = draw.textbbox((0, 0), message, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Smart positioning based on image content
        x, y = self._get_smart_text_position(
            canvas, text_width, text_height, ratio_name
        )

        # Create subtle background
        self._create_stylish_background(draw, x, y, text_width, text_height, None)

        # Add text with nice colors and shadow
        draw.text((x + 2, y + 2), message, font=font, fill=(0, 0, 0, 120))
        # Main text - nice vibrant color
        draw.text((x, y), message, font=font, fill=(255, 255, 255, 255))

    def _calculate_font_size(self, width, height, ratio_name):
        """Calculate appropriate font size for each ratio"""
        base_size = min(width, height) // 26  # Increased from 28 to make bigger

        # Adjust for different ratios (+2 to all previous sizes)
        if ratio_name == "9x16":
            return max(24, base_size)  
        elif ratio_name == "16x9":
            return max(22, base_size)  
        else:  # 1x1
            return max(26, base_size)  

    def _get_smart_text_position(self, canvas, text_width, text_height, ratio_name):
        """Smart positioning based on image content and empty space"""
        canvas_width, canvas_height = canvas.size

        # More strategic positioning
        if ratio_name == "9x16":
            # Center in the gray area below the laptop image
            x = (canvas_width - text_width) // 2  # Center horizontally
            y = int(canvas_height * 0.85)  # Position in lower gray area

        elif ratio_name == "16x9":
            # Top left corner, less intrusive
            x = 20
            y = 20

        else:  # 1x1
            # Bottom right corner
            x = canvas_width - text_width - 20
            y = canvas_height - text_height - 20

        return (x, y)

    def _create_stylish_background(self, draw, x, y, text_width, text_height, colors):
        """Create stylish but subtle background for text"""
        padding = 12

        # Create subtle rounded rectangle background
        left = x - padding
        top = y - padding
        right = x + text_width + padding
        bottom = y + text_height + padding

        draw.rounded_rectangle(
            [left, top, right, bottom],
            radius=6,
            fill=(0, 0, 0, 180),  # Darker for better contrast
        )
