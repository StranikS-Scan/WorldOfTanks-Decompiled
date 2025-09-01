# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/random_mode_selector_item.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_random_battle_model import ModeSelectorRandomBattleModel
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID

class RandomModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorRandomBattleModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.RANDOM

    @property
    def viewModel(self):
        return super(RandomModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(RandomModeSelectorItem, self)._onInitializing()
        self._addReward(ModeSelectorRewardID.CREDITS)
        self._addReward(ModeSelectorRewardID.EXPERIENCE)
        setBattlePassState(self.viewModel)
