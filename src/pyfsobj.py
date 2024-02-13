import datetime
from functools import lru_cache

from fs.move import copy_file, move_file
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

# from PIL.ExifTags import TAGS


class FileWrapper:
    def __init__(self, filesystem, filename, check=True):
        # @todo Check if filesystem is a filesystem
        self.filesystem = filesystem
        # @todo: Here, make sure this filename does not contain any path
        # separator

        # @todo: Here, make sure the filename is not a directory
        # and if it is, raise an exception and ask for the filesystem

        # @todo: Here, make sure the file is not an alias. We onoy
        # support actual files for now
        # If so, raise an exception
        self.filename = filename
        if check and not self.exists():
            raise FileNotFoundError(f"File {filename} does not exist")

    @staticmethod
    def check_validity(callable):
        def wrapper(*args, **kwargs):
            self = args[0]
            if self.filesystem is None:
                raise ValueError("File has been deleted")
            return callable(*args, **kwargs)

        return wrapper

    def __repr__(self):
        return f"FileWrapper({self.filesystem}, {self.filename})"

    # return the same file, after it's moved
    def move_to(self, dest_fs, *, as_name=None, new_name_if_needed=False):
        as_name = as_name or self.filename
        if new_name_if_needed:
            if dest_fs.exists(as_name):
                return self.move_to(
                    dest_fs,
                    as_name=f"Copy of {as_name}",
                    new_name_if_needed=True,
                )

        move_file(
            src_fs=self.filesystem,
            src_path=self.filename,
            dst_fs=dest_fs,
            dst_path=as_name,
        )
        self.filesystem = dest_fs
        self.filename = as_name
        return self

    def trash(self, *, trash_filesystem=None, for_real=False, as_name=None):
        if for_real:
            self.filesystem.remove(self.filename)
            self.filesystem = None
            self.filename = None
            return self
        else:
            trash = trash_filesystem or self.filesystem.makedir(
                ".trash", recreate=True
            )
            # Here, check if the file is already in the trash first
            return self.move_to(trash, new_name_if_needed=True)

    # returns a new object with the copy of the file
    def copy_to(self, dest_fs, as_name=None):
        copy_file(
            src_fs=self.filesystem,
            src_path=self.filename,
            dst_fs=dest_fs,
            dst_path=as_name or self.filename,
        )
        return FileWrapper(dest_fs, as_name or self.filename)

    # used all over the place, and just in casse
    def exists(self):
        return self.filesystem.exists(self.filename)

    @property
    @lru_cache(maxsize=None)
    def md5(self):
        return self.filesystem.hash(self.filename, "md5")

    @property
    def size(self):
        return self.filesystem.getinfo(
            self.filename, namespaces=["details"]
        ).size

    def is_same(self, other):
        return self.size == other.size and self.md5 == other.md5

    def is_image(self):
        return self.filename.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".heic", ".nef")
        )

    @property
    @lru_cache(maxsize=None)
    def exif(self):
        if self.is_image():
            with self.filesystem.open(self.filename, "rb") as imfile:
                try:
                    with Image.open(imfile) as opened:
                        return opened.getexif()
                except Image.UnidentifiedImageError:
                    return None
        return None

    @property
    def date(self):
        if self.exif:
            exif_d = (
                self.exif.get(36867)
                or self.exif.get(36868)
                or self.exif.get(306)
            )
            return exif_d and datetime.datetime.strptime(
                exif_d, "%Y:%m:%d %H:%M:%S"
            )
        return None
