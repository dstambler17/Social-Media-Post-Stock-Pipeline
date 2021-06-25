
import requests
import logging
import pytesseract
from PIL import Image
from src.utils.custom_decorators import time_func

class OCR:
    @staticmethod
    @time_func
    def get_text_from_image(image_url) -> str:
        '''
        extracts text from image url
        '''
        logger = logging.getLogger(__name__)

        im = Image.open(requests.get(image_url, stream=True).raw)
        text = pytesseract.image_to_string(im)
        if len(text) < 17:
            return None
        else:
            logger.info('Extracted OCR text for image_url: %s' % image_url)
            logger.info('Text extracted: %s' % text)
            return text

