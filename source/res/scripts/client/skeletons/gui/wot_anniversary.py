# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/wot_anniversary.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from helpers.server_settings import WotAnniversaryConfig
    from gui.impl.lobby.wot_anniversary.bonuses_layout_manager import BonusesLayoutManager
    from gui.impl.lobby.wot_anniversary.content_loader.cache import WotAnniversaryCdnCacheMgr

class IWotAnniversaryController(IGameController):
    onSettingsChanged = None
    onNextEnvelopeArrived = None
    onStartDateReached = None
    onEndDateReached = None

    @property
    def config(self):
        raise NotImplementedError

    @property
    def cdnCacheMgr(self):
        raise NotImplementedError

    @property
    def bonusLayoutManager(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def getReleasedEnvelopCount(self):
        raise NotImplementedError

    def getAvailableEnvelops(self):
        raise NotImplementedError

    def getDayTokenCount(self):
        raise NotImplementedError

    def getProgressionTokenCount(self):
        raise NotImplementedError
