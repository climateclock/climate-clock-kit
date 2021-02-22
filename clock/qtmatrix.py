
from __future__ import annotations

from ctypes import c_ubyte
from multiprocessing import Array, Process, Queue

import numpy as np
from PIL import Image
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel


Q = Queue()


def gui(pixbuf, w, h, fps=60):
    '''
    Simple image display process
    '''
    def quit(e):
        Q.put_nowait(1)
        app.exit()

    def redraw():
        widget.setPixmap(QPixmap(image))

    app = QApplication([])

    widget = QLabel(parent=None)
    widget.resize(w, h)
    widget.show()
    widget.mouseReleaseEvent = quit

    image = QImage(pixbuf, w, h, QImage.Format_RGBA8888)

    timer = QTimer()
    timer.timeout.connect(redraw)
    timer.start(1000 // fps)

    app.exec()


class RGBMatrix(object):
    def __init__(self, options):
        self.options = options
        w = self.w = options.cols * options.chain_length
        h = self.h = options.rows
        w *= 4
        h *= 4

        # Create a pixel buffer shareable between this and the GUI process
        self.pixbuf = np.ctypeslib.as_array(Array(c_ubyte, w * h * 4).get_obj()).reshape(h, w, 4)

        # Launch the GUI process
        self.p = Process(target=gui, args=(self.pixbuf, w, h))
        self.p.start()


    def SetImage(self, image) -> bool:
        if Q.empty():
            #pixels = np.kron(image.convert('RGBA'), np.ones((4, 4, 1)))
            pixels = np.asarray(image.convert('RGBA')).repeat(4, axis=0).repeat(4, axis=1)
            pixels[::4,:,:] = (0,0,0,255)
            pixels[:,::4,:] = (0,0,0,255)
            self.pixbuf[:] = pixels
            return True

