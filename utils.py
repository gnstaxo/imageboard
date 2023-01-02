import os
import re
import random
import hashlib
import shutil
import filetype
from string import ascii_lowercase
from PIL import Image

def thumbnail(path, refnum, ext, is_reply=False):

    save_path = "/".join(path.split("/")[0:2]) + "/" + str(refnum) + "s.jpg"

    with Image.open(path) as im:

        if im.height < im.width:

            thumb_width = 125 if is_reply else 250
            thumb_height = round(im.height * (thumb_width / im.width))

            im = im.resize((thumb_width, thumb_height))
        else:
            thumb_height = 125 if is_reply else 250
            thumb_width = round(im.width * (thumb_height / im.height))

            im = im.resize((thumb_width, thumb_height))

        if ext == '.png' and im.mode == "RGBA":

            bg = Image.new("RGB", (thumb_width, thumb_height), (255,255,255))

            bg.paste(im, im)
            bg.save(save_path)
        elif ext == '.gif':
            im.seek(0)
            im = im.convert('RGB')
            im.save(save_path)
        else:
            im.save(save_path)

def file_validation(board_name, refnum, upload, is_reply=False): 

    name, ext = os.path.splitext(upload.filename)

    valid_ext = ('png','jpg','jpeg','gif', 'mp4', 'webm', 'ogg')

    if ext[1:] not in valid_ext:
        return 1

    save_path = "uploads/%s/%s%s" % (board_name, refnum, ext)
    
    upload.save(save_path)

    mime = filetype.guess(save_path)

    if mime.EXTENSION not in valid_ext or mime.EXTENSION != ext[1:]:
        os.remove(save_path)
        return 1

    thumbnail(save_path, refnum, ext, is_reply)

    return save_path

def remove_media(path):

    name, ext = os.path.splitext(path)

    if ext not in ('.mp4', '.webm', '.ogg'): os.remove(name + "s.jpg")

    os.remove(path)

def random_name(): return ''.join(random.choices(ascii_lowercase, k=8))

def board_directory(name, remove=False):
    if remove: shutil.rmtree("uploads/%s" % name)
    else: os.makedirs("uploads/%s" % name, exist_ok=True)

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total

def author_color(author):
    return '#' + hashlib.blake2b(author.encode()).hexdigest()[:6]

def image_size(path):

    size = os.stat(path).st_size

    if not is_video(path):

        with Image.open(path) as im:

            width, height = im.size

        return "%s, %s x %s" % (get_size_format(size), width, height)
    else:
        return get_size_format(size)

def is_video(filename):

    name, ext = os.path.splitext(filename)

    if ext in ('.webm', '.mp4', '.ogg'): return True

    return False

def short_msg(string):

    ellipsis = ""

    if len(string.split(" ")) > 22: ellipsis = " ..."

    return ' '.join(string.split(" ")[:22]) + ellipsis
