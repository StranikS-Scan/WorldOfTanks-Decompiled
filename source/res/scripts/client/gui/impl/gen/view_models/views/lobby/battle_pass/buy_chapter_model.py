# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/buy_chapter_model.py
from frameworks.wulf import ViewModel

class BuyChapterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BuyChapterModel, self).__init__(properties=properties, commands=commands)

    def getChapterID(self):
        return self._getNumber(0)

    def setChapterID(self, value):
        self._setNumber(0, value)

    def getHasStarterPack(self):
        return self._getBool(1)

    def setHasStarterPack(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(BuyChapterModel, self)._initialize()
        self._addNumberProperty('chapterID', 0)
        self._addBoolProperty('hasStarterPack', False)
