# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/battle/races/races_hud.py
import logging
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.battle_control.controllers.arena_load_ctrl import IArenaLoadCtrlListener
from races.gui.impl.battle.races_hud.races_hud_view import RacesHudView
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
_logger = logging.getLogger(__name__)

class RacesHud(InjectComponentAdaptor, IArenaLoadCtrlListener, IAbstractPeriodView):

    def __init__(self):
        super(RacesHud, self).__init__()
        _logger.debug('[Races Hud] _makeInjectView')

    def _onPopulate(self):
        _logger.debug('[Races Hud] _onPopulate')
        self._createInjectView()

    def _makeInjectView(self):
        _logger.debug('[Races Hud] _makeInjectView')
        return RacesHudView()

    def arenaLoadCompleted(self):
        pass

    def setPeriod(self, period):
        self.getInjectView().setPeriod(period)

    def showHint(self, hint, data=None):
        self.getInjectView().showHint(hint, data)

    def hideHint(self, hint=None):
        _logger.warning('hideHint should not be used.')
