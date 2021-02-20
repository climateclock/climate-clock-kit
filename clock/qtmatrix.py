
from __future__ import annotations

from ctypes import c_ubyte
from multiprocessing import Array, Process

import numpy as np
from PIL import Image
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel


def gui(pixbuf, w, h, fps=30):
    '''
    Simple image display process
    '''
    def redraw():
        widget.setPixmap(QPixmap(image).scaled(2 * w, 2 * h))

    app = QApplication([])

    widget = QLabel(parent=None)
    widget.resize(2 * w, 2 * h)
    widget.show()

    image = QImage(pixbuf, w, h, QImage.Format_RGBA8888)

    timer = QTimer()
    timer.timeout.connect(redraw)
    timer.start(1000 // fps)

    app.exec()


class RGBMatrixOptions(object): ...


class RGBMatrix(object):
    def __init__(self, options):
        self.options = options
        w = self.w = options.cols * options.chain_length
        h = self.h = options.rows

        # Create a pixel buffer shareable between this and the GUI process
        self.pixbuf = np.ctypeslib.as_array(Array(c_ubyte, w * h * 4).get_obj()).reshape(h, w, 4)

        # Launch the GUI process
        Process(target=gui, args=(self.pixbuf, w, h)).start()

        #i = Image.open('rainbow.png')
        #i.thumbnail((w, h), Image.ANTIALIAS)
        #self.SetImage(i)

    def SetImage(self, image):
        self.pixbuf[:] = image.convert('RGBA')

