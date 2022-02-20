# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/__init__.py
import typing
from adisp import process, async
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from lunar_ny.lunar_ny_charm import LunarNYCharm
    from lunar_ny.lunar_ny_progression_config import LunarNYProgressionConfig
    from lunar_ny.lunar_ny_progression_config import LunarNYProgressionLevel
    from lunar_ny.lunar_ny_constants import EnvelopeTypes
    from lunar_ny.sub_controllers.gift_system import LunarNYGiftSystemSubController
    from lunar_ny.sub_controllers.received_envelopes import ReceivedEnvelopesSubController
    from lunar_ny.sub_controllers.charms import CharmsSubController
    from lunar_ny.sub_controllers.progression import ProgressionSubController

class ILunarNYController(IGameController):
    onStatusChange = None

    @property
    def giftSystem(self):
        raise NotImplementedError

    @property
    def receivedEnvelopes(self):
        raise NotImplementedError

    @property
    def charms(self):
        raise NotImplementedError

    @property
    def progression(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isGiftSystemEventActive(self):
        raise NotImplementedError

    def getEventActiveTime(self):
        raise NotImplementedError

    def getAboutEnvelopesUrl(self):
        raise NotImplementedError

    def getEventRulesURL(self):
        raise NotImplementedError

    def getInfoVideoURL(self):
        raise NotImplementedError

    @async
    @process
    def getEnvelopesExternalShopURL(self, callback=None):
        raise NotImplementedError

    def getEnvelopePurchasesLimit(self):
        raise NotImplementedError

    def getMinRareCharmProbability(self):
        raise NotImplementedError
