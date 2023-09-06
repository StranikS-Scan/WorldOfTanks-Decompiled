# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/impl/lobby/mode_selector/versus_ai_mode_selector_item.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem

class VersusAIModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.VERSUS_AI

    def _getIsDisabled(self):
        return False
