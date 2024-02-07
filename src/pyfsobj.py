from functools import lru_cache

from fs.move import copy_file, move_file


class File:
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

    # return the same file, after it's moved
    def move_to(self, dest_fs):
        move_file(
            src_fs=self.filesystem,
            src_path=self.filename,
            dst_fs=dest_fs,
            dst_path=self.filename,
        )
        self.filesystem = dest_fs
        return self

    # returns a new object with the copy of the file
    def copy_to(self, dest_fs):
        copy_file(
            src_fs=self.filesystem,
            src_path=self.filename,
            dst_fs=dest_fs,
            dst_path=self.filename,
        )
        return File(dest_fs, self.filename)

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
