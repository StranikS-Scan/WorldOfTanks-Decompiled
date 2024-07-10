# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/epic_quests_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class EpicQuestsBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(EpicQuestsBonusModel, self).__init__(properties=properties, commands=commands)

    def getOverlayType(self):
        return self._getString(9)

    def setOverlayType(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(EpicQuestsBonusModel, self)._initialize()
        self._addStringProperty('overlayType', '')
