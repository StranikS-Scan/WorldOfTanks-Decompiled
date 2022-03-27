# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SafeUnpickler.py
import sys
import cPickle
import StringIO

class SafeUnpickler(object):
    PICKLE_SAFE = {'__builtin__': {'object',
                     'set',
                     'frozenset',
                     'list',
                     'tuple'},
     'datetime': {'datetime'},
     '_BWp': {'Array', 'FixedDict'},
     'Math': {'Vector2', 'Vector3'}}

    @classmethod
    def find_class(cls, module, name):
        if module not in cls.PICKLE_SAFE:
            raise cPickle.UnpicklingError('Attempting to unpickle unsafe module %s' % module)
        classesSet = cls.PICKLE_SAFE[module]
        if name not in classesSet or classesSet is None:
            raise cPickle.UnpicklingError('Attempting to unpickle unsafe class %s' % name)
        __import__(module)
        return getattr(sys.modules[module], name)

    @classmethod
    def loads(cls, pickle_string):
        pickle_obj = cPickle.Unpickler(StringIO.StringIO(pickle_string))
        pickle_obj.find_global = cls.find_class
        return pickle_obj.load()
