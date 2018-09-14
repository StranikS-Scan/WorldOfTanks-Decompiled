# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCQuestsControl.py
from gui.Scaleform.daapi.view.lobby.header.QuestsControl import QuestsControl
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events

class BCQuestsControl(QuestsControl):

    def __init__(self, ctx=None):
        LOG_DEBUG('BCQuestControl.__init__')
        super(BCQuestsControl, self).__init__()

    def _populate(self):
        super(BCQuestsControl, self)._populate()

    def showQuestsWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_QUESTS_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)
