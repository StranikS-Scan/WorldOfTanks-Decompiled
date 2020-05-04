# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_menu_widget.py
from frameworks.wulf import ViewFlags
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.lobby.secret_event.action_view_with_menu import ActionViewWithMenu
from gui.impl.lobby.secret_event.sound_constants import ACTION_WIDGET_SETTINGS

class ActionMenuWidget(ActionViewWithMenu):
    __slots__ = ()
    _COMMON_SOUND_SPACE = ACTION_WIDGET_SETTINGS

    def __init__(self):
        settings = ViewSettings(R.views.lobby.secretEvent.MenuWidget(), ViewFlags.COMPONENT, ActionMenuModel())
        super(ActionMenuWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self):
        super(ActionMenuWidget, self)._onLoading()
        self.viewModel.setCurrentView(ActionMenuModel.SHOP)

    def handleEscape(self):
        self._onEscPressed()
