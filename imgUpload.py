import os
from uuid import uuid4
from flask import current_app  # current_app 属于应用上下文，代表项目中的app本身


def img_upload(img):
    if not img:
        return None

    end_name = img.filename.rsplit('.')[-1]

    if end_name not in ['jpg', 'png', 'gif', 'jpeg']:
        return None

    media = current_app.config['MEDIA_PATH']
    # print(media)
    filename = str(uuid4()) + '.' + end_name
    img_path = os.path.join(media, filename)

    img.save(img_path)

    return filename
