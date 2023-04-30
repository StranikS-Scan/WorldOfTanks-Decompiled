# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/premium_mission_model.py
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class PremiumMissionModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(PremiumMissionModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(11)

    def setIcon(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(PremiumMissionModel, self)._initialize()
        self._addStringProperty('icon', '')
