# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/shared/gui_helpers.py
from frameworks.wulf.view.array import fillStringsArray, fillIntsArray
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_view_model import LootboxViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_key_view_model import LootboxKeyViewModel
from gui.impl.lobby.loot_box.loot_box_helper import isAllVehiclesObtainedInSlot
from shared_utils import findFirst

def getLootBoxViewModel(lootBox, attemptsAfterGuaranteedReward):
    lbModel = LootboxViewModel()
    lbModel.setTier(lootBox.getTier())
    lbModel.setBoxID(lootBox.getID())
    lbModel.setBoxType(lootBox.getType())
    lbModel.setCount(lootBox.getInventoryCount())
    lbModel.setIsOpenEnabled(lootBox.isEnabled())
    lbModel.setAutoOpenTime(lootBox.getAutoOpenTime())
    lbModel.setUserName(lootBox.getUserNameKey())
    lbModel.setIconName(lootBox.getIconName())
    lbModel.setDescriptionKey(lootBox.getDesrciption())
    lbModel.setVideoRes(lootBox.getVideoRes())
    lbModel.setCategory(lootBox.getCategory())
    lbModel.setIsInfinite(lootBox.isHiddenCount())
    fillIntsArray(lootBox.getUnlockKeyIDs(), lbModel.getUnlockKeyIDs())
    rotationStage = lootBox.getRotationStage()
    if lootBox.hasLootLists():
        rotationStage = lootBox.getRotationStage()
        lootlists = lootBox.getLootLists()
        firstSlot = findFirst(lambda x: x is not None, lootlists[rotationStage])
        if firstSlot is not None:
            rotationStage += isAllVehiclesObtainedInSlot(lootlists[rotationStage][firstSlot])
        rotationStage += 1
    lbModel.setProgressionStage(rotationStage)
    fillStringsArray(lootBox.getBonusGroups(), lbModel.getBonusGroups())
    if lootBox.getGuaranteedFrequency() > 0:
        fillIntsArray(lootBox.getGuaranteedVehicleLevelsRange(), lbModel.guaranteedReward.getLevelsRange())
        lbModel.guaranteedReward.setBoxesUntilGuaranteedReward(lootBox.getGuaranteedFrequency() - attemptsAfterGuaranteedReward)
    return lbModel


def getLootBoxKeyViewModel(lootBoxKey):
    lbKeyModel = LootboxKeyViewModel()
    lbKeyModel.setKeyID(lootBoxKey.keyID)
    lbKeyModel.setCount(lootBoxKey.count)
    lbKeyModel.keyType.setValue(lootBoxKey.keyType)
    lbKeyModel.setIconName(lootBoxKey.iconName)
    lbKeyModel.setUserName(lootBoxKey.userName)
    lbKeyModel.setOpenProbability(lootBoxKey.openProbability)
    return lbKeyModel
