# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCFragCorrelationBarMeta.py
from gui.Scaleform.daapi.view.battle.shared.frag_correlation_bar import FragCorrelationBar

class BCFragCorrelationBarMeta(FragCorrelationBar):

    def as_showHintS(self):
        return self.flashObject.as_showHint() if self._isDAAPIInited() else None
