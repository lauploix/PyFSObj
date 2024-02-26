import os
import tempfile

import fs

from pyfsobj import FileWrapper

if __name__ == "__main__":
    srcfs = fs.open_fs("/Volumes/video/Famille")
    rawfs = fs.open_fs("/Volumes/raw")
    with tempfile.TemporaryDirectory() as tmpdirname:
        tempfs = fs.open_fs(tmpdirname)
        # Create a local temporary folder

        for step in srcfs.walk(
            search="depth",
            exclude_dirs=[
                "#recycle",
                "@eaDir",
            ],
            filter=["*.mov", "*.wmv", "*.m2ts", "*.avi"],
        ):
            filesystem = srcfs.opendir(step.path)
            for file in step.files:
                wrapper = FileWrapper(filesystem, file.name)
                dir, f = os.path.split(wrapper.fullpath)
                target_dir = dir.replace("/Volumes/video/Famille/", "")
                if wrapper.is_video():
                    print()
                    print()
                    print("**************************")
                    print(wrapper.fullpath)
                    print("**************************")
                    if wrapper.fullpath.endswith(
                        (
                            ".mov",
                            ".wmv",
                            ".m2ts",
                            ".avi",
                        )
                    ):
                        print(
                            "Copyping" + wrapper.fullpath + " to " + tmpdirname
                        )
                        copied = wrapper.copy_to(tempfs)

                        target_fs = rawfs.makedirs(target_dir, recreate=True)
                        print("Creating mp4 in " + step.path)
                        try:
                            mp4 = copied.to_mp4(tempfs)
                        except ValueError as e:
                            print(e)
                            print("Error converting " + copied.fullpath)
                            continue

                        print("Moving mp4 (in tempfs) file to " + step.path)
                        mp4.move_to(filesystem, new_name_if_needed=True)

                        print(
                            "Moving original (in tempfs) file to " + target_dir
                        )
                        copied.move_to(target_fs, new_name_if_needed=True)

                        print("Deleteing original file from " + step.path)
                        wrapper.trash(for_real=True)
