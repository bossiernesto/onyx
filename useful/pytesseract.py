tesseract_cmd = 'tesseract-ocr'

from PIL import Image
import io
import subprocess
import sys
import os

__all__ = ['image_to_string']


def run_tesseract(input_filename, output_filename_base, lang=None, boxes=False):
    """
    runs the command:
        `tesseract_cmd` `input_filename` `output_filename_base`

    returns the exit status of tesseract, as well as tesseract's stderr output

    """

    command = [tesseract_cmd, input_filename, output_filename_base]

    if lang is not None:
        command += ['-l', lang]

    if boxes:
        command += ['batch.nochop', 'makebox']

    proc = subprocess.Popen(command,
                            stderr=subprocess.PIPE)
    return proc.wait(), proc.stderr.read()


def cleanup(filename):
    """ tries to remove the given filename. Ignores non-existent files """
    try:
        os.remove(filename)
    except OSError:
        pass


def get_errors(error_string):
    """
    returns all lines in the error_string that start with the string "error"

    """

    lines = error_string.splitlines()
    error_lines = tuple(line for line in lines if line.find('Error') >= 0)
    if len(error_lines) > 0:
        return '\n'.join(error_lines)
    else:
        return error_string.strip()


def tempnam():
    """ returns a temporary file-name """

    # prevent os.tmpname from printing an error...
    stderr = sys.stderr
    try:
        sys.stderr = io.StringIO()
        return os.tempnam(None, 'tess_')
    finally:
        sys.stderr = stderr


class TesseractError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.args = (status, message)


def image_to_string(image, lang=None, boxes=False):
    """
    Runs tesseract on the specified image. First, the image is written to disk,
    and then the tesseract command is run on the image. Resseract's result is
    read, and the temporary files are erased.
    """

    input_file_name = '%s.bmp' % tempnam()
    output_file_name_base = tempnam()
    if not boxes:
        output_file_name = '%s.txt' % output_file_name_base
    else:
        output_file_name = '%s.box' % output_file_name_base
    try:
        image.save(input_file_name)
        status, error_string = run_tesseract(input_file_name,
                                             output_file_name_base,
                                             lang=lang,
                                             boxes=boxes)
        if status:
            errors = get_errors(error_string)
            raise TesseractError(status, errors)
        f = open(output_file_name)
        try:
            return f.read().strip()
        finally:
            f.close()
    finally:
        cleanup(input_file_name)
        cleanup(output_file_name)


if __name__ == '__main__':
    filename = '../test/Captcha.png'
    im = Image.open(filename)
    rgbimg = im.convert('RGB')
    print()
    image_to_string(rgbimg)