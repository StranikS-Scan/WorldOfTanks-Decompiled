# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/battle/frag_correlation_bar.py
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform.daapi.view.meta.BCFragCorrelationBarMeta import BCFragCorrelationBarMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

class BootcampFragCorrelationBar(BCFragCorrelationBarMeta):

    def __init__(self):
        super(BootcampFragCorrelationBar, self).__init__()
        self.__needHint = False

    def _populate(self):
        super(BootcampFragCorrelationBar, self)._populate()
        g_bootcampEvents.onHighlightAdded += self.__onHighlightAdded

    def _dispose(self):
        g_bootcampEvents.onHighlightAdded -= self.__onHighlightAdded
        super(BootcampFragCorrelationBar, self)._dispose()

    def __onHighlightAdded(self, alias):
        if alias == BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR:
            self.as_showHintS()
