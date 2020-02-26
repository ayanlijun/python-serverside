from PIL import Image, ImageDraw
from hashlib import md5
from io import BytesIO


class Identicon:

    GRID_SIZE = 9
    BORDER_SIZE = 10
    SQUARE_SIZE = 10

    def __init__(self, _str: str, background="#ebebeb"):
        w = h = Identicon.BORDER_SIZE * 2 + Identicon.SQUARE_SIZE * Identicon.GRID_SIZE
        self._image = Image.new("RGB", (w, h), background)
        self._draw = ImageDraw.Draw(self._image)
        self._hash = int(md5(_str.encode("utf-8")).hexdigest(), 16)
        self.__generate()
        assert isinstance(self._image, Image.Image)

    @property
    def identicon(self) -> bytes:
        byteIO = BytesIO()
        self._image.save(byteIO, format="png")
        return byteIO.getvalue()

    def __generate(self):
        color = (self._hash & 0xff, self._hash >> 8 & 0xff, self._hash >> 16 & 0xff)
        self._hash >>= 24
        square_x = square_y = 0
        for x in range(Identicon.GRID_SIZE * (Identicon.GRID_SIZE + 1) // 2):
            if self._hash & 1:
                x = Identicon.BORDER_SIZE + square_x * Identicon.SQUARE_SIZE
                y = Identicon.BORDER_SIZE + square_y * Identicon.SQUARE_SIZE
                self._draw.rectangle(
                    (x, y, x + Identicon.SQUARE_SIZE, y + Identicon.SQUARE_SIZE),
                    fill=color,
                    outline=color
                )
                x = Identicon.BORDER_SIZE + (Identicon.GRID_SIZE - 1 - square_x) * Identicon.SQUARE_SIZE
                self._draw.rectangle(
                    (x, y, x + Identicon.SQUARE_SIZE, y + Identicon.SQUARE_SIZE),
                    fill=color,
                    outline=color
                )
            self._hash >>= 1
            square_y += 1
            if square_y == Identicon.GRID_SIZE:
                square_y = 0
                square_x += 1


def generate_identicon_bytes(id: str) -> bytes:
    return Identicon(id).identicon
