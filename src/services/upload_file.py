import logging
import cloudinary
import cloudinary.uploader

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)


class UploadFileService:
    """
    Service for uploading files to Cloudinary.
    """

    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initialize the Cloudinary configuration.

        :param cloud_name: Cloudinary cloud name.
        :param api_key: Cloudinary API key.
        :param api_secret: Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Upload a file to Cloudinary and return the URL.

        :param file: File object to be uploaded.
        :param username: Username for unique file identification.
        :return: URL of the uploaded file.
        """
        logging.debug(f"Uploading file for user: {username}")

        try:
            public_id = f"RestApp/{username}"
            r = cloudinary.uploader.upload(
                file.file, public_id=public_id, overwrite=True
            )
            logging.debug(f"Upload response: {r}")
            src_url = cloudinary.CloudinaryImage(public_id).build_url(
                width=250, height=250, crop="fill", version=r.get("version")
            )
            return src_url
        except Exception as e:
            logging.error(f"Cloudinary upload error: {e}")
            raise
