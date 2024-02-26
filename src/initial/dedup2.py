# from pprint import pprint

import os

import fs

from pyfsobj import FileWrapper

fss = {}


# Horrible, need to keep the same base !
def get_sub_fs(base, path):
    if path in fss:
        return fss[path]
    else:
        fss[path] = base.opendir(path) if base.exists(path) else None
        return fss[path]


if __name__ == "__main__":
    md5d = {}

    print("Open filesystem...")
    main_fs = fs.open_fs("/Volumes/archives")
    print("...open md5s...")
    with main_fs.open("all_md5.log", "r") as md5s:
        print("...reading md5s...")
        lines = md5s.readlines()
        lines = [lin for lin in lines if "@eaDir" not in lin]
        print("...Done")
        for line in lines[:-1]:
            md5 = line[:32]
            path = line[34:].strip()
            if md5 in md5d:
                print(f"Duplicate: {path} and {md5d[md5]}")
                lis = md5d[md5]
            else:
                lis = []
            if path not in lis:
                lis.append(path)
            md5d[md5] = lis

    duplicates = {k: v for k, v in md5d.items() if len(v) > 1}

    print("Open trash filesystem...")
    trashfs = main_fs.opendir("trash")
    print("...Done")

    print("Open #recyle filesystem...")
    recylcefs = main_fs.opendir("#recycle")
    print("...Done")

    nb = len(duplicates)
    n = 0

    for k, v in duplicates.items():
        n = n + 1

        print()
        print(f"{n/nb*100:.2f}% ({n}/{nb})")
        print(f"Checking {k}...")
        # For each list of duplicates

        pathes = list(set(v))
        pathes.sort(
            key=lambda x: (
                x.startswith("target"),
                x.startswith("Archive"),
                0 - len(x),
            ),
            reverse=True,
        )
        pass
        noteadir = [os.path.split(p) for p in pathes if "eaDir" not in p]
        print(f"ex: ...{noteadir[0]}...")
        pass
        _fileWrappers = []
        for pat in noteadir:
            subfs = get_sub_fs(main_fs, pat[0])
            if subfs is None:
                print(f"Missing {pat[0]}")
                continue
            _fileWrappers.append(
                FileWrapper(
                    subfs,
                    pat[1],
                    check=False,
                )
            )
        pass
        fileWrappers = [fw for fw in _fileWrappers if fw.exists()]
        pass
        if len(fileWrappers) > 1:
            inTrash = [
                w
                for w in fileWrappers
                if w.filesystem.getsyspath(".").endswith("trash")
            ]

            notInTrash = [
                w
                for w in fileWrappers
                if not w.filesystem.getsyspath(".").endswith("trash")
            ]

            if inTrash:
                if notInTrash:
                    li = inTrash
                    print(f"keeping {notInTrash[0]}")
                else:
                    li = inTrash[1:]
                    print(f"keeping {inTrash[0]}")
                for fw in li:
                    print(f"#recycling {fw}")
                    fw.trash(trash_filesystem=recylcefs)

            fileWrappers = None

            if len(notInTrash) > 1:
                length = notInTrash[0].size
                core0, ext0 = os.path.splitext(notInTrash[0].filename)
                core0 = (
                    core0.replace("(0)", "")
                    .replace("(1)", "")
                    .replace("(2)", "")
                    .replace("(3)", "")
                    .replace("(4)", "")
                    .replace("(5)", "")
                    .replace("(6)", "")
                    .replace("(7)", "")
                    .replace("(8)", "")
                    .replace("(9)", "")
                    .replace("é", "e")
                    .replace("è", "e")
                    .replace("â", "a")
                    .replace("å", "a")
                    .replace("ö", "o")
                    .replace("ä", "a")
                    .replace("à", "a")
                    .replace("-2", "")
                    .strip()
                    .lower()
                )
                i = 0
                print("Keeping ", notInTrash[0])
                for fw in notInTrash[1:]:
                    if fw.size != length:
                        print(f"Size mismatch: {fw}")
                        continue

                    if fw.fullpath == notInTrash[0].fullpath:
                        print(f"Same path: {fw}")
                        continue

                    core, ext = os.path.splitext(fw.filename)
                    core = (
                        core.replace("(0)", "")
                        .replace("(1)", "")
                        .replace("(2)", "")
                        .replace("(3)", "")
                        .replace("å", "a")
                        .replace("ö", "o")
                        .replace("ä", "a")
                        .replace("(4)", "")
                        .replace("(5)", "")
                        .replace("(6)", "")
                        .replace("(7)", "")
                        .replace("(8)", "")
                        .replace("(9)", "")
                        .replace("é", "e")
                        .replace("è", "e")
                        .replace("â", "a")
                        .replace("à", "a")
                        .replace("Ö", "o")
                        .strip()
                        .lower()
                    )

                    if (
                        (core0 in core)
                        or (core in core0)
                        or "fullsizeoutput" in core
                    ) and (ext.replace("jpeg", "jpg").lower() == ext0.lower()):
                        if i == 0:
                            print(f"Trashing {fw}")
                            fw.trash(trash_filesystem=trashfs)
                        else:
                            print(f"Recycling {fw}")
                            fw.trash(trash_filesystem=recylcefs)
                    else:
                        print(f"Names differ, keeping {fw}")
                    i = i + 1
