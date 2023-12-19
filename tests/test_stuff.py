from fs.osfs import OSFS

from hello import hello_f


def test_stuff():
    print(hello_f())
    print(OSFS(".").listdir(path="."))
