# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview/vehicle_preview_dp.py
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared.formatters import text_styles
from gui.shared.gui_items.items_actions import factory
CREW_INFO_TAB_ID = 'crewInfoTab'
FACT_SHEET_TAB_ID = 'factSheetTab'
TAB_ORDER = [FACT_SHEET_TAB_ID, CREW_INFO_TAB_ID]
TAB_DATA_MAP = {FACT_SHEET_TAB_ID: (VEHPREVIEW_CONSTANTS.FACT_SHEET_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_FACTSHEET_NAME),
 CREW_INFO_TAB_ID: (VEHPREVIEW_CONSTANTS.CREW_INFO_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_NAME)}

def _formatRoleLevelValue(value):
    return '{}%'.format(value)


class IVehPreviewDataProvider(object):

    def getCrewInfo(self):
        return NotImplementedError

    def getBuyType(self, vehicle):
        return NotImplementedError

    def getBuyButtonState(self, data=None):
        return NotImplementedError

    def getBottomPanelData(self, item):
        return NotImplementedError

    def getPriceInfo(self, data=None):
        return NotImplementedError

    def buyAction(self, actionType, vehicleCD, skipConfirm):
        return NotImplementedError


class DefaultVehPreviewDataProvider(IVehPreviewDataProvider):

    def getCrewInfo(self):
        """Fill panel with formed crew or with crew roles
        :return:
        """
        return {'crewPanel': self.__packTabButtonsData()}

    def getBuyType(self, vehicle):
        if vehicle.isUnlocked:
            return factory.BUY_VEHICLE
        else:
            return factory.UNLOCK_ITEM

    def getBuyButtonState(self, data=None):
        return {'enabled': data.enabled,
         'label': data.label,
         'tooltip': data.tooltip}

    def getBottomPanelData(self, item):
        isBuyingAvailable = not item.isHidden or item.isRentable or item.isRestorePossible()
        if isBuyingAvailable:
            if item.canTradeIn:
                buyingLabel = text_styles.main(VEHICLE_PREVIEW.BUYINGPANEL_TRADEINLABEL)
            else:
                buyingLabel = text_styles.main(VEHICLE_PREVIEW.BUYINGPANEL_LABEL)
        else:
            buyingLabel = text_styles.alert(VEHICLE_PREVIEW.BUYINGPANEL_ALERTLABEL)
        if item.hasModulesToSelect:
            modulesLabel = VEHICLE_PREVIEW.MODULESPANEL_TITLE
        else:
            modulesLabel = VEHICLE_PREVIEW.MODULESPANEL_NOMODULESOPTIONS
        return {'buyingLabel': buyingLabel,
         'modulesLabel': text_styles.middleTitle(modulesLabel),
         'isBuyingAvailable': isBuyingAvailable,
         'isCanTrade': item.canTradeIn,
         'vehicleId': item.intCD}

    def getPriceInfo(self, data=None):
        return {'value': data.price,
         'icon': data.currencyIcon,
         'showAction': data.isAction,
         'actionTooltipType': TOOLTIPS_CONSTANTS.ACTION_PRICE if data.isAction else None,
         'actionData': data.action}

    def buyAction(self, actionType, vehicleCD, skipConfirm):
        if actionType == factory.UNLOCK_ITEM:
            unlockProps = g_techTreeDP.getUnlockProps(vehicleCD)
            factory.doAction(factory.UNLOCK_ITEM, vehicleCD, unlockProps.parentID, unlockProps.unlockIdx, unlockProps.xpCost, skipConfirm=skipConfirm)
        else:
            factory.doAction(factory.BUY_VEHICLE, vehicleCD, skipConfirm=skipConfirm)

    def __packTabButtonsData(self):
        data = []
        for idx in TAB_ORDER:
            linkage, label = TAB_DATA_MAP[idx]
            data.append({'label': label,
             'linkage': linkage})

        return data
