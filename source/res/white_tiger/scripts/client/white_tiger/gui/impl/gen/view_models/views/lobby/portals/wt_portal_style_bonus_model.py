# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portals/wt_portal_style_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class WtPortalStyleBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(WtPortalStyleBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsCollected(self):
        return self._getBool(8)

    def setIsCollected(self, value):
        self._setBool(8, value)

    def getIsCustom(self):
        return self._getBool(9)

    def setIsCustom(self, value):
        self._setBool(9, value)

    def getName(self):
        return self._getString(10)

    def setName(self, value):
        self._setString(10, value)

    def getLabel(self):
        return self._getString(11)

    def setLabel(self, value):
        self._setString(11, value)

    def getStyleProgressionLvl(self):
        return self._getNumber(12)

    def setStyleProgressionLvl(self, value):
        self._setNumber(12, value)

    def getLockStatus(self):
        return self._getBool(13)

    def setLockStatus(self, value):
        self._setBool(13, value)

    def getStyleCD(self):
        return self._getNumber(14)

    def setStyleCD(self, value):
        self._setNumber(14, value)

    def _initialize(self):
        super(WtPortalStyleBonusModel, self)._initialize()
        self._addBoolProperty('isCollected', False)
        self._addBoolProperty('isCustom', False)
        self._addStringProperty('name', '')
        self._addStringProperty('label', '')
        self._addNumberProperty('styleProgressionLvl', 0)
        self._addBoolProperty('lockStatus', False)
        self._addNumberProperty('styleCD', 0)
