# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/metaclass.py


class Metaclass(type):

    def __init__(cls, name, bases, attrs):
        mro = list(cls.__mro__)
        mro.pop(0)
        for base in reversed(mro):
            init = base.__dict__.get('__init_subclass__', None)
            if init:
                init.__func__(cls, name, bases, attrs)

        return
