# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_reserves/converted_booster_list.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_reserves.converted_booster_list_item import ConvertedBoosterListItem

class ConvertedBoosterList(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ConvertedBoosterList, self).__init__(properties=properties, commands=commands)

    def getOldBoosters(self):
        return self._getArray(0)

    def setOldBoosters(self, value):
        self._setArray(0, value)

    @staticmethod
    def getOldBoostersType():
        return ConvertedBoosterListItem

    def getNewBoosters(self):
        return self._getArray(1)

    def setNewBoosters(self, value):
        self._setArray(1, value)

    @staticmethod
    def getNewBoostersType():
        return ConvertedBoosterListItem

    def _initialize(self):
        super(ConvertedBoosterList, self)._initialize()
        self._addArrayProperty('oldBoosters', Array())
        self._addArrayProperty('newBoosters', Array())
