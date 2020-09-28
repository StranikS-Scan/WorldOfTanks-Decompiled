# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventPrebattleTimerMeta.py
from gui.Scaleform.daapi.view.meta.PrebattleTimerMeta import PrebattleTimerMeta

class EventPrebattleTimerMeta(PrebattleTimerMeta):

    def highlightedMessageShown(self, messageType):
        self._printOverrideError('highlightedMessageShown')

    def as_queueHighlightedMessageS(self, data, flush):
        return self.flashObject.as_queueHighlightedMessage(data, flush) if self._isDAAPIInited() else None

    def as_showExtraMessageS(self, value, highlight):
        return self.flashObject.as_showExtraMessage(value, highlight) if self._isDAAPIInited() else None
