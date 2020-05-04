# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/radar_ctrl.py
import logging
import BigWorld
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IRadarController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class IRadarListener(object):

    def radarInfoReceived(self, duration, positions):
        pass


class RadarController(ViewComponentsController, IRadarController):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RadarController, self).__init__()
        self.__dynamicViews = []

    def getControllerID(self):
        return BATTLE_CTRL_ID.RADAR_CTRL

    def startControl(self, *args):
        avatar = BigWorld.player()
        arena = avatar.arena
        if arena is not None:
            arena.onRadarInfoReceived += self.__onRadarInfoReceived
        return

    def stopControl(self):
        avatar = BigWorld.player()
        arena = avatar.arena
        if arena is not None:
            arena.onRadarInfoReceived -= self.__onRadarInfoReceived
        self.clearViewComponents()
        return

    def setViewComponents(self, *components):
        self._viewComponents = list(components)

    def clearViewComponents(self):
        super(RadarController, self).clearViewComponents()
        self.__dynamicViews = []

    def addRuntimeView(self, view):
        if view in self.__dynamicViews:
            _logger.warning('View already added - %s', view)
        else:
            self.__dynamicViews.append(view)

    def removeRuntimeView(self, view):
        if view in self.__dynamicViews:
            self.__dynamicViews.remove(view)
        else:
            _logger.warning('View has not been found - %s', view)

    def __onRadarInfoReceived(self, duration, positions):
        for listener in self._viewComponents + self.__dynamicViews:
            listener.radarInfoReceived(duration, positions)
