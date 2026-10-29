import pytest
from PIL import Image

from food11.data import CLASSES, category_from_filename, resize_image


def test_categories():
    assert category_from_filename("0_12.jpg") == "Bread"
    assert category_from_filename("10_3.jpg") == "Vegetable-Fruit"
    assert len(CLASSES) == 11
    for filename in ("bad.jpg", "-1_2.jpg", "11_1.jpg"):
        with pytest.raises(ValueError):
            category_from_filename(filename)


def test_resize():
    image = resize_image(Image.new("L", (512, 384)))
    assert image.mode == "RGB"
    assert image.size == (128, 128)
