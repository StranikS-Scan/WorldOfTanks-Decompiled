# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/gift_system/hubs/lunar_ny_keeper.py
from gui.gift_system.constants import GiftMessageType
from gui.gift_system.hubs.base.relations_keeper import GiftEventBaseKeeper
from helpers import dependency
from lunar_ny import ILunarNYController
from gui.gift_system.wrappers import ifMessagesAllowed
_SENT_PERIOD_LIMIT_KEY = 'secret_santa_lifetime'
_DEFAULT_SECRET_SANTA_SENT_PERIOD_LIMIT = 84600

class GiftLunarNYKeeper(GiftEventBaseKeeper):
    __slots__ = ('__sentPeriodLimit',)
    __lunarNYController = dependency.descriptor(ILunarNYController)

    def __init__(self, eventSettings, clearCallback):
        super(GiftLunarNYKeeper, self).__init__(eventSettings, clearCallback)
        self.__sentPeriodLimit = _DEFAULT_SECRET_SANTA_SENT_PERIOD_LIMIT

    def __repr__(self):
        return 'GiftLunarNYKeeper id={}'.format(self._settings.eventID)

    def getSentPeriodLimit(self):
        return self.__sentPeriodLimit

    @ifMessagesAllowed(GiftMessageType.LIMITS, useQueue=False)
    def _processWebState(self, webState):
        super(GiftLunarNYKeeper, self)._processWebState(webState)
        commonData = webState.common
        self.__sentPeriodLimit = commonData.get(_SENT_PERIOD_LIMIT_KEY, _DEFAULT_SECRET_SANTA_SENT_PERIOD_LIMIT)
