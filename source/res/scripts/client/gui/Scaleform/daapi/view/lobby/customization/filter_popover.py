# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/filter_popover.py
from constants import IGR_TYPE
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.meta.CustomizationFiltersPopoverMeta import CustomizationFiltersPopoverMeta
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.customization import g_customizationController
from gui.customization.shared import CUSTOMIZATION_TYPE, getBonusIcon16x16, FILTER_TYPE, QUALIFIER_TYPE_INDEX, PURCHASE_TYPE, DEFAULT_GROUP_VALUE, EMBLEM_IGR_GROUP_NAME
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IIGRController
_BONUS_TOOLTIPS = (VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_ENTIRECREW,
 VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_COMMANDER,
 VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_AIMER,
 VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_DRIVER,
 VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_RADIOMAN,
 VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_BONUS_LOADER)
_PURCHASE_TYPE_LABELS = (VEHICLE_CUSTOMIZATION.FILTER_POPOVER_WAYSTOBUY_BUY, VEHICLE_CUSTOMIZATION.FILTER_POPOVER_WAYSTOBUY_MISSIONS, icons.premiumIgrSmall())

def _getPurchaseTypeVO():
    result = []
    igrCtrl = dependency.instance(IIGRController)
    for purchaseType, label in zip(PURCHASE_TYPE.ALL, _PURCHASE_TYPE_LABELS):
        purchaseVO = {'label': label,
         'enabled': True}
        if purchaseType == PURCHASE_TYPE.IGR:
            if not GUI_SETTINGS.igrEnabled:
                continue
            purchaseVO['enabled'] = igrCtrl.getRoomType() == IGR_TYPE.PREMIUM
            purchaseVO['tooltipDisabled'] = makeTooltip(_ms(VEHICLE_CUSTOMIZATION.FILTER_TOOLTIP_IGR_DISABLED_HEADER), _ms(VEHICLE_CUSTOMIZATION.FILTER_TOOLTIP_IGR_DISABLED_BODY, icon=_ms(icons.premiumIgrSmall())))
        result.append(purchaseVO)

    return result


def _getBonusTypeVO(selectedBonuses):
    result = []
    for bonusType, tooltipText in zip(QUALIFIER_TYPE_INDEX, _BONUS_TOOLTIPS):
        tooltip = makeTooltip(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTERPOPOVER_BONUSDESCRIPTION_HEADER, bonus=_ms(tooltipText)), _ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTERPOPOVER_BONUSDESCRIPTION_BODY, bonus=_ms(tooltipText)))
        result.append({'selected': selectedBonuses[bonusType],
         'value': getBonusIcon16x16(bonusType),
         'tooltip': tooltip})

    return result


