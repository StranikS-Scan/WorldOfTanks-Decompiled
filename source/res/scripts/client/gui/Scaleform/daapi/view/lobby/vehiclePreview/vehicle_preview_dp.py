# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview/vehicle_preview_dp.py
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.shared.formatters import text_styles
from gui.shared.formatters.icons import makeImageTag
from gui.shared.gui_items.items_actions import factory
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
CREW_INFO_TAB_ID = 'crewInfoTab'
FACT_SHEET_TAB_ID = 'factSheetTab'
TAB_ORDER = [FACT_SHEET_TAB_ID, CREW_INFO_TAB_ID]
TAB_DATA_MAP = {FACT_SHEET_TAB_ID: (VEHPREVIEW_CONSTANTS.FACT_SHEET_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_FACTSHEET_NAME),
 CREW_INFO_TAB_ID: (VEHPREVIEW_CONSTANTS.CREW_INFO_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_NAME)}
TAB_DATA_MAP_ELITE = {FACT_SHEET_TAB_ID: (VEHPREVIEW_CONSTANTS.ELITE_FACT_SHEET_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_FACTSHEET_NAME),
 CREW_INFO_TAB_ID: (VEHPREVIEW_CONSTANTS.CREW_INFO_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_NAME)}

def _formatRoleLevelValue(value):
    return '{}%'.format(value)


class IVehPreviewDataProvider(object):

    def getCrewInfo(self, vehicle):
        return NotImplementedError

    def getBuyType(self, vehicle):
        return NotImplementedError

    def getBottomPanelData(self, item, isHeroTank=False, isBootCamp=False):
        return NotImplementedError

    def getBuyingPanelData(self, item, data=None, isHeroTank=False):
        return NotImplementedError

    def buyAction(self, actionType, vehicleCD, skipConfirm):
        return NotImplementedError


class DefaultVehPreviewDataProvider(IVehPreviewDataProvider):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def getCrewInfo(self, vehicle):
        return {'crewPanel': self.__packTabButtonsData(vehicle)}

    def getBuyType(self, vehicle):
        return factory.BUY_VEHICLE if vehicle.isUnlocked else factory.UNLOCK_ITEM

    def getBottomPanelData(self, item, isHeroTank=False, isBootCamp=False):
        isBuyingAvailable = not isHeroTank and (not item.isHidden or item.isRentable or item.isRestorePossible())
        if isBuyingAvailable or isHeroTank:
            if item.canTradeIn:
                buyingLabel = text_styles.main(VEHICLE_PREVIEW.BUYINGPANEL_TRADEINLABEL)
            else:
                buyingLabel = ''
        else:
            buyingLabel = text_styles.tutorial(VEHICLE_PREVIEW.BUYINGPANEL_ALERTLABEL)
        vcData = None if isBootCamp else self.__getVehCompareData(item)
        vcIcon = None if isBootCamp else makeImageTag(RES_ICONS.MAPS_ICONS_BUTTONS_VEHICLECOMPAREBTN, 30, 24, -27)
        return {'buyingLabel': buyingLabel,
         'isBuyingAvailable': isBuyingAvailable,
         'isCanTrade': item.canTradeIn,
         'showStatusInfoTooltip': item.hasModulesToSelect,
         'vehicleId': item.intCD,
         'vehCompareData': vcData,
         'vehCompareIcon': vcIcon}

    def __getVehCompareData(self, vehicle):
        state, tooltip = resolveStateTooltip(self.comparisonBasket, vehicle, enabledTooltip=VEH_COMPARE.VEHPREVIEW_COMPAREVEHICLEBTN_TOOLTIPS_ADDTOCOMPARE, fullTooltip=VEH_COMPARE.STORE_COMPAREVEHICLEBTN_TOOLTIPS_DISABLED)
        return {'btnEnabled': state,
         'btnTooltip': tooltip}

    def getBuyingPanelData(self, item, data=None, isHeroTank=False):
        isAction = data.isAction
        return {'buyButtonEnabled': data.enabled,
         'buyButtonLabel': data.label,
         'buyButtonTooltip': data.tooltip,
         'value': data.price,
         'icon': data.currencyIcon,
         'showGlow': isHeroTank or item.isPremium and (not item.isHidden or item.isRentable or item.isRestorePossible()),
         'showAction': isAction,
         'actionTooltipType': TOOLTIPS_CONSTANTS.ACTION_PRICE if isAction else None,
         'actionData': data.action}

    def buyAction(self, actionType, vehicleCD, skipConfirm):
        if actionType == factory.UNLOCK_ITEM:
            unlockProps = g_techTreeDP.getUnlockProps(vehicleCD)
            factory.doAction(factory.UNLOCK_ITEM, vehicleCD, unlockProps.parentID, unlockProps.unlockIdx, unlockProps.xpCost, skipConfirm=skipConfirm)
        else:
            factory.doAction(factory.BUY_VEHICLE, vehicleCD, skipConfirm=skipConfirm)

    def __packTabButtonsData(self, vehicle):
        data = []
        isPremium = vehicle.isPremium and (not vehicle.isHidden or vehicle.isRentable or vehicle.isRestorePossible())
        tabMapping = TAB_DATA_MAP_ELITE if isPremium else TAB_DATA_MAP
        for idx in TAB_ORDER:
            linkage, label = tabMapping[idx]
            data.append({'label': label,
             'linkage': linkage})

        return data
