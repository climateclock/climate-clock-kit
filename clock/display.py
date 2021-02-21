#!/usr/bin/env python

from __future__ import annotations
import re
import tkinter as tk
from abc import ABC, abstractmethod

import rgbmatrix
import PIL

from utils import log


class Display(ABC):
    '''
    Abstract base for all clock display classes

    Subclasses should be named for the device they support, e.g. `PortablePi`
    for the `portable_pi` device. Concrete classes can be instantiated by
    passing a device name and any arguments  for `__init__` to the the 
    `create` factory method.
    '''
    device_classes = {}

    def __init__(self, w: int, h: int, done: asyncio.Future, *a, **kw) -> None:
        self.w = w
        self.h = h
        self.done = done

    def __init_subclass__(cls, **kw) -> None:
        '''
        Keep track of subclasses for instantiation by the factory method.
        The PascalCase subclass name will be converted to snake_case as the
        device_name attribute.
        '''
        super().__init_subclass__(**kw)
        cls.device_name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        cls.device_classes[cls.device_name] = cls

    @classmethod
    def create(cls, device_name: str, *a, **kw) -> Display:
        '''
        Factory method for instantiating a Display subclass for the given
        device name.
        '''
        return cls.device_classes[device_name](*a, **kw)

    @abstractmethod
    def draw(self):
        '''
        '''




class PortablePi(Display): 
    '''
    Display for the portable_pi clock based on the RGBMatrix library
    '''
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        options = rgbmatrix.RGBMatrixOptions()
        for k, v in kw['options'].items():
            try: setattr(options, k, v)
            except AttributeError: log(f'Ignoring: {k} = {v}')
        self.matrix = rgbmatrix.RGBMatrix(options=options)

    @property
    def brightness(self):
        return self.matrix.brightness

    @brightness.setter
    def brightness(self, value):
        self.matrix.brightness = value

    def draw(self): ...



class Generic(Display): 
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        print('generic', self.w, self.h)

    def draw(self): ...


'''
class TkinterDisplay(ClockDisplay):
    def __init__(self, *a, **kw):
        print(':::__init__ (SUB)', a)
        config = kw.pop('config')
        super().__init__(*a, **kw)

    def gui_process(self):
        ...
        

'''
