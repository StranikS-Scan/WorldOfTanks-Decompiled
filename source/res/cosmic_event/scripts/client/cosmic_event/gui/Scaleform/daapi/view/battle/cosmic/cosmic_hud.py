# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/Scaleform/daapi/view/battle/cosmic/cosmic_hud.py
import logging
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.battle_control.controllers.arena_load_ctrl import IArenaLoadCtrlListener
from cosmic_event.gui.impl.battle.cosmic_hud.cosmic_hud_view import CosmicHudView
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
_logger = logging.getLogger(__name__)

class CosmicHud(InjectComponentAdaptor, IArenaLoadCtrlListener, IAbstractPeriodView):

    def __init__(self):
        super(CosmicHud, self).__init__()
        _logger.debug('[Cosmic Hud] _makeInjectView')

    def _onPopulate(self):
        _logger.debug('[Cosmic Hud] _onPopulate')
        self._createInjectView()

    def _makeInjectView(self):
        _logger.debug('[Cosmic Hud] _makeInjectView')
        return CosmicHudView()

    def arenaLoadCompleted(self):
        pass

    def setPeriod(self, period):
        self.getInjectView().setPeriod(period)

    def showHint(self, hint, data=None):
        self.getInjectView().showHint(hint, data)

    def hideHint(self, hint=None):
        _logger.warning('hideHint should not be used.')
