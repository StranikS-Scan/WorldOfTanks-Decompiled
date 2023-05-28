# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/achievements20_requester.py
import typing
import BigWorld
from adisp import adisp_async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IAchievements20Requester
from constants import AchievementsLayoutStates
if typing.TYPE_CHECKING:
    from typing import List

class Achievements20Requester(AbstractSyncDataRequester, IAchievements20Requester):

    def getLayout(self):
        return self.getCacheValue('achievementsLayout', {}).get('layout', [])

    def getLayoutState(self):
        return self.getCacheValue('achievementsLayout', {}).get('state', AchievementsLayoutStates.AUTO)

    def getAchievementBitmask(self):
        return self.getCacheValue('achievementsLayout', {}).get('achievementBitmask', AchievementsLayoutStates.AUTO)

    def getLayoutLength(self):
        return self.getCacheValue('achievementsLayout', {}).get('layoutLength', 0)

    def _preprocessValidData(self, data):
        return dict(data.get('achievements20', {}))

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().achievements20.getCache(lambda resID, value: self._response(resID, value, callback))
