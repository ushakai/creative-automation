import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY")

    # File Upload Configuration
    UPLOAD_FOLDER = "uploads"
    ASSETS_FOLDER = "assets"
    OUTPUTS_FOLDER = "outputs"

    # Supported aspect ratios
    ASPECT_RATIOS = {
        "1x1": (1024, 1024),  # Instagram square
        "9x16": (576, 1024),  # Instagram story
        "16x9": (1024, 576),  # Facebook landscape
    }

    # Default products
    PRODUCTS = ["running_shoes", "coffee_beans"]
