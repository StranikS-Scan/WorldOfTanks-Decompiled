# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/__init__.py
from frameworks.wulf import ViewFlags
from gui.clans.clan_helpers import getStrongholdClanCardUrl
from helpers.dependency import replace_none_kwargs
from gui.goodies.goodie_items import _CLAN_RESERVE_TO_GUI_TYPE
from gui.shared.event_dispatcher import showStrongholds, closeViewsWithFlags
from skeletons.gui.goodies import IGoodiesCache

@replace_none_kwargs(goodiesCache=IGoodiesCache)
def boosterActivationFlow(boosterId, goodiesCache=None):
    if boosterId in _CLAN_RESERVE_TO_GUI_TYPE:
        showStrongholds(getStrongholdClanCardUrl())
        closeViewsWithFlags([], [ViewFlags.LOBBY_TOP_SUB_VIEW])
        return
    from gui.shared.gui_items.items_actions import factory
    booster = goodiesCache.getBooster(boosterId)
    if booster.isInAccount:
        actionId = factory.ACTIVATE_BOOSTER
    else:
        actionId = factory.BUY_AND_ACTIVATE_BOOSTER
    factory.doAction(actionId, booster)
