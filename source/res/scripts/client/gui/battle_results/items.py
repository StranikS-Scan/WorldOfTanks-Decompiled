# Embedded file name: scripts/client/gui/battle_results/items.py
from functools import partial
from gui.shared.utils import mapTextureToTheMemory

class TeamInfo(object):

    def __init__(self, name = '', emblemRq = None):
        self.__name = name
        self.__emblemRq = emblemRq or (lambda cb: cb(None))

    def getUserName(self):
        return self.__name

    def requestEmblemID(self, callback):

        def _cbWrapper(cb, emblem):
            if emblem is not None:
                cb(mapTextureToTheMemory(emblem))
            else:
                cb(None)
            return

        self.__emblemRq(partial(_cbWrapper, callback))
