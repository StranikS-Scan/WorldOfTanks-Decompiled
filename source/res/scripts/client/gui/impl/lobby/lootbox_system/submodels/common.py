# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/submodels/common.py
from typing import TYPE_CHECKING
from gui.impl.gen.view_models.views.lobby.lootbox_system.box_info_model import BoxInfoModel
from gui.lootbox_system.utils import getIsAnimationActive, setIsAnimationActive
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Dict, Union
    from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.has_boxes_view_model import HasBoxesViewModel
    from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.single_box_rewards_view_model import SingleBoxRewardsViewModel
    from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.multiple_boxes_rewards_view_model import MultipleBoxesRewardsViewModel
    from gui.shared.gui_items.loot_box import LootBox
    IAnimatedViewModel = Union[HasBoxesViewModel, SingleBoxRewardsViewModel, MultipleBoxesRewardsViewModel]

@dependency.replace_none_kwargs(lootBoxes=ILootBoxSystemController)
def updateBoxesInfoModel(boxesInfo, lootBoxes=None):
    boxesInfo.clear()
    for box in lootBoxes.getActiveBoxes():
        boxInfo = BoxInfoModel()
        boxInfo.setBoxCategory(box.getCategory())
        boxInfo.setBoxesCount(box.getInventoryCount())
        boxInfo.setBoxesCountToGuaranteed(lootBoxes.getBoxInfo(box.getID())['boxCountToGuaranteedBonus'])
        boxesInfo.addViewModel(boxInfo)

    boxesInfo.invalidate()


def updateAnimationState(model, ctx):
    isAnimationActive = (ctx or {}).get('isAnimationActive')
    if isAnimationActive is None:
        isAnimationActive = getIsAnimationActive()
    else:
        setIsAnimationActive(isAnimationActive)
    model.setIsAnimationActive(isAnimationActive)
    return
