# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortSortieOrdersPanelComponent.py
import UnitBase
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleRoomOrdersPanelComponent import FortBattleRoomOrdersPanelComponent

class FortSortieOrdersPanelComponent(FortBattleRoomOrdersPanelComponent):

    def _isConsumablesAvailable(self):
        _, unit = self.prbEntity.getUnit(self.prbEntity.getUnitIdx())
        return unit is not None and unit.getRosterTypeID() == UnitBase.ROSTER_TYPE.SORTIE_ROSTER_10

    def _getSlotsProps(self):
        props = super(FortSortieOrdersPanelComponent, self)._getSlotsProps()
        props.update({'panelAlias': FORTIFICATION_ALIASES.FORT_SORTIE_ORDERS_PANEL_COMPONENT_ALIAS})
        return props
