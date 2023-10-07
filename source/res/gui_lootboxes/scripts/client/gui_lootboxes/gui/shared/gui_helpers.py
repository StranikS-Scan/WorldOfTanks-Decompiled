# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/shared/gui_helpers.py
from frameworks.wulf.view.array import fillStringsArray
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_view_model import LootboxViewModel

def getLootBoxViewModel(lootBox):
    lbModel = LootboxViewModel()
    lbModel.setTier(lootBox.getTier())
    lbModel.setBoxID(lootBox.getID())
    lbModel.setBoxType(lootBox.getType())
    lbModel.setCount(lootBox.getInventoryCount())
    lbModel.setIsOpenEnabled(lootBox.isEnabled())
    lbModel.setUserName(lootBox.getUserNameKey())
    lbModel.setIconName(lootBox.getIconName())
    lbModel.setDescriptionKey(lootBox.getDesrciption())
    lbModel.setVideoRes(lootBox.getVideoRes())
    lbModel.setCategory(lootBox.getCategory())
    fillStringsArray(lootBox.getBonusGroups(), lbModel.getBonusGroups())
    return lbModel
