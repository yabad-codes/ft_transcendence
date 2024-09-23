from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting
from urllib.parse import urljoin

class GoogleCloudMediaStorage(GoogleCloudStorage):
    """
    A class representing Google Cloud Storage for media files.

    This class extends the base GoogleCloudStorage class and provides
    functionality specific to media files.

    Attributes:
        bucket_name (str): The name of the Google Cloud Storage bucket.
    """

    bucket_name = setting('GS_BUCKET_NAME')

    def url(self, name):
        """
        Generate the URL for a media file.

        Args:
            name (str): The name of the media file.

        Returns:
            str: The URL of the media file.
        """
        return urljoin(settings.MEDIA_URL, name)