import os

import fs

from pyfsobj import FileWrapper

if __name__ == "__main__":
    srcfs = fs.open_fs("/Volumes/archives")
    destfs = fs.open_fs("/Volumes/archives/target")
    trashfs = srcfs.opendir("#recycle")

    for step in srcfs.walk(
        search="depth",
        exclude_dirs=[
            "#recycle",
            "System Volume Information",
            "lost+found",
            "old backup",
            "Archives",
        ],
    ):
        filesystem = srcfs.opendir(step.path)
        if filesystem.getospath(".").startswith(trashfs.getospath(".")):
            pass
        else:
            for f in step.files:
                file = FileWrapper(filesystem, f.name)
                if file.is_image():
                    if file.date:
                        year = file.date.year
                        month = file.date.month
                        new_name = f.name
                    else:
                        year = 0
                        month = 0
                        dir_name = os.path.split(filesystem.getospath("."))[
                            -1
                        ].decode("utf-8")
                        new_name = f"{dir_name}.{f.name}"

                    s_year = f"{year:04d}"
                    s_month = f"{month:02d}"

                    print(file, file.date, s_year, s_month)

                    try:
                        target = destfs.opendir(f"{s_year}/{s_month}")
                    except fs.errors.ResourceNotFound:
                        target = destfs.makedirs(f"{s_year}/{s_month}")

                    if target.exists(new_name):
                        target_file = FileWrapper(target, new_name)
                        if target_file.md5 == file.md5:
                            file.trash(trash_filesystem=trashfs)
                        else:
                            file.move_to(
                                target,
                                as_name="Copy of " + new_name,
                                new_name_if_needed=True,
                            )
                    else:
                        file.move_to(target, as_name=new_name)

                    # md5 = file.md5

                    # 1- Goal: Move file in YYYY/MM under dest_dir
                    # 2- If file exists already with same name
                    # in dest_dir, then check for md5
                    # 3- If same md5, move to trash dir
                    # 4- if not same MD5, then rename file and move
                    # to dest_dir/YYYY/MM
