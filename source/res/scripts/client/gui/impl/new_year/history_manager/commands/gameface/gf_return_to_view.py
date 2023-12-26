# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/history_manager/commands/gameface/gf_return_to_view.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.new_year.history_manager.commands.return_to_view import ReturnToView
from gui.shared import g_eventBus, events

class GfReturnToView(ReturnToView):

    def __init__(self, contentResId, presenter, context, backButtonText, viewScope=ScopeTemplates.LOBBY_SUB_SCOPE):
        super(GfReturnToView, self).__init__(context, backButtonText)
        self.__contentResId = contentResId
        self.__presenter = presenter
        self.__viewScope = viewScope

    def execute(self):
        context = self.getContext()
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(self.__contentResId, self.__presenter, self.__viewScope), **context), scope=self._getScope())
