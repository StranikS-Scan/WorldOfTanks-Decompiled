# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/premium_daily/premium_daily_mission_model.py
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.common.mission_base_model import MissionBaseModel

class PremiumDailyMissionModel(MissionBaseModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(PremiumDailyMissionModel, self).__init__(properties=properties, commands=commands)

    def getIsLocked(self):
        return self._getBool(10)

    def setIsLocked(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(PremiumDailyMissionModel, self)._initialize()
        self._addBoolProperty('isLocked', False)
