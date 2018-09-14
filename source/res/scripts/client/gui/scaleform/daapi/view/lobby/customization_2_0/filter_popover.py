# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization_2_0/filter_popover.py
from constants import IGR_TYPE
from gui import GUI_SETTINGS
from gui.game_control import getIGRCtrl
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.CUSTOMIZATION import CUSTOMIZATION
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.meta.CustomizationFiltersPopoverMeta import CustomizationFiltersPopoverMeta
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from gui.customization_2_0 import g_customizationController
from gui.customization_2_0.data_aggregator import CUSTOMIZATION_TYPE
from gui.customization_2_0.filter import FILTER_TYPE, QUALIFIER_TYPE_INDEX, PURCHASE_TYPE
from gui.customization_2_0.elements.qualifier import QUALIFIER_TYPE
from gui.customization_2_0.elements.qualifier import getIcon16x16ByType as _getQualifierIcon

class FilterPopover(CustomizationFiltersPopoverMeta):

    def __init__(self, ctx = None):
        super(FilterPopover, self).__init__()
        self.__filter = g_customizationController.carousel.filter
        self.__tooltipsMap = {QUALIFIER_TYPE.ALL: self.__createTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_ENTIRECREW),
         QUALIFIER_TYPE.COMMANDER: self.__createTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_COMMANDER),
         QUALIFIER_TYPE.GUNNER: self.__createTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_AIMER),
         QUALIFIER_TYPE.DRIVER: self.__createTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_DRIVER),
         QUALIFIER_TYPE.RADIOMAN: self.__createTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_RADIOMAN),
         QUALIFIER_TYPE.LOADER: self.__createTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_LOADER)}
        self.__enableGroupsFilter = True
        self.__filterTypeGroup = self.__filter.currentGroup
        self.__groupsMap = [[('all_groups', CUSTOMIZATION.FILTER_POPOVER_GROUPS_ALL)], [('all_groups', CUSTOMIZATION.FILTER_POPOVER_GROUPS_ALL)], [('all_groups', CUSTOMIZATION.FILTER_POPOVER_GROUPS_ALL)]]
        for cType in (CUSTOMIZATION_TYPE.CAMOUFLAGE, CUSTOMIZATION_TYPE.EMBLEM, CUSTOMIZATION_TYPE.INSCRIPTION):
            for groupName, userName in self.__filter.availableGroupNames[cType]:
                if groupName != 'group5' and groupName != 'IGR':
                    self.__groupsMap[cType].append((groupName, userName))

        self.__purchaseTypeMap = {PURCHASE_TYPE.PURCHASE: CUSTOMIZATION.FILTER_POPOVER_WAYSTOBUY_BUY,
         PURCHASE_TYPE.QUEST: CUSTOMIZATION.FILTER_POPOVER_WAYSTOBUY_MISSIONS,
         PURCHASE_TYPE.ACTION: CUSTOMIZATION.FILTER_POPOVER_WAYSTOBUY_EVENT,
         PURCHASE_TYPE.IGR: icons.premiumIgrSmall()}
        self.__purchaseTypeList = [PURCHASE_TYPE.PURCHASE, PURCHASE_TYPE.QUEST]
        if GUI_SETTINGS.igrEnabled:
            self.__purchaseTypeList.append(PURCHASE_TYPE.IGR)

    def _populate(self):
        super(FilterPopover, self)._populate()
        self.as_setInitDataS(self.createInitVO())
        self.as_enableDefBtnS(not self.__filter.isDefaultFilterSet())

    def __switchIGRFilter(self, value):
        if self.__enableGroupsFilter == value:
            self.__enableGroupsFilter = not value
            self.as_enableGroupFilterS(self.__enableGroupsFilter)
            if value:
                self.__filterTypeGroup = self.__filter.currentGroup
                self.__filter.set(FILTER_TYPE.GROUP, 'all_groups')
            else:
                self.__filter.set(FILTER_TYPE.GROUP, self.__filterTypeGroup)

    def changeFilter(self, filterGroup, filterGroupValue):
        if filterGroup == FILTER_TYPE.GROUP:
            filterGroupValue = self.__groupsMap[self.__filter.currentType][filterGroupValue][0]
        if filterGroup == FILTER_TYPE.PURCHASE_TYPE:
            filterGroupValue = self.__purchaseTypeList[filterGroupValue]
            self.__switchIGRFilter(filterGroupValue == PURCHASE_TYPE.IGR)
        self.__filter.set(filterGroup, filterGroupValue)
        self.__filter.apply()
        self.as_enableDefBtnS(not self.__filter.isDefaultFilterSet())

    def createInitVO(self):
        isTypeNotCamouflage = self.__filter.currentType != CUSTOMIZATION_TYPE.CAMOUFLAGE
        groupsUserNames = []
        groupsList = []
        for groupData in self.__groupsMap[self.__filter.currentType]:
            groupsUserNames.append(groupData[1])
            groupsList.append(groupData[0])

        if isTypeNotCamouflage:
            groupsSelectIndex = groupsList.index(self.__filter.currentGroup)
        else:
            groupsSelectIndex = 0
        return {'lblTitle': text_styles.highTitle(CUSTOMIZATION.FILTER_POPOVER_TITLE),
         'lblBonusType': text_styles.standard(CUSTOMIZATION.FILTER_POPOVER_BONUSTYPE_TITLE),
         'lblCustomizationType': text_styles.standard(CUSTOMIZATION.FILTER_POPOVER_GROUPS_TITLE),
         'lblPurchaseType': text_styles.standard(CUSTOMIZATION.FILTER_POPOVER_WAYSTOBUY_TITLE),
         'btnDefault': CUSTOMIZATION.FILTER_POPOVER_GETDEFAULTSETTINGS,
         'bonusTypeId': FILTER_TYPE.QUALIFIER,
         'bonusType': self.__getBonusTypeVO(),
         'customizationBonusTypeVisible': isTypeNotCamouflage,
         'customizationTypeId': FILTER_TYPE.GROUP,
         'customizationType': groupsUserNames,
         'customizationTypeSelectedIndex': groupsSelectIndex,
         'customizationTypeVisible': isTypeNotCamouflage,
         'bonusTypeDisableTooltip': makeTooltip(CUSTOMIZATION.TOOLTIP_FILTER_GROUPS_DISABLED_HEADER, CUSTOMIZATION.TOOLTIP_FILTER_GROUPS_DISABLED_BODY),
         'refreshTooltip': makeTooltip(TOOLTIPS.CUSTOMIZATION_FILTERPOPOVER_REFRESH_HEADER, TOOLTIPS.CUSTOMIZATION_FILTERPOPOVER_REFRESH_BODY),
         'purchaseTypeId': FILTER_TYPE.PURCHASE_TYPE,
         'purchaseType': self.__getPurchaseTypeVO(),
         'purchaseTypeSelectedIndex': self.__purchaseTypeList.index(self.__filter.purchaseType)}

    def __getPurchaseTypeVO(self):
        result = []
        for purchaseType in self.__purchaseTypeList:
            purchaseVO = {'label': self.__purchaseTypeMap[purchaseType],
             'enabled': True}
            if purchaseType == PURCHASE_TYPE.IGR:
                purchaseVO['enabled'] = getIGRCtrl().getRoomType() == IGR_TYPE.PREMIUM
                purchaseVO['tooltipDisabled'] = makeTooltip(_ms(CUSTOMIZATION.FILTER_TOOLTIP_IGR_DISABLED_HEADER), _ms(CUSTOMIZATION.FILTER_TOOLTIP_IGR_DISABLED_BODY, icon=_ms(icons.premiumIgrSmall())))
            result.append(purchaseVO)

        return result

    def __getBonusTypeVO(self):
        result = []
        for bonusType in QUALIFIER_TYPE_INDEX:
            vo = {'selected': self.__filter.selectedBonuses[bonusType],
             'value': _getQualifierIcon(bonusType),
             'tooltip': self.__tooltipsMap[bonusType]}
            result.append(vo)

        return result

    def __createTooltip(self, value):
        return makeTooltip(_ms(TOOLTIPS.CUSTOMIZATION_FILTERPOPOVER_BONUSDESCRIPTION_HEADER, bonus=_ms(value)), _ms(TOOLTIPS.CUSTOMIZATION_FILTERPOPOVER_BONUSDESCRIPTION_BODY, bonus=_ms(value)))

    def setDefaultFilter(self):
        self.__filter.setDefaultFilter()
        self.__filter.apply()
        bonusTypeSelected = []
        for bonusType in QUALIFIER_TYPE_INDEX:
            bonusTypeSelected.append(self.__filter.selectedBonuses[bonusType])

        data = {'customizationTypeSelectedIndex': 0,
         'purchaseTypeSelectedIndex': 0,
         'bonusTypeSelected': bonusTypeSelected}
        self.as_setStateS(data)
        self.as_enableDefBtnS(False)
