# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/cybersport_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import cybersport
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.CYBER_SPORT_SLOT, TOOLTIPS_CONSTANTS.SUITABLE_VEHICLE_UI, cybersport.CybersportSlotToolTipData(contexts.CyberSportUnitContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CYBER_SPORT_SLOT_SELECTED, TOOLTIPS_CONSTANTS.SELECTED_VEHICLE_UI, cybersport.CybersportSlotSelectedToolTipData(contexts.CyberSportUnitContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CYBER_SPORT_SELECTED_VEHICLE, TOOLTIPS_CONSTANTS.SELECTED_VEHICLE_UI, cybersport.CybersportSelectedVehicleToolTipData(contexts.CyberSportUnitContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SELECTED_VEHICLE_TRADEOFF, TOOLTIPS_CONSTANTS.SELECTED_VEHICLE_UI, cybersport.CybersportSelectedVehicleToolTipData(contexts.CyberSportUnitContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CYBER_SPORT_TEAM, TOOLTIPS_CONSTANTS.UNIT_COMMAND, cybersport.CybersportUnitToolTipData(contexts.CyberSportUnitContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CYBER_SPORT_UNIT_LEVEL, TOOLTIPS_CONSTANTS.UNIT_LEVEL_UI, cybersport.CybersportUnitLevelToolTipData(contexts.CyberSportUnitContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CYBER_SPORT_VEHICLE_NOT_READY, TOOLTIPS_CONSTANTS.SELECTED_VEHICLE_UI, cybersport.CybersportSlotSelectedToolTipData(contexts.CyberSportUnitContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SQUAD_SLOT_VEHICLE_SELECTED, TOOLTIPS_CONSTANTS.SELECTED_VEHICLE_UI, cybersport.SquadSlotSelectedToolTipData(contexts.CyberSportUnitContext())))
