
import io
import base64
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from functools import wraps

def decodeDesignImage(data):
    try:
        data = base64.b64decode(data.encode('UTF-8'))

        return data
    except Exception as e:
        print(f"Error decoding or verifying the image: {e}")
        return None

def saveimage(image, imgname):
    img = decodeDesignImage(image)
    
    data = ContentFile(img, f"{imgname}.jpg")
    
    return data

def staff_exists_required(func):
    from pprint import pprint
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        for index, item in enumerate(args):
            if hasattr(item, 'META'):
                ...
                
            
        return func(request, *args, **kwargs)
    return wrapper
