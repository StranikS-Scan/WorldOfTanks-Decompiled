# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/techtree/selected_nation.py
import nations
from CurrentVehicle import g_currentVehicle
from gui.techtree.techtree_dp import g_techTreeDP

class SelectedNation(object):
    __slots__ = ()
    __index = None

    @classmethod
    def byDefault(cls):
        if cls.__index is None:
            index = 0
            if g_currentVehicle.isPresent() and g_currentVehicle.item.nationID in g_techTreeDP.getAvailableNationsIndices():
                index = g_currentVehicle.item.nationID
            cls.__index = index
        return

    @classmethod
    def select(cls, index):
        if index in g_techTreeDP.getAvailableNationsIndices():
            cls.__index = index

    @classmethod
    def getIndex(cls):
        return cls.__index

    @classmethod
    def getName(cls):
        return nations.NAMES[cls.__index]

    @classmethod
    def clear(cls):
        cls.__index = None
        return
