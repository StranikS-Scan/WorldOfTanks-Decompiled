# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBuildingCardPopover.py
import BigWorld
import ArenaType
import fortified_regions
import constants
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from constants import FORT_BUILDING_TYPE, CLAN_MEMBER_FLAGS
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeBuildingIndicatorsVOByDescr
from gui.Scaleform.daapi.view.meta.FortBuildingCardPopoverMeta import FortBuildingCardPopoverMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES as ALIAS, FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as FORT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import icons, text_styles, time_formatters
from helpers import i18n, time_utils
from shared_utils import CONST_CONTAINER

class FortBuildingCardPopover(FortViewHelper, FortBuildingCardPopoverMeta):

    class STATUS_COLORS(CONST_CONTAINER):
        FOUNDATION = ('foundation',
         'BB2B00',
         text_styles.alert,
         text_styles.main)
        MODERNIZATION = ('modernization',
         'BB6200',
         text_styles.neutral,
         text_styles.main)
        HALFDESTROY = ('halfDestroy',
         '400000',
         text_styles.error,
         text_styles.main)
        FREEZE = ('freeze',
         '400000',
         text_styles.error,
         text_styles.main)
        CGR = ('congratulation',
         'BB6200',
         text_styles.neutral,
         text_styles.main)

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
        self._buildingID = self.getBuildingIDbyUID(self._buildingUID)
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
                self.__orderTime = time_formatters.getTimeDurationStr(order.getProductionLeftTime())
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
        DialogsInterface.showDialog(BuyOrderDialogMeta(self.getOrderUIDbyID(currentOrderID)), None)
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
        garrisonLabel = text_styles.main(i18n.makeString(FORT.BUILDINGPOPOVER_GARRISONLABEL))
        oldBuilding = self.getBuildingUIDbyID(self.fortCtrl.getFort().getAssignedBuildingID(BigWorld.player().databaseID))
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
        fort = self.fortCtrl.getFort()
        isDefencePeriodActivated = fort.isDefenceHourEnabled()
        inProcess, _ = fort.getDefenceHourProcessing()
        isDefenceOn = isDefencePeriodActivated or inProcess
        buildingIcon = FortViewHelper.getPopoverIconSource(self._buildingUID, self.__buildingLevel, isDefenceOn=isDefenceOn)
        result = {'buildingName': i18n.makeString(FORT.buildings_buildingname(self._buildingUID)),
         'buildingIcon': buildingIcon}
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
        if self.__progress is ALIAS.STATE_BUILDING and isDefencePeriodActivated:
            nextMapTimestamp, nextMapID, curMapID = self.fortCtrl.getFort().getBuildingMaps(self._buildingID)
            isMapsInfoEnabled = nextMapTimestamp > 0
            if self.__buildingLevel < fortified_regions.g_cache.defenceConditions.minRegionLevel:
                mapIcon = icons.alert()
                mapMsg = text_styles.alert(i18n.makeString(FORT.BUILDINGPOPOVER_MAPINFO_NOBATTLE))
                header = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTBUILDINGCARDPOPOVER_MAPINFO_NOBATTLE_HEADER)
                body = i18n.makeString(TOOLTIPS.FORTIFICATION_FORTBUILDINGCARDPOPOVER_MAPINFO_NOBATTLE_BODY)
                isToolTipSpecial = False
            elif isMapsInfoEnabled:
                currentMapUserName = self.__getMapUserName(curMapID)
                mapIcon = icons.info()
                mapMsg = text_styles.main(currentMapUserName)
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
        demountTooltip = None
        upgradeBtnEnable = False
        upgradeTooltip = ''
        if self._isVisibleDemountBtn(self.__buildingDescr):
            demountEnabling = self._isEnableDemountBtn(self.__buildingDescr)
            if not self._isTutorial():
                demountTooltip = TOOLTIPS.FORTIFICATION_POPOVER_DEMOUNTBTN
        if self._isEnableModernizationBtnByDamaged(self.__buildingDescr):
            upgradeBtnEnable = True
            upgradeTooltip = TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEFOUNDATIONBTN
        if upgradeBtnEnable and not self._isEnableModernizationBtnByProgress(self.__buildingDescr):
            upgradeBtnEnable = False
            upgradeTooltip = TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEFOUNDATIONBTN_DISABLED
        self.as_setModernizationDestructionEnablingS(upgradeBtnEnable, demountEnabling, upgradeTooltip, demountTooltip)
        return

    def __disableModernizationAndDestroy(self):
        self.as_setModernizationDestructionEnablingS(False, False, TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEBTN_DISABLEDBYBATTLE, TOOLTIPS.FORTIFICATION_POPOVER_DEMOUNTBTNDISABLED)

    def __getBodyStatus(self, status, headerStyle, bodyStyle):
        headerLbl = headerStyle(i18n.makeString(FORT.buildingpopover_header_titlestatus(status)))
        if self.__isCommander:
            bodyLbl = bodyStyle(i18n.makeString(FORT.buildingpopover_commanderstatus_bodystatus(status)))
        else:
            bodyLbl = bodyStyle(i18n.makeString(FORT.buildingpopover_soldierstatus_bodystatus(status)))
        return (headerLbl, bodyLbl)

    def __makeHeaderStatusMessage(self):
        headerLbl = ''
        bodyLbl = ''
        status, filterColor, headerStyle, bodyStyle = self.STATUS_COLORS.FOUNDATION
        if self.__progress != ALIAS.STATE_BUILDING:
            status, filterColor, headerStyle, bodyStyle = self.STATUS_COLORS.FOUNDATION
            headerLbl, bodyLbl = self.__getBodyStatus(status, headerStyle, bodyStyle)
        elif self._isBaseBuilding:
            if self._isFortFrozen():
                status, filterColor, headerStyle, bodyStyle = self.STATUS_COLORS.FREEZE
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerStyle, bodyStyle)
            elif self._isBaseBuildingDamaged():
                status, filterColor, headerStyle, bodyStyle = self.STATUS_COLORS.HALFDESTROY
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerStyle, bodyStyle)
        elif self._isBuildingDamaged(self.__buildingDescr):
            status, filterColor, headerStyle, bodyStyle = self.STATUS_COLORS.HALFDESTROY
            headerLbl, bodyLbl = self.__getBodyStatus(status, headerStyle, bodyStyle)
        elif self.__canUpgrade and self._isEnableModernizationBtnByDamaged(self.__buildingDescr):
            if self.__congratMessage:
                status, filterColor, headerStyle, bodyStyle = self.STATUS_COLORS.CGR
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerStyle, bodyStyle)
            else:
                status, filterColor, headerStyle, bodyStyle = self.STATUS_COLORS.MODERNIZATION
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerStyle, bodyStyle)
        return (headerLbl, bodyLbl, filterColor)

    def __prepareIndicatorData(self):
        return makeBuildingIndicatorsVOByDescr(self.__buildingDescr)

    def __prepareDefResInfo(self):
        result = {}
        icon = None
        level = None
        showAlertIcon = False
        alertIconTooltip = ''
        if self._isBaseBuilding:
            defResTitle = text_styles.middleTitle(i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESINFO_BASEBUILDINGTITLE))
            defresDescr = text_styles.main(i18n.makeString(FORT.buildings_defresinfo(self._buildingUID)))
        else:
            order = self.fortCtrl.getFort().getOrder(self.__orderID)
            icon = order.icon
            level = order.level
            defResTitle = text_styles.middleTitle(i18n.makeString('#fortifications:General/orderType/%s' % self.getOrderUIDbyID(self.__orderID)))
            defresDescr = order.description
            showAlertIcon, alertIconTooltip = self._showOrderAlertIcon(order)
        result['showAlertIcon'] = showAlertIcon
        result['alertIconTooltip'] = alertIconTooltip
        result['title'] = defResTitle
        result['description'] = defresDescr
        result['iconSource'] = icon
        result['iconLevel'] = level
        if self.__orderID in constants.FORT_ORDER_TYPE.CONSUMABLES:
            result['orderID'] = self.__orderID
        return result

    def __prepareActionData(self):
        result = {}
        enableActionBtn = False
        if self._isBaseBuilding:
            if self.__isCommander:
                result['currentState'] = self.ACTION_STATES.BASE_COMMANDER
                resultConcat = ''.join((text_styles.main(i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_DIRECTIONOPENED)), text_styles.neutral(self.__directionOpened)))
                result['generalLabel'] = resultConcat
                result['actionButtonLbl'] = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_MANAGEMENT)
                enableActionBtn = True
            else:
                result['currentState'] = self.ACTION_STATES.BASE_NOT_COMMANDER
                resultConcat = ''.join((text_styles.main(i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_DIRECTIONOPENED)), text_styles.neutral(self.__directionOpened)))
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
                    orderTimeIcon = icons.alert()
                    orderTimeMsg = text_styles.alert(overTime)
                    orderTime = i18n.makeString(orderTimeIcon + ' ' + orderTimeMsg)
                else:
                    overTime = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPARETIMEOVER)
                    overTime = overTime + self.__orderTime
                    orderTime = text_styles.neutral(overTime)
                orderTimer = ''.join((text_styles.main(i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPARINGDEFRES)), text_styles.neutral(orderCount)))
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
                    orderName = i18n.makeString(FORT.orders_orderpopover_ordertype(self.getOrderUIDbyID(self.__orderID)))
                    result['toolTipData'] = i18n.makeString(TOOLTIPS.FORTIFICATION_POPOVER_PREPAREORDERENABLE, orderName=orderName)
        else:
            result['currentState'] = self.ACTION_STATES.NOT_BASE_NOT_COMMANDER
            result['generalLabel'] = 'unVISIBLE'
            result['actionButtonLbl'] = 'unVISIBLE'
        result['enableActionButton'] = enableActionBtn and not self.__isTutorial
        return result

    def __makeGeneralActionLabel(self):
        formatter = text_styles.standard
        if self.__buildingCurrentCapacity > 0:
            formatter = text_styles.neutral
        currCapacityColor = formatter(str(self.__buildingCurrentCapacity))
        generalLabel = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPAREDDEFRES, currentValue=currCapacityColor)
        resultGeneralLabel = text_styles.standard(generalLabel)
        return resultGeneralLabel
