# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/formatters.py
from gui.Scaleform import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control import getVehicleComparisonBasketCtrl
from gui.game_control.veh_comparison_basket import isValidVehicleForComparing
from helpers.i18n import makeString as _ms

def packHeaderColumnData(columnID, btnWidth, btnHeight, label='', icon='', tooltip='', direction='descending', showSeparator=True, textAlign='center', enabled=False):
    return {'id': columnID,
     'label': _ms(label),
     'iconSource': icon,
     'buttonWidth': btnWidth,
     'toolTip': tooltip,
     'defaultSortDirection': direction,
     'buttonHeight': btnHeight,
     'showSeparator': showSeparator,
     'enabled': enabled,
     'textAlign': textAlign}


def getTreeNodeCompareData(vehicle):
    assert vehicle
    comparison_basket = getVehicleComparisonBasketCtrl()
    return {'modeAvailable': comparison_basket.isEnabled(),
     'cmpBasketFull': not comparison_basket.isReadyToAdd(vehicle)}


def getBtnCompareData(vehicle):
    assert vehicle
    comparisonBasket = getVehicleComparisonBasketCtrl()
    state, tooltip = resolveStateTooltip(comparisonBasket, vehicle, enabledTooltip=TOOLTIPS.RESEARCHPAGE_VEHICLE_BUTTON_COMPARE_ADD, fullTooltip=TOOLTIPS.RESEARCHPAGE_VEHICLE_BUTTON_COMPARE_DISABLED)
    return {'modeAvailable': comparisonBasket.isEnabled(),
     'btnLabel': MENU.RESEARCH_LABELS_BUTTON_ADDTOCOMPARE,
     'btnEnabled': state,
     'btnTooltip': tooltip}


def resolveStateTooltip(comparisonBasket, vehicle, enabledTooltip, fullTooltip, invalidTooltip=VEH_COMPARE.VEHPREVIEW_COMPAREVEHICLEBTN_TOOLTIPS_CANNOTADDTOCOMPARE, miniclientTooltip=VEH_COMPARE.COMPAREVEHICLEBTN_TOOLTIPS_MINICLIENT):
    if not comparisonBasket.isAvailable():
        state, tooltip = False, miniclientTooltip
    elif comparisonBasket.isFull():
        state, tooltip = False, fullTooltip
    elif not isValidVehicleForComparing(vehicle):
        state, tooltip = False, invalidTooltip
    else:
        state, tooltip = True, enabledTooltip
    return (state, tooltip)
