import doctest

import dropboxer.tasks
from dropboxer.tasks import drop_ext


def test_drop_ext():
    filename = 'image.jpeg'
    filename = drop_ext(filename, ('jpg', 'jpeg'))
    assert filename == 'image'

def test_drop_ext_upper_ext():
    filename = 'IMAGE.JPG'
    filename = drop_ext(filename, ('jpg', 'jpeg'))
    assert filename == 'IMAGE'


def test_drop_ext_no_ext():
    filename = 'README'
    filename = drop_ext(filename, ('jpg', 'jpeg'))
    assert filename == 'README'


def test_drop_ext_unknown_ext():
    filename = 'hello.world'
    filename = drop_ext(filename, ('jpg', 'jpeg'))
    assert filename == 'hello.world'


def test_doctests():
    results = doctest.testmod(dropboxer.tasks)
    assert results.failed == 0
