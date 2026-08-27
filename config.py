import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    DATABASE = os.path.join(BASE_DIR, "petpulse.db")

    PET_IMAGE_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "pets")
    REPORT_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "reports")

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_REPORT_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx"}

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
