# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_story_point_controller.py
from __future__ import absolute_import
import typing
import Event
from helpers import dependency
from gui.prb_control.entities.listener import IGlobalListener
from gui.ClientUpdateManager import g_clientUpdateManager
from skeletons.gui.server_events import IEventsCache
from last_stand.skeletons.ls_story_point_controller import ILSStoryPointController
from last_stand.skeletons.ls_controller import ILSController
from last_stand_common.last_stand_constants import StoryPointsSettings
from last_stand.gui.ls_gui_constants import FUNCTIONAL_FLAG
if typing.TYPE_CHECKING:
    from gui.shared.events import GUICommonEvent

class LSStoryPointController(ILSStoryPointController, IGlobalListener):
    eventsCache = dependency.descriptor(IEventsCache)
    lsCtrl = dependency.descriptor(ILSController)
    FIRST_STORY_POINT_INDEX = 1

    def __init__(self):
        super(LSStoryPointController, self).__init__()
        self.onStoryPointStatusUpdated = Event.Event()
        self._storyPointsIDs = []
        self._selectedStoryPointID = None
        return

    def init(self):
        super(LSStoryPointController, self).init()
        g_clientUpdateManager.addCallbacks({'tokens': self.__handleTokensUpdate})

    def fini(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.onStoryPointStatusUpdated.clear()
        self._storyPointsIDs = []
        self._selectedStoryPointID = None
        return

    def onDisconnected(self):
        super(LSStoryPointController, self).onDisconnected()
        self.stopGlobalListening()

    def onAvatarBecomePlayer(self):
        super(LSStoryPointController, self).onAvatarBecomePlayer()
        self.stopGlobalListening()

    def onLobbyStarted(self, ctx):
        super(LSStoryPointController, self).onLobbyStarted(ctx)
        self._selectedStoryPointID = None
        self._initStoryPoints()
        return

    def onLobbyInited(self, event):
        self.startGlobalListening()

    def onPrbEntitySwitched(self):
        if self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.LAST_STAND:
            return
        else:
            self._selectedStoryPointID = None
            return

    @property
    def selectedStoryPointID(self):
        return self._selectedStoryPointID if self._selectedStoryPointID in self._storyPointsIDs else None

    @selectedStoryPointID.setter
    def selectedStoryPointID(self, storyPointID):
        if storyPointID is None or self.isStoryPointReceived(storyPointID):
            self._selectedStoryPointID = storyPointID
        return

    @property
    def storyPoints(self):
        return self._storyPointsIDs

    def isStoryPointReceived(self, storyPointID):
        return self.eventsCache.questsProgress.getTokenCount(storyPointID) > 0 or storyPointID == self.getStoryPointIDByIndex(self.FIRST_STORY_POINT_INDEX)

    def getStoryPointIDByIndex(self, index):
        return '{prefix}{index}'.format(prefix=StoryPointsSettings.TOKEN_PREFIX, index=index)

    def getIndex(self, storyPointID):
        _, index = storyPointID.split(':')
        return int(index)

    def getStoryPointsCount(self):
        return len(self._storyPointsIDs)

    def _initStoryPoints(self):
        self._storyPointsIDs = self.lsCtrl.getModeSettings().storyPointsList

    def __handleTokensUpdate(self, diff):
        for token in diff:
            if token.startswith(StoryPointsSettings.TOKEN_PREFIX):
                self.onStoryPointStatusUpdated(token)
