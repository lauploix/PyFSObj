import os

import fs

from pyfsobj import File


def test_import():
    assert type(File) is type


def test_move_between_mem_dirs():
    myFs = fs.open_fs("mem://")
    srcdir = myFs.makedir("mydir1")
    destdir = myFs.makedir("mydir2")

    assert isinstance(srcdir, fs.subfs.SubFS)

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.listdir(".") == ["hello.txt"]
    assert destdir.listdir(".") == []

    f = File(srcdir, "hello.txt")
    f2 = f.move_to(destdir)

    assert f2 is f
    assert srcdir.listdir(".") == []
    assert destdir.listdir(".") == ["hello.txt"]
    assert f.exists() is True
    assert f.filesystem == destdir
    assert f.filename == "hello.txt"


def test_move_between_mem_filesystems():
    myfirstFs = fs.open_fs("mem://")
    mysecondFs = fs.open_fs("mem://")
    srcdir = myfirstFs.makedir("mydir1")
    destdir = mysecondFs.makedir("mydir2")

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.listdir(".") == ["hello.txt"]
    assert destdir.listdir(".") == []

    f = File(srcdir, "hello.txt")
    f2 = f.move_to(destdir)

    assert f2 is f
    assert srcdir.listdir(".") == []
    assert destdir.listdir(".") == ["hello.txt"]
    assert f.exists() is True
    assert f.filesystem == destdir
    assert f.filename == "hello.txt"


def test_copy_between_mem_filesystems():
    myfirstFs = fs.open_fs("mem://")
    mysecondFs = fs.open_fs("mem://")
    srcdir = myfirstFs.makedir("mydir1")
    destdir = mysecondFs.makedir("mydir2")

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.listdir(".") == ["hello.txt"]
    assert destdir.listdir(".") == []

    f = File(srcdir, "hello.txt")
    f2 = f.copy_to(destdir)

    assert f2 is not f
    assert srcdir.listdir(".") == ["hello.txt"]
    assert destdir.listdir(".") == ["hello.txt"]
    assert f2.exists() is True
    assert f.exists() is True
    assert f.filesystem == srcdir
    assert f.filename == "hello.txt"
    assert f2.filesystem == destdir
    assert f2.filename == "hello.txt"

    assert f2.is_same(f) is True


def test_copy_between_real_and_mem_filesystems():
    myfirstFs = fs.open_fs(os.path.join(os.path.split(__file__)[0], "data"))
    mysecondFs = fs.open_fs("mem://")
    srcdir = myfirstFs.opendir("dir_one")
    destdir = mysecondFs.makedir("mydir2")

    assert set(srcdir.listdir(".")) == set(
        [
            "NGC2841_Astrobin.jpg",
            "DSC_9229 copy.jpeg",
            "DSC_9229.jpeg",
            "IMG_0238.heic",
            "LPL_2009.JPG",
            "LPL_2009.JPG",
            "STScI-01G8GZQ3ZFJRD8YF8YZWMAXCE3.png",
        ]
    )
    assert destdir.listdir(".") == []

    f = File(srcdir, "NGC2841_Astrobin.jpg")
    f2 = f.copy_to(destdir)

    assert f2 is not f
    assert destdir.listdir(".") == ["NGC2841_Astrobin.jpg"]
    assert f2.exists() is True
    assert f.exists() is True
    assert f.filesystem == srcdir
    assert f.filename == "NGC2841_Astrobin.jpg"
    assert f2.filesystem == destdir
    assert f2.filename == "NGC2841_Astrobin.jpg"

    assert f2.is_same(f) is True


def test_walk():
    d_md5 = {}

    myfirstFs = fs.open_fs(os.path.join(os.path.split(__file__)[0], "data"))
    for step in myfirstFs.walk():
        for f in step.files:
            filesystem = myfirstFs.opendir(step.path)
            file = File(filesystem, f.name)

            d_md5[file.md5] = d_md5.get(file.md5, []) + [file]

    duplicates = [v for v in d_md5.values() if len(v) > 1]
    assert len(duplicates) == 1  # Only one hash is duplicated
    assert len(duplicates[0]) == 3  # Three files with the same hash
    assert (
        len(set(item.md5 for item in duplicates[0])) == 1
    )  # One hash for all three files
