# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_camp_capture_progress_bar.py
import logging
from helpers import time_utils
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.TeamBasesPanelMeta import TeamBasesPanelMeta
from portal.sounds.sound_constants import CampSound
from portal.sounds.sound_helpers import play2DSound
from portal_common.portal_constants import PORTAL_GAME_PARAMS_KEY
from portal.gui.portal_gui_constants import CAMP_ORDER_INDEX
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from portal_common_cgf.portal_helpers import isLowPreset
from PortalBattleStateComponent import PortalBattleStateComponent
_logger = logging.getLogger(__name__)

class PortalCampCamptureProgressBar(TeamBasesPanelMeta):
    _COLOR = 'eventPurple'
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(PortalCampCamptureProgressBar, self).__init__()
        self.__activeList = []
        PortalBattleStateComponent.onCampCapturing += self.__onCapturing
        PortalBattleStateComponent.onCampStopCapturing += self.__onStopCapturing
        PortalBattleStateComponent.onCampCaptured += self.__onStopCapturing
        self.isLowPreset = isLowPreset()

    def _dispose(self):
        self.__activeList = None
        PortalBattleStateComponent.onCampCapturing -= self.__onCapturing
        PortalBattleStateComponent.onCampStopCapturing -= self.__onStopCapturing
        PortalBattleStateComponent.onCampCaptured -= self.__onStopCapturing
        super(PortalCampCamptureProgressBar, self)._dispose()
        return

    def __getPortalConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings()[PORTAL_GAME_PARAMS_KEY]

    def __getCampIndex(self, campName):
        frontierInfos = self.__getPortalConfig()['scenario']['campsSettings']['frontiers']
        for frontier, frontierInfo in frontierInfos.iteritems():
            if campName in frontierInfo['camps']:
                return CAMP_ORDER_INDEX[frontier]

    def __onCapturing(self, info):
        index = self.__getCampIndex(info['name'])
        if index < 0:
            _logger.error('Cannot find index for camp %s', info)
        text = backport.text(R.strings.portal_battle.camp.capturing(), percent=info['progress'])
        timeText = time_utils.getTimeLeftFormat(info['timeLeft'])
        invadersText = str(info['invaderCount'])
        if index not in self.__activeList:
            self.as_addS(index, 0, self._COLOR, text, 0, timeText, invadersText, self.isLowPreset)
            self.__activeList.append(index)
            play2DSound(CampSound.CAPTURE_START)
        self.as_updateCaptureDataS(index, info['progress'], 1, timeText, invadersText, text, self._COLOR)

    def __onStopCapturing(self, campGO):
        index = self.__getCampIndex(campGO.name)
        if index < 0:
            _logger.error('Cannot find index for camp %s', campGO.name)
        if index in self.__activeList:
            self.as_updateCaptureDataS(index, 0, 0, '', '', '', self._COLOR)
            self.as_removeS(index)
            self.__activeList.remove(index)
            play2DSound(CampSound.CAPTURE_LEAVE)
