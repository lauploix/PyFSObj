# from hello import hello_f

import os

import fs
from fs.move import move_file
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def test_stuff():
    myFs = fs.open_fs("mem://")
    srcfs = myFs.makedir("mydir1")
    destfs = myFs.makedir("mydir2")

    hello = srcfs.create("hello.txt")
    with srcfs.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcfs.gettext("hello.txt") == "Hello World!"

    move_file(srcfs, "hello.txt", destfs, "hello.txt")

    assert destfs.exists("hello.txt")
    assert not srcfs.exists("hello.txt")
    assert destfs.gettext("hello.txt") == "Hello World!"


def test_exif():
    myFs = fs.open_fs(os.path.join(os.path.split(__file__)[0], "data"))
    memFs = fs.open_fs("mem://")
    fs.copy.copy_dir(src_fs=myFs, dst_fs=memFs, src_path=".", dst_path=".")
    files = memFs.walk.files(
        filter=["*.jpg", "*.jpeg", "*.png", "*.heic", "*.bmp"]
    )
    for file in files:
        with memFs.open(file, "rb") as imfile:  # open first
            with Image.open(imfile) as opened:  # file like object
                exif = opened.getexif()
                print(file, ": ", exif.get(306, "0000:00:00 00:00:00"))
