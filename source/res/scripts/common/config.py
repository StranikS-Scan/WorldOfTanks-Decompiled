# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/config.py
from __future__ import absolute_import
from future.utils import lmap, viewitems

class Config(object):

    def __init__(self, **kwargs):
        lmap(lambda item: setattr(self, *item), viewitems(kwargs))

    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError
