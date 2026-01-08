# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/battle/quests_tab_model.py
from frameworks.wulf import Array
from frontline.gui.impl.gen.view_models.views.battle.fl_progression_model import FlProgressionModel
from frontline.gui.impl.gen.view_models.views.battle.quests_model import QuestsModel

class QuestsTabModel(QuestsModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(QuestsTabModel, self).__init__(properties=properties, commands=commands)

    def getSectorName(self):
        return self._getString(9)

    def setSectorName(self, value):
        self._setString(9, value)

    def getIsClientReady(self):
        return self._getBool(10)

    def setIsClientReady(self, value):
        self._setBool(10, value)

    def getIsLastLine(self):
        return self._getBool(11)

    def setIsLastLine(self, value):
        self._setBool(11, value)

    def getProgressions(self):
        return self._getArray(12)

    def setProgressions(self, value):
        self._setArray(12, value)

    @staticmethod
    def getProgressionsType():
        return FlProgressionModel

    def _initialize(self):
        super(QuestsTabModel, self)._initialize()
        self._addStringProperty('sectorName', '')
        self._addBoolProperty('isClientReady', False)
        self._addBoolProperty('isLastLine', False)
        self._addArrayProperty('progressions', Array())
