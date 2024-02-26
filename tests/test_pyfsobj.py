import os

import fs

from pyfsobj import FileWrapper


def test_import():
    assert type(FileWrapper) is type


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

    f = FileWrapper(srcdir, "hello.txt")
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

    f = FileWrapper(srcdir, "hello.txt")
    f2 = f.move_to(destdir)

    assert f2 is f
    assert srcdir.listdir(".") == []
    assert destdir.listdir(".") == ["hello.txt"]
    assert f.exists() is True
    assert f.filesystem == destdir
    assert f.filename == "hello.txt"


def test_trash_two_files_will_create_a_trash_file_with_two_files():
    myFs = fs.open_fs("mem://")
    srcdir = myFs.makedir("mydir1")

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    srcdir.create("hello2.txt")
    with srcdir.open("hello2.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.listdir(".") == ["hello.txt", "hello2.txt"]

    f = FileWrapper(srcdir, "hello.txt")
    f2 = FileWrapper(srcdir, "hello2.txt")
    f.trash()

    trashdir = srcdir.opendir(".trash")
    assert trashdir.listdir(".") == ["hello.txt"]

    f2.trash()

    assert srcdir.listdir(".") == [".trash"]
    assert trashdir.listdir(".") == ["hello.txt", "hello2.txt"]


def test_trash_same_file_twice_will_create_a_trash_with_2_files():
    myFs = fs.open_fs("mem://")
    srcdir = myFs.makedir("mydir1")

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.listdir(".") == ["hello.txt"]

    f = FileWrapper(srcdir, "hello.txt")
    f.trash()

    # Now do the seocond one

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello2:
        hello2.write("Hello World!")

    assert srcdir.listdir(".") == [".trash", "hello.txt"]

    f2 = FileWrapper(srcdir, "hello.txt")
    f2.trash()

    trashdir = srcdir.opendir(".trash")

    assert srcdir.listdir(".") == [".trash"]
    assert trashdir.listdir(".") == ["hello.txt", "Copy of hello.txt"]


def test_trash_diff_file_same_name_will_create_a_trash_file_with_two_file():
    myFs = fs.open_fs("mem://")
    srcdir = myFs.makedir("mydir1")

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.listdir(".") == ["hello.txt"]

    f = FileWrapper(srcdir, "hello.txt")
    f.trash()

    # Now do the seocond one

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello2:
        hello2.write("Hello World! Again.")

    assert srcdir.listdir(".") == [".trash", "hello.txt"]

    f2 = FileWrapper(srcdir, "hello.txt")
    f2.trash()

    trashdir = srcdir.opendir(".trash")

    assert srcdir.listdir(".") == [".trash"]
    assert trashdir.listdir(".") == ["hello.txt", "Copy of hello.txt"]


def test_can_trash_file_for_real():
    myFs = fs.open_fs("mem://")
    srcdir = myFs.makedir("mydir1")

    srcdir.create("hello.txt")
    with srcdir.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    assert srcdir.listdir(".") == ["hello.txt"]

    f = FileWrapper(srcdir, "hello.txt")
    f.trash(for_real=True)

    assert srcdir.listdir(".") == []


def test_can_trash_file_in_trash_dir_fromn_diff_dirs():
    myFs = fs.open_fs("mem://")
    srcdir1 = myFs.makedir("mydir1")
    srcdir2 = myFs.makedir("mydir2")
    trash = myFs.makedir(".trash")

    srcdir1.create("hello.txt")
    with srcdir1.open("hello.txt", "w") as hello:
        hello.write("Hello World!")

    f1 = FileWrapper(srcdir1, "hello.txt")
    f2 = f1.copy_to(srcdir2, as_name="hello2.txt")

    assert srcdir1.listdir(".") == ["hello.txt"]
    assert srcdir2.listdir(".") == ["hello2.txt"]

    assert f1.filesystem == srcdir1
    f1.trash(trash_filesystem=trash)
    assert f1.filesystem == trash

    assert f2.filesystem == srcdir2
    f2.trash(trash_filesystem=trash)
    assert f2.filesystem == trash

    assert srcdir1.listdir(".") == []
    assert srcdir2.listdir(".") == []
    assert trash.listdir(".") == ["hello.txt", "hello2.txt"]


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

    f = FileWrapper(srcdir, "hello.txt")
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
    destdir = mysecondFs.makedir("my_mem_dir")

    assert set(srcdir.listdir(".")) == set(
        [
            "NGC2841_Astrobin.jpg",
            "DSC_9229 copy.jpeg",
            "DSC_9229.jpeg",
            "IMG_0238.heic",
            "LPL_2009.JPG",
            "LPL_2009.JPG",
            "STScI-01G8GZQ3ZFJRD8YF8YZWMAXCE3.png",
            "DSC_00332005-07-16.NEF",
        ]
    )
    assert destdir.listdir(".") == []

    f = FileWrapper(srcdir, "NGC2841_Astrobin.jpg")
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
            file = FileWrapper(filesystem, f.name)

            d_md5[file.md5] = d_md5.get(file.md5, []) + [file]

    duplicates = [v for v in d_md5.values() if len(v) > 1]
    assert len(duplicates) == 1  # Only one hash is duplicated
    assert len(duplicates[0]) == 3  # Three files with the same hash
    assert (
        len(set(item.md5 for item in duplicates[0])) == 1
    )  # One hash for all three files


def test_can_read_exif():
    myfirstFs = fs.open_fs(os.path.join(os.path.split(__file__)[0], "data"))
    srcdir = myfirstFs.opendir("dir_one")

    f = FileWrapper(srcdir, "DSC_00332005-07-16.NEF")
    assert f.is_image() is True
    assert f.exif is not None
    """
    assert f.exif["Model"] == "NIKON D70"
    assert f.exif["ExposureTime"] == "1/60"
    assert f.exif["FNumber"] == "5.6"
    assert f.exif["ISOSpeedRatings"] == 200
    assert f.exif["DateTimeOriginal"] == "2005:07:16 11:26:30"
    assert f.exif["FocalLength"] == "70.0 mm"
    assert f.exif["LensModel"] == "18.0-70.0 mm f/3.5-4.5"
    assert f.exif["LensID"] == "AF-S DX Zoom-Nikkor 18-70mm f/3.5-4.5G IF-ED"
    assert f.exif["LensSpec"] == "18.0-70.0 mm f/3.5-4.5"
    assert f.exif["LensMake"] == "NIKON CORPORATION"
    assert f.exif["LensSerialNumber"] == "200211"
    assert f.exif["LensFirmwareVersion"] == "1.01"
    assert f.exif["LensType"] == "G VR"
    assert f.exif["LensInfo"] == "18-70mm f/3.5-4.5"
    assert f.exif["LensModel"] == "18.0-70.0 mm f/3.5-4.5"
    assert f.exif["LensSerialNumber"] == "200211"
    assert f.exif["LensFirmwareVersion"] == "1.01"
    assert f.exif["LensType"] == "G VR"
    assert f.exif["LensInfo"] == "18-70mm f/3.5-4.5"
    assert f.exif["LensModel"] == "18.0-70.0 mm f/3"
    """


def test_can_convert_to_mp4():
    # First move the mov file to a temp dir in memory
    # Then convert it to mp4
    # Then check the file is there
    # Then check the file is an mp4

    myfirstFs = fs.open_fs(os.path.join(os.path.split(__file__)[0], "data"))
    srcdir = myfirstFs.opendir("films")
    mov_file = FileWrapper(srcdir, "clip-2009-04-12 02;49;22.mov")
    assert mov_file.is_video() is True
    mp4_file = mov_file.to_mp4(srcdir)
    assert mp4_file.is_video() is True
    assert mp4_file.filename.endswith(".mp4")
    mp4_file.trash(for_real=True)
