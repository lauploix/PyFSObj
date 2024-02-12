from functools import lru_cache

from fs.move import copy_file, move_file


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

    # return the same file, after it's moved
    @check_validity
    def move_to(self, dest_fs, as_name=None):
        move_file(
            src_fs=self.filesystem,
            src_path=self.filename,
            dst_fs=dest_fs,
            dst_path=as_name or self.filename,
        )
        self.filesystem = dest_fs
        self.filename = as_name or self.filename
        return self

    @check_validity
    def trash(self, for_real=False, trash_filesystem=None):
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
            if not trash.exists(self.filename):
                return self.move_to(trash)
            else:
                # if there's another file in the trash
                # with the same name
                return self.move_to(
                    trash,
                    as_name="Copy of " + self.filename,
                )

    # returns a new object with the copy of the file
    @check_validity
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
    @check_validity
    def md5(self):
        return self.filesystem.hash(self.filename, "md5")

    @property
    @check_validity
    def size(self):
        return self.filesystem.getinfo(
            self.filename, namespaces=["details"]
        ).size

    @check_validity
    def is_same(self, other):
        return self.size == other.size and self.md5 == other.md5
