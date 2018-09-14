# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBuildingCardPopover.py
import BigWorld
import ArenaType
import fortified_regions
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from constants import FORT_BUILDING_TYPE, CLAN_MEMBER_FLAGS
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeBuildingIndicatorsVOByDescr
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortBuildingCardPopoverMeta import FortBuildingCardPopoverMeta
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES as ALIAS, FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as FORT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils import CONST_CONTAINER
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, time_utils

class FortBuildingCardPopover(View, SmartPopOverView, FortViewHelper, FortBuildingCardPopoverMeta, AppRef):

    class STATUS_COLORS(CONST_CONTAINER):
        FOUNDATION = ('foundation',
         'BB2B00',
         TextType.ALERT_TEXT,
         TextType.MAIN_TEXT)
        MODERNIZATION = ('modernization',
         'BB6200',
         TextType.NEUTRAL_TEXT,
         TextType.MAIN_TEXT)
        HALFDESTROY = ('halfDestroy',
         '400000',
         TextType.ERROR_TEXT,
         TextType.MAIN_TEXT)
        FREEZE = ('freeze',
         '400000',
         TextType.ERROR_TEXT,
         TextType.MAIN_TEXT)
        CGR = ('congratulation',
         'BB6200',
         TextType.NEUTRAL_TEXT,
         TextType.MAIN_TEXT)

    class ACTION_STATES(CONST_CONTAINER):
        BASE_NOT_COMMANDER = 1
        BASE_COMMANDER = 2
        NOT_BASE_NOT_COMMANDER = 3
        NOT_BASE_COMMANDER_ORDERED = 4
        NOT_BASE_COMMANDER_NOT_ORDERED = 5

    def __init__(self, ctx = None):
        super(FortBuildingCardPopover, self).__init__()
        data = ctx.get('data', None)
        self._buildingUID = data.uid
        self._orderCooldownCallback = None
        return

    def _populate(self):
        super(FortBuildingCardPopover, self)._populate()
        self.startFortListening()
        self.__updateData()
        self.__setButtonsStates()

    def _dispose(self):
        self.__clearOrderCooldownCallback()
        self.stopFortListening()
        super(FortBuildingCardPopover, self)._dispose()

    def __updateData(self):
        self.__clearOrderCooldownCallback()
        self.__prepareData()
        self.__generateData()
        self.__setButtonsStates()
        fort = self.fortCtrl.getFort()
        if self.__orderID:
            order = fort.getOrder(self.__orderID)
            delta = order.getProductionLeftTime()
            if delta > time_utils.ONE_DAY:
                period = time_utils.ONE_DAY
            elif delta > time_utils.ONE_HOUR:
                period = time_utils.ONE_HOUR
            else:
                period = time_utils.ONE_MINUTE
            timer = delta % period or period
            if timer > 0:
                self._orderCooldownCallback = BigWorld.callback(timer, self.__updateData)

    def __clearOrderCooldownCallback(self):
        if self._orderCooldownCallback is not None:
            BigWorld.cancelCallback(self._orderCooldownCallback)
            self._orderCooldownCallback = None
        return

    def __prepareData(self):
        self.__isTutorial = not self.fortCtrl.getFort().isStartingScriptDone()
        self._buildingID = self.UI_BUILDINGS_BIND.index(self._buildingUID)
        self.__congratMessage = False
        limits = self.fortCtrl.getLimits()
        canUpgrade, _ = limits.canUpgrade(self._buildingID)
        self.__canUpgrade = canUpgrade and self._isAvailableBlinking()
        if self._buildingID not in self.fortCtrl.getUpgradeVisitedBuildings() and self.__canUpgrade and self._isAvailableBlinking():
            self.__congratMessage = True
        self._isBaseBuilding = self._buildingUID == ALIAS.FORT_BASE_BUILDING
        self.__isViceCommander = g_clanCache.clanRole == CLAN_MEMBER_FLAGS.VICE_LEADER
        self.__isCommander = self.fortCtrl.getPermissions().canUpgradeBuilding()
        self.__buildingDescr = self.fortCtrl.getFort().getBuilding(self._buildingID)
        self.__buildingLevel = self.__buildingDescr.level
        self.__hpVal = self.__buildingDescr.hp
        self.__hpTotalVal = self.__buildingDescr.levelRef.hp
        self.__defResVal = self.__buildingDescr.storage
        self.__maxDefResVal = self.__buildingDescr.levelRef.storage
        self.__progress = ALIAS.STATE_BUILDING if self.__buildingDescr.level else ALIAS.STATE_FOUNDATION_DEF
        self.__orderID = self.fortCtrl.getFort().getBuildingOrder(self._buildingID)
        self.__orderTime = None
        self.__orderCount = 0
        self.__buildingCurrentCapacity = 0
        self.__orderLevel = 0
        self.__buildingTotalCapacity = 0
        if self.__orderID is not None:
            order = self.fortCtrl.getFort().getOrder(self.__orderID)
            self.__buildingTotalCapacity = self.__buildingDescr.levelRef.maxOrdersCount
            self.__buildingCurrentCapacity = order.count
            self.__orderLevel = order.level
            if order.inProgress:
                self.__orderTime = self.app.utilsManager.textManager.getTimeDurationStr(order.getProductionLeftTime())
                self.__orderCount = order.productionCount
        self.__directionOpened = len(self.fortCtrl.getFort().getOpenedDirections())
        self.__assignedPlayerCount = len(self.__buildingDescr.attachedPlayers)
        self.__maxPlayerCount = self.__buildingDescr.typeRef.attachedPlayersLimit
        baseBuildingDescr = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        self.__baseLevel = baseBuildingDescr.level
        return

    def openDirectionControlWindow(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)

    def openUpgradeWindow(self, value):
        self.fireEvent(events.LoadViewEvent(ALIAS.FORT_MODERNIZATION_WINDOW_ALIAS, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def openAssignedPlayersWindow(self, value):
        self.fireEvent(events.LoadViewEvent(ALIAS.FORT_FIXED_PLAYERS_WINDOW_ALIAS, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def openDemountBuildingWindow(self, value):
        self.fireEvent(events.LoadViewEvent(ALIAS.FORT_DEMOUNT_BUILDING_WINDOW, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def openBuyOrderWindow(self):
        currentOrderID = self.fortCtrl.getFort().getBuildingOrder(self._buildingID)
        DialogsInterface.showDialog(BuyOrderDialogMeta(self.UI_ORDERS_BIND[currentOrderID]), None)
        return

    def onBuildingsUpdated(self, buildingsTypeIDs, cooldownPassed = False):
        if self._buildingID in buildingsTypeIDs:
            self.__updateData()

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if self._buildingID == buildingTypeID:
            if reason == BUILDING_UPDATE_REASON.DELETED:
                self.destroy()
            else:
                self.__updateData()

    def onDefenceHourStateChanged(self):
        self.__setButtonsStates()

    def __setButtonsStates(self):
        if self.__buildingDescr.direction in self.fortCtrl.getFort().getDirectionsInBattle():
            self.__disableModernizationAndDestroy()
        else:
            self.__setDefaultEnabling()

    def __generateData(self):
        data = {'buildingType': self._buildingUID}
        assignedLbl = i18n.makeString(FORT.BUILDINGPOPOVER_ASSIGNPLAYERS)
        garrisonLabel = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_GARRISONLABEL))
        oldBuilding = self.UI_BUILDINGS_BIND[self.fortCtrl.getFort().getAssignedBuildingID(BigWorld.player().databaseID)]
        isAssigned = self._buildingUID == oldBuilding
        data['isTutorial'] = self.__isTutorial
        data['assignLbl'] = assignedLbl
        data['garrisonLbl'] = garrisonLabel
        data['isAssigned'] = isAssigned
        data['canUpgradeBuilding'] = self.fortCtrl.getPermissions().canUpgradeBuilding()
        data['canAddOrder'] = self.fortCtrl.getPermissions().canAddOrder()
        data['playerCount'] = self.__assignedPlayerCount
        data['maxPlayerCount'] = self.__maxPlayerCount
        data['buildingHeader'] = self.__prepareHeaderData()
        data['buildingIndicators'] = self.__prepareIndicatorData()
        data['defresInfo'] = self.__prepareDefResInfo()
        data['actionData'] = self.__prepareActionData()
        self.as_setDataS(data)

    def onWindowClose(self):
        self.destroy()

    def __convertBuildLevel(self, level):
        return str(fort_formatters.getTextLevel(level))

    def __prepareHeaderData(self):
        result = {'buildingName': i18n.makeString(FORT.buildings_buildingname(self._buildingUID)),
         'buildingIcon': self._buildingUID}
        buildLevel = self.__convertBuildLevel(self.__buildingLevel)
        result['buildLevel'] = i18n.makeString(FORT.BUILDINGPOPOVER_HEADER_LEVELSLBL, buildLevel=buildLevel)
        upgradeBtnVisible = False
        upgradeBtnEnable = False
        localTooltip = ''
        if self._canModernization(self.__buildingDescr):
            upgradeBtnVisible = upgradeBtnEnable = True
            localTooltip = TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEFOUNDATIONBTN
        if upgradeBtnVisible:
            if not self._isEnableModernizationBtnByDamaged(self.__buildingDescr):
                upgradeBtnEnable = False
                localTooltip = TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEBTN_DISABLEDBYDESTROY
            elif not self._isEnableModernizationBtnByProgress(self.__buildingDescr):
                upgradeBtnEnable = False
                localTooltip = TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEFOUNDATIONBTN_DISABLED
        result['upgradeButtonToolTip'] = localTooltip
        result['showUpgradeButton'] = upgradeBtnVisible
        result['enableUpgradeBtn'] = upgradeBtnEnable
        isVisibleDemountBtn = self._isVisibleDemountBtn(self.__buildingDescr)
        result['isVisibleDemountBtn'] = isVisibleDemountBtn
        if isVisibleDemountBtn:
            result['enableDemountBtn'] = self._isEnableDemountBtn(self.__buildingDescr)
            result['demountBtnTooltip'] = TOOLTIPS.FORTIFICATION_POPOVER_DEMOUNTBTN
        header, body, filterColor = self.__makeHeaderStatusMessage()
        result['titleStatus'] = header
        result['bodyStatus'] = body
        result['glowColor'] = int(filterColor, 16)
        result['isModernization'] = self.__canUpgrade
        result['canDeleteBuilding'] = self.fortCtrl.getPermissions().canDeleteBuilding()
        isDefencePeriodActivated = self.fortCtrl.getFort().isDefenceHourEnabled()
        if self.__progress is ALIAS.STATE_BUILDING and isDefencePeriodActivated:
            nextMapTimestamp, nextMapID, curMapID = self.fortCtrl.getFort().getBuildingMaps(self._buildingID)
            isMapsInfoEnabled = nextMapTimestamp > 0
            if self.__buildingLevel < fortified_regions.g_cache.defenceConditions.minRegionLevel:
                mapIcon = self.app.utilsManager.textManager.getIcon(TextIcons.ALERT_ICON)
                mapMsg = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_MAPINFO_NOBATTLE))
                header = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTBUILDINGCARDPOPOVER_MAPINFO_NOBATTLE_HEADER)
                body = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTBUILDINGCARDPOPOVER_MAPINFO_NOBATTLE_BODY)
                isToolTipSpecial = False
            elif isMapsInfoEnabled:
                currentMapUserName = self.__getMapUserName(curMapID)
                mapIcon = self.app.utilsManager.textManager.getIcon(TextIcons.INFO_ICON)
                mapMsg = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, currentMapUserName)
                header = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTBUILDINGCARDPOPOVER_MAPINFO_HEADER, currentMap=currentMapUserName)
                body = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTBUILDINGCARDPOPOVER_MAPINFO_BODY, nextMap=self.__getMapUserName(nextMapID), changeDate=BigWorld.wg_getLongDateFormat(nextMapTimestamp), changeTime=BigWorld.wg_getShortTimeFormat(nextMapTimestamp))
                isToolTipSpecial = True
            else:
                mapIcon = mapMsg = ''
                isToolTipSpecial = False
            mapInfo = i18n.makeString(mapIcon + ' ' + mapMsg)
            result['mapInfo'] = mapInfo
            result['isToolTipSpecial'] = isToolTipSpecial
            result['tooltipData'] = {'mapName': header,
             'description': body,
             'imageURL': self.__getMapImage(curMapID)}
        return result

    @classmethod
    def __getMapUserName(cls, arenaTypeID):
        if arenaTypeID in ArenaType.g_cache:
            return ArenaType.g_cache[arenaTypeID].name
        return ''

    @classmethod
    def __getMapImage(cls, arenaTypeID):
        if arenaTypeID in ArenaType.g_cache:
            return '../maps/icons/map/small/%s.png' % ArenaType.g_cache[arenaTypeID].geometryName
        return ''

    def __setDefaultEnabling(self):
        demountEnabling = False
        demountTooltip = ''
        upgradeBtnEnable = False
        upgradeTooltip = ''
        if self._isVisibleDemountBtn(self.__buildingDescr):
            demountEnabling = self._isEnableDemountBtn(self.__buildingDescr)
            demountTooltip = TOOLTIPS.FORTIFICATION_POPOVER_DEMOUNTBTN
        if self._isEnableModernizationBtnByDamaged(self.__buildingDescr):
            upgradeBtnEnable = True
            upgradeTooltip = TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEFOUNDATIONBTN
        if upgradeBtnEnable and not self._isEnableModernizationBtnByProgress(self.__buildingDescr):
            upgradeBtnEnable = False
            upgradeTooltip = TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEFOUNDATIONBTN_DISABLED
        self.as_setModernizationDestructionEnablingS(upgradeBtnEnable, demountEnabling, upgradeTooltip, demountTooltip)

    def __disableModernizationAndDestroy(self):
        self.as_setModernizationDestructionEnablingS(False, False, TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEBTN_DISABLEDBYBATTLE, TOOLTIPS.FORTIFICATION_POPOVER_DEMOUNTBTNDISABLED)

    def __getBodyStatus(self, status, headerColor, bodyColor):
        bodyLbl = ''
        headerLbl = self.app.utilsManager.textManager.getText(headerColor, i18n.makeString(FORT.buildingpopover_header_titlestatus(status)))
        if self.__isCommander:
            bodyLbl = self.app.utilsManager.textManager.getText(bodyColor, i18n.makeString(FORT.buildingpopover_commanderstatus_bodystatus(status)))
        else:
            bodyLbl = self.app.utilsManager.textManager.getText(bodyColor, i18n.makeString(FORT.buildingpopover_soldierstatus_bodystatus(status)))
        return (headerLbl, bodyLbl)

    def __makeHeaderStatusMessage(self):
        headerLbl = ''
        bodyLbl = ''
        status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.FOUNDATION
        if self.__progress != ALIAS.STATE_BUILDING:
            status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.FOUNDATION
            headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
        elif self._isBaseBuilding:
            if self._isFortFrozen():
                status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.FREEZE
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
            elif self._isBaseBuildingDamaged():
                status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.HALFDESTROY
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
        elif self._isBuildingDamaged(self.__buildingDescr):
            status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.HALFDESTROY
            headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
        elif self.__canUpgrade and self._isEnableModernizationBtnByDamaged(self.__buildingDescr):
            if self.__congratMessage:
                status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.CGR
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
            else:
                status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.MODERNIZATION
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
        return (headerLbl, bodyLbl, filterColor)

    def __prepareIndicatorData(self):
        return makeBuildingIndicatorsVOByDescr(self.__buildingDescr)

    def __prepareDefResInfo(self):
        result = {}
        icon = None
        level = None
        showAlertIcon = False
        if self._isBaseBuilding:
            defResTitle = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESINFO_BASEBUILDINGTITLE))
            defresDescr = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(FORT.buildings_defresinfo(self._buildingUID)))
        else:
            order = self.fortCtrl.getFort().getOrder(self.__orderID)
            icon = order.icon
            level = order.level
            defResTitle = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString('#fortifications:General/orderType/%s' % self.UI_ORDERS_BIND[self.__orderID]))
            defresDescr = order.description
            showAlertIcon = self._showOrderAlertIcon(order)
        result['showAlertIcon'] = showAlertIcon
        result['title'] = defResTitle
        result['description'] = defresDescr
        result['iconSource'] = icon
        result['iconLevel'] = level
        return result

    def __prepareActionData(self):
        result = {}
        enableActionBtn = False
        if self._isBaseBuilding:
            if self.__isCommander:
                result['currentState'] = self.ACTION_STATES.BASE_COMMANDER
                textOne = ((TextType.MAIN_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_DIRECTIONOPENED)), (TextType.NEUTRAL_TEXT, self.__directionOpened))
                resultConcat = self.app.utilsManager.textManager.concatStyles(textOne)
                result['generalLabel'] = resultConcat
                result['actionButtonLbl'] = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_MANAGEMENT)
                enableActionBtn = True
            else:
                result['currentState'] = self.ACTION_STATES.BASE_NOT_COMMANDER
                textOne = ((TextType.MAIN_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_DIRECTIONOPENED)), (TextType.NEUTRAL_TEXT, self.__directionOpened))
                resultConcat = self.app.utilsManager.textManager.concatStyles(textOne)
                result['generalLabel'] = resultConcat
        elif self.__isCommander:
            if self.__buildingDescr.orderInProduction:
                orderCount = self.__buildingDescr.orderInProduction.get('count', 0)
                result['currentState'] = self.ACTION_STATES.NOT_BASE_COMMANDER_ORDERED
                if self._isProductionInPause(self.__buildingDescr):
                    result['productionInPause'] = True
                    title = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPROCESS_INPAUSE_HEADER)
                    body = i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPROCESS_INPAUSE_BODY)
                    result['pauseReasonTooltip'] = [title, body]
                    overTime = i18n.makeString(FORT.BUILDINGPOPOVER_ORDERPROCESS_INPAUSE)
                    orderTimeIcon = self.app.utilsManager.textManager.getIcon(TextIcons.ALERT_ICON)
                    orderTimeMsg = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, overTime)
                    orderTime = i18n.makeString(orderTimeIcon + ' ' + orderTimeMsg)
                else:
                    overTime = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPARETIMEOVER)
                    overTime = overTime + self.__orderTime
                    orderTime = self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, overTime)
                orderTimer = self.app.utilsManager.textManager.concatStyles(((TextType.MAIN_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPARINGDEFRES)), (TextType.NEUTRAL_TEXT, orderCount)))
                result['orderTimer'] = orderTimer
                result['timeOver'] = orderTime
                result['generalLabel'] = self.__makeGeneralActionLabel()
            else:
                result['currentState'] = self.ACTION_STATES.NOT_BASE_COMMANDER_NOT_ORDERED
                result['generalLabel'] = self.__makeGeneralActionLabel()
                result['actionButtonLbl'] = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_REQUESTDEFRES)
                enableActionBtn = True
                order = self.fortCtrl.getFort().getOrder(self.__orderID)
                if self.__defResVal < order.productionCost:
                    enableActionBtn = False
                    result['toolTipData'] = TOOLTIPS.FORTIFICATION_POPOVER_PREPAREORDERDISABLE
                if order.maxCount <= order.count:
                    enableActionBtn = False
                    result['toolTipData'] = TOOLTIPS.FORTIFICATION_POPOVER_PREPAREORDEROVERLOAD
                if self._isBuildingDamaged(self.__buildingDescr) or self._isBaseBuildingDamaged() or self._isFortFrozen():
                    enableActionBtn = False
                    header = TOOLTIPS.FORTIFICATION_ORDERPROCESS_NOTAVAILABLE_HEADER
                    body = TOOLTIPS.FORTIFICATION_ORDERPROCESS_NOTAVAILABLE_BODY
                    result['toolTipData'] = makeTooltip(header, body)
                if enableActionBtn:
                    orderName = i18n.makeString(FORT.orders_orderpopover_ordertype(self.UI_ORDERS_BIND[self.__orderID]))
                    result['toolTipData'] = i18n.makeString(TOOLTIPS.FORTIFICATION_POPOVER_PREPAREORDERENABLE, orderName=orderName)
        else:
            result['currentState'] = self.ACTION_STATES.NOT_BASE_NOT_COMMANDER
            result['generalLabel'] = 'unVISIBLE'
            result['actionButtonLbl'] = 'unVISIBLE'
        result['enableActionButton'] = enableActionBtn and not self.__isTutorial
        return result

    def __makeGeneralActionLabel(self):
        capacityTextColor = TextType.STANDARD_TEXT
        if self.__buildingCurrentCapacity > 0:
            capacityTextColor = TextType.NEUTRAL_TEXT
        currCapacityColor = self.app.utilsManager.textManager.getText(capacityTextColor, str(self.__buildingCurrentCapacity))
        generalLabel = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPAREDDEFRES, currentValue=currCapacityColor)
        resultGeneralLabel = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, generalLabel)
        return resultGeneralLabel
