# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/instructions/__init__.py
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.views.lobby.common.buy_sell_items_dialog_model import BuySellItemsDialogModel

def getBattleBoosterItemType(item):
    if item.isCrewBooster() and not item.isAffectedSkillLearnt(g_currentVehicle.item):
        itemType = BuySellItemsDialogModel.BATTLE_BOOSTER_CREW_REPLACE
    else:
        itemType = BuySellItemsDialogModel.BATTLE_BOOSTER
    return itemType
