# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/skeletons/gui/game_control.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from typing import Dict
    from Event import Event
    from comp7.gui.game_control.comp7_weekly_quests_controller import _Comp7WeeklyQuests
    from gui.ranked_battles.ranked_models import Rank

class IComp7ShopController(IGameController):
    onDataUpdated = None
    onShopStateChanged = None

    @property
    def isShopEnabled(self):
        raise NotImplementedError

    def getProducts(self):
        raise NotImplementedError

    def buyProduct(self, productCode):
        raise NotImplementedError

    def hasNewProducts(self, rank):
        raise NotImplementedError

    def hasNewDiscounts(self, rank):
        raise NotImplementedError


class IComp7WeeklyQuestsController(IGameController):
    onWeeklyQuestsUpdated = None

    def getQuests(self):
        raise NotImplementedError()

    def isInHideState(self):
        raise NotImplementedError()
