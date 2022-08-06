# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pickle_intern.py
import pickle
from copy import deepcopy
from StringIO import StringIO
STR_LEN_FOR_INTERN = 20

class UnpicklerWithIntern(pickle.Unpickler, object):

    def __init__(self, file):
        super(UnpicklerWithIntern, self).__init__(file)
        self.dispatch = deepcopy(self.dispatch)
        self.dispatch[pickle.SHORT_BINSTRING] = UnpicklerWithIntern.load_short_binstring

    def load_short_binstring(self):
        str_len = ord(self.read(1))
        obj = self.read(str_len)
        if len(obj) <= STR_LEN_FOR_INTERN:
            obj = intern(obj)
        self.append(obj)

    @classmethod
    def loads(cls, data):
        unpickler = cls(StringIO(data))
        return unpickler.load()
