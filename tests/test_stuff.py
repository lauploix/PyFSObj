# from hello import hello_f

import os

import fs
from fs.move import move_file
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def test_move_between_mem_dirs():
    myFs = fs.open_fs("mem://")
    srcdir = myFs.makedir("mydir1")
    destdir = myFs.makedir("mydir2")

    listdir = myFs.listdir(".")
    assert listdir == ["mydir1", "mydir2"]

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.gettext("hello.txt") == "Hello World!"

    move_file(srcdir, "hello.txt", destdir, "hello_dest.txt")

    assert destdir.exists("hello_dest.txt")
    assert not srcdir.exists("hello.txt")
    assert destdir.gettext("hello_dest.txt") == "Hello World!"


def test_move_between_mem_filesystems():
    myfirstFs = fs.open_fs("mem://")
    mysecondFs = fs.open_fs("mem://")
    srcdir = myfirstFs.makedir("mydir1")
    destdir = mysecondFs.makedir("mydir2")

    assert myfirstFs.listdir(".") == ["mydir1"]
    assert mysecondFs.listdir(".") == ["mydir2"]

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.gettext("hello.txt") == "Hello World!"

    move_file(srcdir, "hello.txt", destdir, "hello_dest.txt")

    assert destdir.exists("hello_dest.txt")
    assert not srcdir.exists("hello.txt")
    assert destdir.gettext("hello_dest.txt") == "Hello World!"


def test_copy_between_real_and_mem_filesystems():
    # use the local data directory and copy its content in a mem filesystem
    myFs = fs.open_fs(os.path.join(os.path.split(__file__)[0], "data"))
    memFs = fs.open_fs("mem://")
    fs.copy.copy_dir(src_fs=myFs, dst_fs=memFs, src_path=".", dst_path=".")
    assert set(myFs.listdir(".")) == set(memFs.listdir("."))
    assert set(myFs.listdir("dir_one")) == set(memFs.listdir("dir_one"))

    # Check that the content of the file is the same
    with myFs.open("dir_one/DSC_9229.jpeg", "rb") as f1:
        with memFs.open("dir_one/DSC_9229.jpeg", "rb") as f2:
            read1 = f1.read()
            assert read1 == f2.read()
            assert len(read1) == 


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
