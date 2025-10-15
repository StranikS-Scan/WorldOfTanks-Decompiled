# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_hud_widget.py
import logging
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from portal.gui.impl.battle.portal_hud_widget_view import PortalHudWidgetView
from gui.battle_control.controllers.arena_load_ctrl import IArenaLoadCtrlListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
_logger = logging.getLogger(__name__)

class PortalHudWidget(InjectComponentAdaptor, IArenaLoadCtrlListener, IAbstractPeriodView):

    def __init__(self):
        super(PortalHudWidget, self).__init__()
        _logger.debug('[Portal HudWidget] _makeInjectView')

    def _onPopulate(self):
        _logger.debug('[Portal HudWidget] _onPopulate')
        self._createInjectView()

    def _makeInjectView(self):
        _logger.debug('[Portal HudWidget] _makeInjectView')
        return PortalHudWidgetView()

    def arenaLoadCompleted(self):
        pass

    def setPeriod(self, period):
        self.getInjectView().setPeriod(period)

    def showHint(self, hint, data=None):
        self.getInjectView().showHint(hint, data)

    def hideHint(self, hint=None):
        _logger.warning('hideHint should not be used.')
