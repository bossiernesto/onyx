from types import MethodType
from . import resource
from .resourceHelper import TYPE_JSON, TYPE_ZIP, TYPE_JPG, TYPE_PNG
from PIL import Image


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


def open_image(self):
    import io

    image_file = io.BytesIO(self.raw)
    return Image.open(image_file)


behaviour = {TYPE_JSON: json, TYPE_ZIP: uncompress, TYPE_JPG: open_image, TYPE_PNG: open_image}


def inject_behaviour(response):
    if not isinstance(response, resource.Request):
        raise TypeError('Not of type {0}'.format(resource.Request))

    try:
        tipe = response.info['content-type'].split(';')[0]
        method_to_inject = behaviour[tipe]
        name_function = method_to_inject.__name__
        response.__dict__[name_function] = MethodType(method_to_inject, response)
    except KeyError:
        # NO behaviour to Inject
        return

