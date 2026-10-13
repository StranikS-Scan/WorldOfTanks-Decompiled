# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/random/hud.py
from __future__ import absolute_import
import logging
import typing
from frameworks.wulf import WindowFlags
from gui.app_loader import settings as app_settings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.shared.hud_view_model import HudDisplay, HudViewModel
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.Scaleform.daapi.settings.views import BattleSharedLayoutType
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Any
_logger = logging.getLogger(__name__)

class RandomHUDWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(RandomHUDWindow, self).__init__(content=RandomHUDView(sharedLayoutId=self.gui.layoutManager.getLayoutByName(app_settings.APP_NAME_SPACE.SF_BATTLE, BattleSharedLayoutType.CROSSHAIR)), wndFlags=(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN), layer=layer, **kwargs)


class RandomHUDView(ViewComponent[HudViewModel]):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(RandomHUDView, self).__init__(R.views.mono.battle_hud.main(), model=HudViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(RandomHUDView, self).getViewModel()

    def _getChildComponents(self):
        return (R.aliases.battle.shared.vehicle_mechanics(), R.aliases.battle.shared.crosshair_state(), R.aliases.battle.shared.gun_state())

    def _getListeners(self):
        return ((events.GameEvent.GUI_VISIBILITY, self.__onGuiVisibility, EVENT_BUS_SCOPE.BATTLE),)

    def _getEvents(self):
        return ((self.__sessionProvider.onBattleSessionStop, self.__onBattleSessionStop),)

    def __onBattleSessionStop(self):
        self._removeChildren()

    def __onGuiVisibility(self, event):
        visible = event.ctx['visible']
        with self.viewModel.transaction() as model:
            model.setDisplay(HudDisplay.ALL if visible else HudDisplay.NONE)
