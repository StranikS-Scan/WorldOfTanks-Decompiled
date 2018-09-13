# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBuildingCardPopover.py
import BigWorld
from constants import FORT_BUILDING_TYPE, CLAN_MEMBER_FLAGS
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortBuildingCardPopoverMeta import FortBuildingCardPopoverMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES as ALIAS, FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as FORT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import events
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils import CONST_CONTAINER
from helpers import i18n, time_utils

class FortBuildingCardPopover(View, SmartPopOverView, FortViewHelper, FortBuildingCardPopoverMeta):

    class STATUS_COLORS(CONST_CONTAINER):
        FOUNDATION = ('foundation',
         'BB2B00',
         fort_text.ALERT_TEXT,
         fort_text.MAIN_TEXT)
        MODERNIZATION = ('modernization',
         'BB6200',
         fort_text.NEUTRAL_TEXT,
         fort_text.MAIN_TEXT)
        HALFDESTROY = ('halfDestroy',
         '400000',
         fort_text.MAIN_TEXT,
         fort_text.MAIN_TEXT)
        FREEZE = ('freeze',
         '400000',
         fort_text.ERROR_TEXT,
         fort_text.MAIN_TEXT)
        CGR = ('congratulation',
         'BB6200',
         fort_text.NEUTRAL_TEXT,
         fort_text.MAIN_TEXT)

    class ACTION_STATES(CONST_CONTAINER):
        BASE_NOT_COMMANDER = 1
        BASE_COMMANDER = 2
        NOT_BASE_NOT_COMMANDER = 3
        NOT_BASE_COMMANDER_ORDERED = 4
        NOT_BASE_COMMANDER_NOT_ORDERED = 5

    def __init__(self, ctx):
        super(FortBuildingCardPopover, self).__init__()
        self._setKeyPoint(ctx.get('inXcoordinate'), ctx.get('inYcoordinate'))
        data = ctx.get('data', None)
        self._buildingUID = data.uid
        self._orderCooldownCallback = None
        return

    def _populate(self):
        super(FortBuildingCardPopover, self)._populate()
        self.startFortListening()
        self.__updateData()

    def _dispose(self):
        self.__clearOrderCooldownCallback()
        self.stopFortListening()
        super(FortBuildingCardPopover, self)._dispose()

    def __updateData(self):
        self.__clearOrderCooldownCallback()
        self.__prepareData()
        self.__generateData()
        fort = self.fortCtrl.getFort()
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
        self.__isCommander = g_clanCache.isClanLeader or self.__isViceCommander
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
                self.__orderTime = fort_text.getTimeDurationStr(order.getProductionLeftTime())
                self.__orderCount = order.productionCount
        self.__directionOpened = len(self.fortCtrl.getFort().getOpenedDirections())
        self.__assignedPlayerCount = len(self.__buildingDescr.attachedPlayers)
        self.__maxPlayerCount = self.__buildingDescr.typeRef.attachedPlayersLimit
        baseBuildingDescr = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        self.__baseLevel = baseBuildingDescr.level
        return

    def openDirectionControlWindow(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_EVENT), scope=EVENT_BUS_SCOPE.LOBBY)

    def openUpgradeWindow(self, value):
        self.fireEvent(events.ShowViewEvent(ALIAS.FORT_MODERNIZATION_WINDOW_EVENT, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def openAssignedPlayersWindow(self, value):
        self.fireEvent(events.ShowViewEvent(ALIAS.FORT_FIXED_PLAYERS_WINDOW_EVENT, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def openDemountBuildingWindow(self, value):
        self.fireEvent(events.ShowWindowEvent(ALIAS.FORT_DEMOUNT_BUILDING_WINDOW_EVENT, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def openBuyOrderWindow(self):
        currentOrderID = self.fortCtrl.getFort().getBuildingOrder(self._buildingID)
        DialogsInterface.showDialog(BuyOrderDialogMeta(self.UI_ORDERS_BIND[currentOrderID]), None)
        return

    def _populate(self):
        super(FortBuildingCardPopover, self)._populate()
        self.startFortListening()
        self.__prepareData()
        self.__generateData()

    def _dispose(self):
        self.stopFortListening()
        super(FortBuildingCardPopover, self)._dispose()

    def onUpdated(self):
        self.__prepareData()
        self.__generateData()

    def onBuildingRemoved(self, buildingTypeID):
        if self._buildingID == buildingTypeID:
            self.destroy()

    def onBuildingsUpdated(self, buildingsTypeIDs, cooldownPassed = False):
        if self._buildingID in buildingsTypeIDs:
            self.__updateData()

    def __generateData(self):
        data = {'buildingType': self._buildingUID,
         'isCommander': self.__isCommander}
        assignedLbl = fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_ASSIGNPLAYERS))
        data['isTutorial'] = self.__isTutorial
        data['assignLbl'] = assignedLbl
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
        if upgradeBtnVisible and not self._isEnableModernizationBtn(self.__buildingDescr):
            upgradeBtnEnable = False
            localTooltip = TOOLTIPS.FORTIFICATION_POPOVER_UPGRADEFOUNDATIONBTN_DISABLED
        result['upgradeButtonToolTip'] = localTooltip
        result['showUpgradeButton'] = upgradeBtnVisible
        result['enableUpgradeBtn'] = upgradeBtnEnable
        isVisibleDemountBtn = self._isVisibleDemountBtn(self.__buildingDescr)
        result['isVisibleDemountBtn'] = isVisibleDemountBtn
        if isVisibleDemountBtn:
            result['enableDemountBtn'] = self._isEnableDemountBtn()
            result['demountBtnTooltip'] = TOOLTIPS.FORTIFICATION_POPOVER_DEMOUNTBTN
        header, body, filterColor = self.__makeHeaderStatusMessage()
        result['titleStatus'] = header
        result['bodyStatus'] = body
        result['glowColor'] = int(filterColor, 16)
        result['isModernization'] = self.__canUpgrade
        return result

    def __getBodyStatus(self, status, headerColor, bodyColor):
        bodyLbl = ''
        headerLbl = fort_text.getText(headerColor, i18n.makeString(FORT.buildingpopover_header_titlestatus(status)))
        if self.__isCommander:
            bodyLbl = fort_text.getText(bodyColor, i18n.makeString(FORT.buildingpopover_commanderstatus_bodystatus(status)))
        else:
            bodyLbl = fort_text.getText(bodyColor, i18n.makeString(FORT.buildingpopover_soldierstatus_bodystatus(status)))
        return (headerLbl, bodyLbl)

    def __makeHeaderStatusMessage(self):
        headerLbl = ''
        bodyLbl = ''
        status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.FOUNDATION
        if self.__progress != ALIAS.STATE_BUILDING:
            status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.FOUNDATION
            headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
        elif self.__hpVal < self.__hpTotalVal and self.__buildingLevel > 0:
            if self._isBaseBuilding:
                status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.FREEZE
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
            else:
                status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.HALFDESTROY
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
        elif self.__canUpgrade:
            if self.__congratMessage:
                status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.CGR
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
            else:
                status, filterColor, headerColor, bodyColor = self.STATUS_COLORS.MODERNIZATION
                headerLbl, bodyLbl = self.__getBodyStatus(status, headerColor, bodyColor)
        return (headerLbl, bodyLbl, filterColor)

    def __prepareIndicatorData(self):
        textStyle = fort_text.PURPLE_TEXT
        if self.__progress == ALIAS.STATE_FOUNDATION_DEF or self.__progress == ALIAS.STATE_FOUNDATION:
            textStyle = fort_text.ALERT_TEXT
        formattedHpValue = fort_text.getText(textStyle, str(BigWorld.wg_getIntegralFormat(self.__hpVal)))
        hpTotalFormatted = str(BigWorld.wg_getIntegralFormat(self.__hpTotalVal)) + ' '
        formattedHpTotal = fort_text.concatStyles(((fort_text.STANDARD_TEXT, hpTotalFormatted), (fort_text.NUT_ICON,)))
        formattedDefResValue = fort_text.getText(fort_text.PURPLE_TEXT, str(BigWorld.wg_getIntegralFormat(self.__defResVal)))
        maxDefDerFormatted = str(BigWorld.wg_getIntegralFormat(self.__maxDefResVal)) + ' '
        formattedDefResTotal = fort_text.concatStyles(((fort_text.STANDARD_TEXT, maxDefDerFormatted), (fort_text.NUT_ICON,)))
        result = {}
        result['hpLabel'] = i18n.makeString(FORT.BUILDINGPOPOVER_INDICATORS_HPLBL)
        result['defResLabel'] = i18n.makeString(FORT.BUILDINGPOPOVER_INDICATORS_DEFRESLBL)
        result['hpCurrentValue'] = self.__hpVal
        result['hpTotalValue'] = self.__hpTotalVal
        result['defResCurrentValue'] = self.__defResVal
        result['defResTotalValue'] = self.__maxDefResVal
        hpProgressLabels = {}
        hpProgressLabels['currentValue'] = formattedHpValue
        hpProgressLabels['totalValue'] = formattedHpTotal
        hpProgressLabels['separator'] = '/'
        storeProgressLabels = {}
        storeProgressLabels['currentValue'] = formattedDefResValue
        storeProgressLabels['totalValue'] = formattedDefResTotal
        storeProgressLabels['separator'] = '/'
        result['hpProgressLabels'] = hpProgressLabels
        result['defResProgressLabels'] = storeProgressLabels
        return result

    def __prepareDefResInfo(self):
        result = {}
        icon = None
        level = None
        isPermanent = False
        if self._isBaseBuilding:
            defResTitle = fort_text.getText(fort_text.MIDDLE_TITLE, i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESINFO_BASEBUILDINGTITLE))
            defresDescr = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORT.buildings_defresinfo(self._buildingUID)))
        else:
            order = self.fortCtrl.getFort().getOrder(self.__orderID)
            icon = order.icon
            level = order.level
            defResTitle = fort_text.getText(fort_text.MIDDLE_TITLE, i18n.makeString('#fortifications:General/orderType/%s' % self.UI_ORDERS_BIND[self.__orderID]))
            defresDescr = order.description
            isPermanent = order.isPermanent
        result['isPermanent'] = isPermanent
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
                textOne = ((fort_text.MAIN_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_DIRECTIONOPENED)), (fort_text.NEUTRAL_TEXT, self.__directionOpened))
                resultConcat = fort_text.concatStyles(textOne)
                result['generalLabel'] = resultConcat
                result['actionButtonLbl'] = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_MANAGEMENT)
                enableActionBtn = True
            else:
                result['currentState'] = self.ACTION_STATES.BASE_NOT_COMMANDER
                textOne = ((fort_text.MAIN_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_DIRECTIONOPENED)), (fort_text.NEUTRAL_TEXT, self.__directionOpened))
                resultConcat = fort_text.concatStyles(textOne)
                result['generalLabel'] = resultConcat
        elif self.__isCommander:
            if self.__orderTime is not None:
                result['currentState'] = self.ACTION_STATES.NOT_BASE_COMMANDER_ORDERED
                orderTimer = fort_text.concatStyles(((fort_text.MAIN_TEXT, i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPARINGDEFRES)), (fort_text.NEUTRAL_TEXT, self.__orderCount)))
                overTime = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPARETIMEOVER)
                overTime = overTime + self.__orderTime
                orderTime = fort_text.getText(fort_text.NEUTRAL_TEXT, overTime)
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
        capacityTextColor = fort_text.STANDARD_TEXT
        if self.__buildingCurrentCapacity > 0:
            capacityTextColor = fort_text.NEUTRAL_TEXT
        currCapacityColor = fort_text.getText(capacityTextColor, str(self.__buildingCurrentCapacity))
        generalLabel = i18n.makeString(FORT.BUILDINGPOPOVER_DEFRESACTIONS_PREPAREDDEFRES, currentValue=currCapacityColor, totalValue=str(self.__buildingTotalCapacity))
        resultGeneralLabel = fort_text.getText(fort_text.STANDARD_TEXT, generalLabel)
        return resultGeneralLabel
