# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_awards_bonus_renderer_model.py
from frameworks.wulf import ViewModel

class SeniorityAwardsBonusRendererModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SeniorityAwardsBonusRendererModel, self).__init__(properties=properties, commands=commands)

    def getLabelStr(self):
        return self._getString(0)

    def setLabelStr(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getTooltipId(self):
        return self._getString(2)

    def setTooltipId(self, value):
        self._setString(2, value)

    def getBonusName(self):
        return self._getString(3)

    def setBonusName(self, value):
        self._setString(3, value)

    def getSpecialAlias(self):
        return self._getString(4)

    def setSpecialAlias(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(SeniorityAwardsBonusRendererModel, self)._initialize()
        self._addStringProperty('labelStr', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('bonusName', '')
        self._addStringProperty('specialAlias', '')
