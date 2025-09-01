# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/daily/daily_mission_model.py
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.common.mission_base_model import MissionBaseModel

class DailyMissionModel(MissionBaseModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(DailyMissionModel, self).__init__(properties=properties, commands=commands)

    def getIsRerollEnabled(self):
        return self._getBool(10)

    def setIsRerollEnabled(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(DailyMissionModel, self)._initialize()
        self._addBoolProperty('isRerollEnabled', False)
