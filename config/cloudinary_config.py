import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv
from os import getenv

data = load_dotenv()

load_dotenv(dotenv_path="external_keys.env")

CLOUD_NAME = getenv("CLOUD_NAME")
API_KEY = getenv("API_KEY")
API_SECRET = getenv("API_SECRET")


# Configuration
cloudinary.config(
    cloud_name = CLOUD_NAME,
    api_key = API_KEY,
    api_secret = API_SECRET,
    secure = True
)

# Upload an image
async def upload_avatar(image_file, email: str):
    content = await image_file.read()
    upload_result = cloudinary.uploader.upload(content, 
                                               folder="avatars/", 
                                               public_id = f"email {email} avatar", 
                                               overwrite = True, 
                                               transformation = [{"width": 300, "height": 300, "crop": "thumb", "gravity": "face"}])
    return upload_result['secure_url']


# # Optimize delivery by resizing and applying auto-format and auto-quality
# optimize_url, _ = cloudinary_url("avatars", fetch_format="auto", quality="auto")
# print(optimize_url)

# # Transform the image: auto-crop to square aspect_ratio
# auto_crop_url, _ = cloudinary_url("avatars", width=500, height=500, crop="auto", gravity="auto")
# print(auto_crop_url)


