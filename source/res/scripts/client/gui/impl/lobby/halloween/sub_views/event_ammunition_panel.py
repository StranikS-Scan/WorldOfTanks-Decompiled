# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/sub_views/event_ammunition_panel.py
from gui.impl.gen import R
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
from gui.impl.lobby.tank_setup.backports.tooltips import PANEL_SLOT_TOOLTIPS, EventShellTooltipBuilder
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants

class EventAmmunitionPanel(HangarAmmunitionPanelView):

    def __init__(self):
        super(EventAmmunitionPanel, self).__init__(layoutId=R.views.lobby.halloween.EventAmmunitionPanel())

    def _createToolTipData(self, event, tooltipsMap=None):
        newTooltipsMap = tooltipsMap
        slotType = event.getArgument('slotType')
        if slotType == TankSetupConstants.SHELLS:
            newTooltipsMap = tooltipsMap or PANEL_SLOT_TOOLTIPS
            newTooltipsMap = newTooltipsMap.copy()
            newTooltipsMap[TankSetupConstants.SHELLS] = EventShellTooltipBuilder
        return super(EventAmmunitionPanel, self)._createToolTipData(event, newTooltipsMap)

    def update(self, fullUpdate=True):
        if self._ammunitionPanel._controller is None:
            return
        else:
            super(EventAmmunitionPanel, self).update(fullUpdate=fullUpdate)
            return
