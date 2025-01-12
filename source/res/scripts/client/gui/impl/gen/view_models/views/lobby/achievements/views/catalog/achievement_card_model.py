# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/catalog/achievement_card_model.py
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.details_model import DetailsModel

class AchievementCardModel(DetailsModel):
    __slots__ = ()

    def __init__(self, properties=26, commands=0):
        super(AchievementCardModel, self).__init__(properties=properties, commands=commands)

    def getIsProgressive(self):
        return self._getBool(18)

    def setIsProgressive(self, value):
        self._setBool(18, value)

    def getIsSingleStage(self):
        return self._getBool(19)

    def setIsSingleStage(self, value):
        self._setBool(19, value)

    def getSpecificItemName(self):
        return self._getString(20)

    def setSpecificItemName(self, value):
        self._setString(20, value)

    def getSpecificItemIconName(self):
        return self._getString(21)

    def setSpecificItemIconName(self, value):
        self._setString(21, value)

    def getSpecificItemLevel(self):
        return self._getNumber(22)

    def setSpecificItemLevel(self, value):
        self._setNumber(22, value)

    def getSpecificItemId(self):
        return self._getNumber(23)

    def setSpecificItemId(self, value):
        self._setNumber(23, value)

    def getNewItemsCount(self):
        return self._getNumber(24)

    def setNewItemsCount(self, value):
        self._setNumber(24, value)

    def getIsResearchable(self):
        return self._getBool(25)

    def setIsResearchable(self, value):
        self._setBool(25, value)

    def _initialize(self):
        super(AchievementCardModel, self)._initialize()
        self._addBoolProperty('isProgressive', True)
        self._addBoolProperty('isSingleStage', False)
        self._addStringProperty('specificItemName', '')
        self._addStringProperty('specificItemIconName', '')
        self._addNumberProperty('specificItemLevel', 0)
        self._addNumberProperty('specificItemId', 0)
        self._addNumberProperty('newItemsCount', 0)
        self._addBoolProperty('isResearchable', False)
