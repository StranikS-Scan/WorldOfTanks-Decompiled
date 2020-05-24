# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from debug_utils import LOG_DEBUG

class EventBattlePage(ClassicPage):

    def _populate(self):
        super(EventBattlePage, self)._populate()
        LOG_DEBUG('Event battle page is created.')

    def _dispose(self):
        super(EventBattlePage, self)._dispose()
        LOG_DEBUG('Event battle page is destroyed.')
