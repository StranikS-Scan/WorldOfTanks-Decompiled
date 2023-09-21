# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_selection_view.py
import logging
from helpers import dependency
from gui.impl.gen import R
from skeletons.gui.game_control import IPlatoonController
from frameworks.wulf import WindowFlags, WindowLayer
from gui.shared.events import PlatoonDropdownEvent
from gui.shared import g_eventBus
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
_logger = logging.getLogger(__name__)
strButtons = R.strings.platoon.buttons

class SelectionWindow(PreloadableWindow):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    previousPosition = None

    @property
    def preBattleView(self):
        prbEntity = self.__platoonCtrl.getPrbEntityType()
        from gui.impl.lobby.platoon.platoon_config import PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY
        return PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY.get(prbEntity, WelcomeView)()

    def __init__(self, initialPosition=None):
        super(SelectionWindow, self).__init__(wndFlags=WindowFlags.POP_OVER, content=self.preBattleView, layer=WindowLayer.WINDOW)
        if initialPosition:
            SelectionWindow.previousPosition = initialPosition
        if SelectionWindow.previousPosition:
            self.move(SelectionWindow.previousPosition.x, SelectionWindow.previousPosition.y)

    def show(self):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        if self.content:
            self.content.update(updateTiersLimitSubview=True)
        super(SelectionWindow, self).show()

    def hide(self):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
        super(SelectionWindow, self).hide()

    def _onContentReady(self):
        if not self.isPreloading():
            g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        super(SelectionWindow, self)._onContentReady()

    def _finalize(self):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
