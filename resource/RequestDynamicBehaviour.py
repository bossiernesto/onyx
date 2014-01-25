from types import MethodType
import resource
from ResourceHelper import TYPE_JSON,TYPE_ZIP,TYPE_JPG,TYPE_PNG

def uncompress(self):
    import os
    from zipfile import ZipFile as lzip
    import io

    z = lzip(io.BytesIO(self.raw))
    for f in z.namelist():
        if f.endswith('/'):
            os.makedirs(f)
        else:
            z.extract(f)

def json(self):
    import json
    return json.loads(self.raw)

def openImage(self):
    from PIL import Image
    import io
    imageFile = io.BytesIO(self.raw)
    return Image.open(imageFile)

behaviour={TYPE_JSON:json,TYPE_ZIP:uncompress,TYPE_JPG:openImage,TYPE_PNG:openImage}

def injectBehaviour(response):

    if not isinstance(response,resource.Request):
        raise TypeError('Not of type {0}'.format(resource.Request))

    try:
        tipe=response.info['content-type'].split(';')[0]
        methodToInject=behaviour[tipe]
        name_function=methodToInject.__name__
        response.__dict__[name_function]=MethodType(methodToInject,response)
    except KeyError:
        return # NO behaviour to Inject

