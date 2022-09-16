# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_selection_view.py
import logging
from constants import PREBATTLE_TYPE
from helpers import dependency
from gui.impl.gen import R
from skeletons.gui.game_control import IPlatoonController
from frameworks.wulf import WindowFlags, WindowLayer
from gui.shared.events import PlatoonDropdownEvent
from gui.shared import g_eventBus
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
from gui.impl.lobby.platoon.view.comp7_platoon_welcome_view import Comp7WelcomeView
_logger = logging.getLogger(__name__)
strButtons = R.strings.platoon.buttons

class SelectionWindow(PreloadableWindow):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    previousPosition = None
    __PRB_TYPE_TO_VIEW_CONTENT_FACTORY = {PREBATTLE_TYPE.SQUAD: WelcomeView,
     PREBATTLE_TYPE.FALLOUT: WelcomeView,
     PREBATTLE_TYPE.EVENT: WelcomeView,
     PREBATTLE_TYPE.EPIC: WelcomeView,
     PREBATTLE_TYPE.BATTLE_ROYALE: WelcomeView,
     PREBATTLE_TYPE.MAPBOX: WelcomeView,
     PREBATTLE_TYPE.COMP7: Comp7WelcomeView}

    @property
    def preBattleView(self):
        prbEntity = self.__platoonCtrl.getPrbEntityType()
        return self.__PRB_TYPE_TO_VIEW_CONTENT_FACTORY.get(prbEntity, WelcomeView)()

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
        if not self._isPreloading():
            g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        super(SelectionWindow, self)._onContentReady()

    def _finalize(self):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
