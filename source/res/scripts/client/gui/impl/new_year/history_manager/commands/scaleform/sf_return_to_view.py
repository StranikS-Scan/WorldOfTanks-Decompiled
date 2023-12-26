# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/history_manager/commands/scaleform/sf_return_to_view.py
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events
from gui.impl.new_year.history_manager.commands.return_to_view import ReturnToView

class SfReturnToView(ReturnToView):

    def execute(self):
        context = self.getContext()
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(context['aliasName']), **context), scope=self._getScope())
