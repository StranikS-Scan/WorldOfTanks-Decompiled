# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview/vehicle_preview_dp.py
from items import tankmen
from items.sabaton_crew import generateTankmenForSpecialEvent
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared.formatters import text_styles
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.items_actions import factory
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms
VEH_PREVIEW_SPECIAL_PANEL_ID = 'VehPreviewSpecialCrew'
VEH_PREVIEW_INFO_PANEL_ID = 'VehPreviewInfoPanelUI'
CREW_INFO_TAB_ID = 'crewInfoTab'
FACT_SHEET_TAB_ID = 'factSheetTab'
SABATON_BTN_LINK = 'OrangeBuyBtnUI'
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
        return {'crewPanel': self.__packTabButtonsData(),
         'crewPanelLink': VEH_PREVIEW_INFO_PANEL_ID}

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


class SabatonVehPreviewDataProvider(IVehPreviewDataProvider):

    def getCrewInfo(self):
        return {'crewPanel': {'title': text_styles.highTitle(VEHICLE_PREVIEW.SPECIALCREW_SABATON_NAME),
                       'description': '{0} {1}'.format(text_styles.main(VEHICLE_PREVIEW.SPECIALCREW_SABATON_DESCRIPTION), text_styles.neutral(VEHICLE_PREVIEW.SPECIALCREW_SABATON_PERK)),
                       'headerImage': '../maps/icons/tankmen/skills/big/sabaton_brotherhood.png',
                       'crewListData': self.__packSpecialCrewInfoData()},
         'crewPanelLink': VEH_PREVIEW_SPECIAL_PANEL_ID}

    def getBuyType(self, _):
        pass

    def getBuyButtonState(self, data=None):
        return {'link': SABATON_BTN_LINK,
         'enabled': True,
         'label': VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUY}

    def getBottomPanelData(self, item):
        buyingLabel = text_styles.main(VEHICLE_PREVIEW.BUYINGPANEL_SABATON_BUYLABEL)
        isBuyingAvailable = True
        modulesLabel = VEHICLE_PREVIEW.MODULESPANEL_TITLE
        return {'buyingLabel': buyingLabel,
         'modulesLabel': text_styles.middleTitle(modulesLabel),
         'isBuyingAvailable': isBuyingAvailable,
         'isCanTrade': item.canTradeIn,
         'vehicleId': item.intCD}

    def getPriceInfo(self, data=None):
        return {'showAction': False,
         'actionTooltipType': None}

    def buyAction(self, actionType, vehicleCD, skipConfirm):
        from gui.shared import g_eventBus, events
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SABATON_SHOP))

    def __packSpecialCrewInfoData(self):
        """Gather and fill info about vehicle crew for sabaton event
        """
        tmanDescrList = generateTankmenForSpecialEvent()
        crewData = []
        for tmanDescr in tmanDescrList:
            t = tankmen.TankmanDescr(tmanDescr)
            header = _ms(TOOLTIPS.sabatonHeader(t.role))
            body = _ms(TOOLTIPS.sabatonBody(t.role))
            tooltip = makeTooltip(header or None, body or None)
            crewData.append({'name': text_styles.highlightText('{} {}'.format(Tankman.getFirstUserName(t.nationID, t.firstNameID), Tankman.getLastUserName(t.nationID, t.lastNameID))),
             'roleIcon': Tankman.getRoleBigIconPath(t.role),
             'icon': Tankman.getSmallIconPath(t.nationID, t.iconID),
             'rankIcon': Tankman.getRankSmallIconPath(t.nationID, t.rankID),
             'tooltip': tooltip,
             'tankmenPercent': _formatRoleLevelValue(t.roleLevel),
             'roles': [{'icon': Tankman.getRoleSmallIconPath(t.role)}],
             'skills': [{'icon': '../maps/icons/tankmen/skills/small/sabaton_brotherhood.png',
                         'active': True}]})

        return crewData
