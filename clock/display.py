
from __future__ import annotations

import abc
import re

import PIL

from utils import log


class Display(abc.ABC):
    '''
    Abstract base for clock display classes

    Concrete classes can be instantiated by passing a device name and
    arguments for `__init__` to the the `create` factory method, e.g.:

        >>> Display.create('portable_pi', settings)

    Subclasses should be named for the device they support, e.g. `PortablePi`
    for the `portable_pi` device.
    '''
    device_classes = {}
    w: 'Display width in pixels'
    h: 'Display height in pixels'

    def __init_subclass__(cls, **kw) -> None:
        '''
        Keeps track of subclasses for instantiation by the `create` factory
        method. Subclass' PascalCased names will be converted to snake_case as
        the device_name attribute.
        '''
        super().__init_subclass__(**kw)
        cls.device_name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        cls.device_classes[cls.device_name] = cls

    @classmethod
    def create(cls, device_name: str, *a, **kw) -> Display:
        '''
        Factory method for instantiating a Display subclass for the given
        device name. Device names are specified in snake_case.
        '''
        return cls.device_classes[device_name](*a, **kw)

    #@abc.abstractmethod
    def get_layouts(self, n: int):
        '''
        Q?s:    * Does this return PIL images?
                * Does it return coordinates
        '''

    @abc.abstractmethod
    def set_image(self, image: PIL.Image) -> None:
        '''
        Replace the entire display with the provided image.
        '''


class Generic(Display):
    def __init__(self, settings: dict, done :asyncio.Future=None, *a, **kw):
        '''
        Launch a Tkinter process to display a clock for testing
        '''
        # Exfiltrate internal imports
        global PhotoImage, np, tk

        import multiprocessing
        import tkinter as tk
        from ctypes import c_ubyte

        import numpy as np
        from PIL.ImageTk import PhotoImage

        self.scale = settings['scale']
        self.w = settings['width']
        self.h = settings['height']
        self.done = done

        self.wSc = self.w * self.scale
        self.hSc = self.h * self.scale

        # Create a synchronized array to share with a GUI process
        self.pixel_buffer = np.ctypeslib.as_array(
            multiprocessing.Array(c_ubyte, self.hSc * self.wSc * 4).get_obj()
        ).reshape(self.hSc, self.wSc, 4)

        # Create a communication Queue and launch the GUI process
        self.Q = multiprocessing.Queue()
        multiprocessing.Process(target=self.GUI).start()

    def set_image(self, image):
        # Assume any message from the GUI means "done"
        if not self.Q.empty():
            self.done.set_result(True)

        # Scale and make pixel-y before writing to the pixel buffer
        pixels = np.asarray(image.convert('RGBA')).repeat(self.scale, axis=0).repeat(self.scale, axis=1)
        pixels[::self.scale, :, :] = (0,0,0,255)
        pixels[:, ::self.scale, :] = (0,0,0,255)
        self.pixel_buffer[:] = pixels

    def GUI(self):
        '''
        Be aware these GUI_* methods run in a separate process from the rest
        of the code, and can only interact with each other or the
        multiprocessing.Queue object.
        '''
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=self.wSc, height=self.hSc)
        self.canvas.bind('<Button-1>', lambda e: [self.Q.put(True), self.root.destroy()])
        self.canvas.pack()
        self.GUI_update()
        self.root.mainloop()
        self.Q.put(True)

    def GUI_update(self, fps: int=60):
        '''
        Update the GUI and schedule itself. No framerate synchronization is 
        performed, so don't expect buttery smooth animation.
        '''
        self.image = PhotoImage(image=PIL.Image.fromarray(self.pixel_buffer))
        self.canvas.create_image(self.wSc, self.hSc, anchor="se", image=self.image)
        self.root.after(int(1000 / fps), self.GUI_update)


class PortablePi(Display): 
    '''
    Display for the portable_pi using the Raspberry Pi RGBMatrix library:
    https://github.com/hzeller/rpi-rgb-led-matrix
    '''
    def __init__(self, settings: dict, *a, **kw):
        # Exfiltrate internal imports
        global rgbmatrix
        import rgbmatrix

        options = rgbmatrix.RGBMatrixOptions()
        for k, v in settings.items():
            try:
                setattr(options, k, v)
            except AttributeError:
                log(f'Ignoring: {k} = {v}')
        self.matrix = rgbmatrix.RGBMatrix(options=options)

        self.w = settings['cols'] * settings['chain_length']
        self.h = settings['rows']

    @property
    def brightness(self) -> int:
        return self.matrix.brightness

    @brightness.setter
    def brightness(self, value: int=100):
        self.matrix.brightness = value

    def set_image(self, image):
        self.matrix.SetImage(image)