class FilterPopover(CustomizationFiltersPopoverMeta):

    def __init__(self, ctx=None):
        super(FilterPopover, self).__init__()
        self.__filter = None
        self.__groupsMap = []
        return

    def changeFilter(self, filterGroup, filterGroupValue):
        applyFilter = True
        if filterGroup == FILTER_TYPE.GROUP:
            filterGroupValue = self.__groupsMap[self.__filter.currentType][filterGroupValue][0]
            if self.__filter.currentGroup == filterGroupValue:
                applyFilter = False
        elif filterGroup == FILTER_TYPE.PURCHASE_TYPE:
            filterGroupValue = PURCHASE_TYPE.ALL[filterGroupValue]
            if self.__filter.purchaseType == filterGroupValue:
                applyFilter = False
            elif self.__filter.currentType != CUSTOMIZATION_TYPE.CAMOUFLAGE:
                self.__switchIGRFilter(filterGroupValue == PURCHASE_TYPE.IGR)
        if applyFilter:
            self.__filter.set(filterGroup, filterGroupValue)
            self.as_enableDefBtnS(not self.__filter.isDefaultFilterSet())

    def setDefaultFilter(self):
        self.__filter.setDefault()
        updateVO = self.__createUpdateVO()
        self.as_setStateS({'bonusTypeSelected': updateVO['bonusTypeSelected'],
         'customizationTypeSelectedIndex': updateVO['groupsSelectIndex'],
         'purchaseTypeSelectedIndex': updateVO['purchaseTypeSelectedIndex'],
         'enableGroupFilter': updateVO['enableGroupFilter']})
        self.as_enableDefBtnS(False)

    def _populate(self):
        super(FilterPopover, self)._populate()
        self.__filter = g_customizationController.filter
        self.__groupsMap = [[('all_groups', VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GROUPS_ALL)], [('all_groups', VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GROUPS_ALL)], [('all_groups', VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GROUPS_ALL)]]
        for cType in CUSTOMIZATION_TYPE.ALL:
            for groupName, userName in self.__filter.availableGroupNames[cType]:
                if groupName != EMBLEM_IGR_GROUP_NAME and groupName != 'IGR':
                    self.__groupsMap[cType].append((groupName, userName))

        self.as_setInitDataS(self.__createInitialVO())
        self.as_enableDefBtnS(not self.__filter.isDefaultFilterSet())

    def _dispose(self):
        self.__filter = None
        self.__groupsMap = []
        super(FilterPopover, self)._dispose()
        return

    def __createInitialVO(self):
        isTypeNotCamouflage = self.__filter.currentType != CUSTOMIZATION_TYPE.CAMOUFLAGE
        groupsUserNames = []
        for _, groupName in self.__groupsMap[self.__filter.currentType]:
            groupsUserNames.append(groupName)

        updateVO = self.__createUpdateVO()
        return {'lblTitle': text_styles.highTitle(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_TITLE),
         'lblBonusType': text_styles.standard(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_BONUSTYPE_TITLE),
         'lblCustomizationType': text_styles.standard(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GROUPS_TITLE),
         'lblPurchaseType': text_styles.standard(VEHICLE_CUSTOMIZATION.FILTER_POPOVER_WAYSTOBUY_TITLE),
         'btnDefault': VEHICLE_CUSTOMIZATION.FILTER_POPOVER_GETDEFAULTSETTINGS,
         'bonusTypeId': FILTER_TYPE.QUALIFIER,
         'bonusType': _getBonusTypeVO(self.__filter.selectedBonuses),
         'customizationBonusTypeVisible': isTypeNotCamouflage,
         'enableGroupFilter': updateVO['enableGroupFilter'],
         'customizationTypeId': FILTER_TYPE.GROUP,
         'customizationType': groupsUserNames,
         'customizationTypeSelectedIndex': updateVO['groupsSelectIndex'],
         'customizationTypeVisible': isTypeNotCamouflage,
         'bonusTypeDisableTooltip': makeTooltip(VEHICLE_CUSTOMIZATION.TOOLTIP_FILTER_GROUPS_DISABLED_HEADER, VEHICLE_CUSTOMIZATION.TOOLTIP_FILTER_GROUPS_DISABLED_BODY),
         'refreshTooltip': makeTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTERPOPOVER_REFRESH_HEADER, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTERPOPOVER_REFRESH_BODY),
         'purchaseTypeId': FILTER_TYPE.PURCHASE_TYPE,
         'purchaseType': _getPurchaseTypeVO(),
         'purchaseTypeSelectedIndex': PURCHASE_TYPE.ALL.index(self.__filter.purchaseType)}

    def __createUpdateVO(self):
        groupsList = []
        bonusTypeSelected = []
        for bonusType in QUALIFIER_TYPE_INDEX:
            bonusTypeSelected.append(self.__filter.selectedBonuses[bonusType])

        for group, _ in self.__groupsMap[self.__filter.currentType]:
            groupsList.append(group)

        if self.__filter.currentType != CUSTOMIZATION_TYPE.CAMOUFLAGE:
            groupsSelectIndex = groupsList.index(self.__filter.currentGroup)
            enableGroupFilter = self.__filter.isGroupFilterEnabled()
        else:
            groupsSelectIndex = 0
            enableGroupFilter = True
        return {'bonusTypeSelected': bonusTypeSelected,
         'groupsSelectIndex': groupsSelectIndex,
         'purchaseTypeSelectedIndex': PURCHASE_TYPE.ALL.index(self.__filter.purchaseType),
         'enableGroupFilter': enableGroupFilter}

    def __switchIGRFilter(self, disableGroupFilter):
        """ Turn on/off group filter.
        
        When IGR (purchase type) is selected, group filter has to become disabled, and
        it has to change it's value to 'All groups', but when user selects another purchase
        type, previous group value should be restored.
        
        :param disableGroupFilter: enable or disable group filter.
        """
        if self.__filter.isGroupFilterEnabled() == disableGroupFilter:
            self.__filter.toggleGroupFilterEnabled()
            if disableGroupFilter:
                groupToSet = DEFAULT_GROUP_VALUE
            else:
                groupToSet = self.__filter.currentGroup
            self.__filter.set(FILTER_TYPE.GROUP, groupToSet)
            updateVO = self.__createUpdateVO()
            self.as_setStateS({'bonusTypeSelected': updateVO['bonusTypeSelected'],
             'customizationTypeSelectedIndex': updateVO['groupsSelectIndex'],
             'purchaseTypeSelectedIndex': updateVO['purchaseTypeSelectedIndex'],
             'enableGroupFilter': updateVO['enableGroupFilter']})
