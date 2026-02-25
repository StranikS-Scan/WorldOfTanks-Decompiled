# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/impl/lobby/mode_selector/versus_ai_mode_selector_item.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.limited_ui.lui_rules_storage import LuiRules

class VersusAIModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.VERSUS_AI

    def getLimitedUIRule(self):
        return LuiRules.VERSUS_AI_CONTENT

    def _onInitializing(self):
        super(VersusAIModeSelectorItem, self)._onInitializing()
        setBattlePassState(self.viewModel)

    def _getIsDisabled(self):
        return False
