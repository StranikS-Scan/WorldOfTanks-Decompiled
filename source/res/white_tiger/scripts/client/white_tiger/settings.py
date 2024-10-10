# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/settings.py
from collections import namedtuple

class WhiteTigerConfig(namedtuple('WhiteTigerConfig', ('isEnabled', 'peripheryIDs', 'primeTimes', 'seasons', 'cycleTimes', 'progression', 'specialVehicles', 'mainVehiclePrize', 'bossMainVehicle', 'stampsPerProgressionStage', 'stamp', 'mainPrizeDiscountToken', 'mainPrizeDiscountPerToken', 'mainPrizeMaxDiscountTokenCount', 'mainPrizeBoughtToken', 'hunterPortalPrice', 'bossPortalPrice', 'tankPortalPrice', 'ticketToken', 'quickBossTicketToken', 'quickHunterTicketToken', 'ticketsToDraw', 'lootBoxDailyPurchaseLimit', 'lootBoxCounterEntitlementID'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, cycleTimes={}, progression=[], specialVehicles=[], mainVehiclePrize='', bossMainVehicle='', stampsPerProgressionStage=0, stamp='', mainPrizeDiscountToken='', mainPrizeDiscountPerToken=0, mainPrizeMaxDiscountTokenCount=0, mainPrizeBoughtToken='', hunterPortalPrice=0, bossPortalPrice=0, tankPortalPrice=0, ticketToken='', quickBossTicketToken='', quickHunterTicketToken='', ticketsToDraw=0, lootBoxDailyPurchaseLimit=0, lootBoxCounterEntitlementID='')
        defaults.update(kwargs)
        return super(WhiteTigerConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    @classmethod
    def defaults(cls):
        return cls()
