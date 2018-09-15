# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/halloween/page.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from debug_utils import LOG_DEBUG

class HalloweenBattlePage(ClassicPage):

    def _populate(self):
        super(HalloweenBattlePage, self)._populate()
        LOG_DEBUG('Halloween battle page is created.')

    def _dispose(self):
        super(HalloweenBattlePage, self)._dispose()
        LOG_DEBUG('Halloween battle page is destroyed.')
