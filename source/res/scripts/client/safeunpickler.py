# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SafeUnpickler.py
from __future__ import absolute_import
import sys
import copy
from io import BytesIO
from future.moves import pickle

class SafeUnpickler(object):
    PICKLE_SAFE = {'__builtin__': {'object',
                     'set',
                     'frozenset',
                     'list',
                     'tuple'},
     'datetime': {'datetime'},
     '_BWp': {'Array', 'FixedDict'},
     'Math': {'Vector2', 'Vector3'}}

    def __init__(self):
        import items.components.shared_components as sc
        sc.MechanicsParams.createMechanicsParamsOrigin = copy.deepcopy

    @classmethod
    def find_class(cls, module, name):
        if module not in cls.PICKLE_SAFE:
            raise pickle.UnpicklingError('Attempting to unpickle unsafe module %s' % module)
        __import__(module)
        mod = sys.modules[module]
        classesSet = cls.PICKLE_SAFE[module]
        if name not in classesSet:
            raise pickle.UnpicklingError('Attempting to unpickle unsafe class %s' % name)
        klass = getattr(mod, name)
        return klass

    @classmethod
    def loads(cls, pickle_string):
        pickle_obj = pickle.Unpickler(BytesIO(pickle_string))
        pickle_obj.find_global = cls.find_class
        return pickle_obj.load()
