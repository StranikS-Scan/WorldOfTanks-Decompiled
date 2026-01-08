# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SixthSenseContextHintMeta.py
from gui.impl.battle.battle_page.battle_context_hints.hint_inject_component import HintInjectComponent

class SixthSenseContextHintMeta(HintInjectComponent):

    def as_setVisibilityS(self, isVisible):
        return self.flashObject.as_setVisibility(isVisible) if self._isDAAPIInited() else None
