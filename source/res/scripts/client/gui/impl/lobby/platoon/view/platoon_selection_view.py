# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/view/platoon_selection_view.py
import logging
from helpers import dependency
from frameworks.wulf import WindowFlags, WindowLayer, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.pop_over_window_model import PopOverWindowModel
from gui.impl.pub import WindowView
from gui.shared.events import PlatoonDropdownEvent
from gui.shared import g_eventBus
from gui.impl.lobby.platoon.platoon_helpers import PreloadableWindow
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
from skeletons.gui.game_control import IPlatoonController
_logger = logging.getLogger(__name__)
strButtons = R.strings.platoon.buttons

class SelectionWindow(PreloadableWindow):
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    @property
    def popOverModel(self):
        return super(SelectionWindow, self)._getDecoratorViewModel()

    @property
    def preBattleView(self):
        prbEntity = self.__platoonCtrl.getPrbEntityType()
        from gui.impl.lobby.platoon.platoon_config import PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY
        return PRB_TYPE_TO_WELCOME_VIEW_CONTENT_FACTORY.get(prbEntity, WelcomeView)()

    def __init__(self):
        popoverParams = self.__platoonCtrl.getPopoverParams()
        decorator = WindowView(layoutID=0, flags=ViewFlags.POP_OVER_DECORATOR, viewModelClazz=PopOverWindowModel)
        areaID = R.areas.pop_over()
        super(SelectionWindow, self).__init__(wndFlags=WindowFlags.POP_OVER, content=self.preBattleView, decorator=decorator, layer=WindowLayer.WINDOW, areaID=areaID)
        if popoverParams is not None:
            with self.popOverModel.transaction() as tx:
                tx.setBoundX(popoverParams.bbox.positionX)
                tx.setBoundY(popoverParams.bbox.positionY)
                tx.setBoundWidth(popoverParams.bbox.width)
                tx.setBoundHeight(popoverParams.bbox.height)
                tx.setDirectionType(popoverParams.direction)
                tx.setIsCloseBtnVisible(False)
        else:
            _logger.warning('Initializing window with empty popover parameters')
        return

    def show(self, focus=True):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        if self.content:
            self.content.update(updateTiersLimitSubview=True)
        super(SelectionWindow, self).show(focus)

    def hide(self, destroy=False):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
        super(SelectionWindow, self).hide(destroy)

    def _onContentReady(self):
        if not self._isPreloading():
            g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': True}))
        super(SelectionWindow, self)._onContentReady()

    def _finalize(self):
        g_eventBus.handleEvent(PlatoonDropdownEvent(PlatoonDropdownEvent.NAME, ctx={'showing': False}))
