# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortModernizationWindow.py
import BigWorld
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from adisp import process
from constants import FORT_BUILDING_TYPE, MAX_FORTIFICATION_LEVEL, FORT_ORDER_TYPE
from FortifiedRegionBase import BuildingDescr
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortModernizationWindowMeta import FortModernizationWindowMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.fortifications import isFortificationBattlesEnabled
from gui.shared.fortifications.FortOrder import FortOrder
from gui.shared.fortifications.context import UpgradeCtx
from gui.shared.fortifications.settings import FORT_RESTRICTION, FORT_BATTLE_DIVISIONS
from gui.shared import events
from gui.shared.formatters import icons, text_styles
from helpers import i18n
from gui import DialogsInterface

class MAX_LEVEL:
    MAX_BUILD_LEVEL = 4
    MAX_BASE_LEVEL_FIRST_ITERATION = 4
    MAX_BASE_LEVEL_SECOND_ITERATION = 5


class FortModernizationWindow(FortModernizationWindowMeta, FortViewHelper):

    def __init__(self, ctx = None):
        super(FortModernizationWindow, self).__init__()
        self.__uid = ctx.get('data', None)
        self.intBuildingID = None
        self._buildingDescr = None
        self.__buildingLevel = None
        self.nextLevel = None
        self.__baseBuildingLevel = None
        self.__progress = None
        self.__hpTotalVal = None
        self.__hpVal = None
        self.__defResVal = None
        self.__maxDerResVal = None
        self.__cost = None
        self.__defencePeriod = False
        self.__isFortBattleAvailable = isFortificationBattlesEnabled()
        return

    def __buildData(self):
        self.intBuildingID = self.getBuildingIDbyUID(self.__uid)
        self._buildingDescr = self.fortCtrl.getFort().getBuilding(self.intBuildingID)
        self.__buildingLevel = max(self._buildingDescr.level, 1)
        self.nextLevel = BuildingDescr(typeID=self.intBuildingID, level=self.__buildingLevel + 1)
        baseBuilding = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        self.__baseBuildingLevel = baseBuilding.level
        self.__progress = self._getProgress(self._buildingDescr.typeID, self.__buildingLevel)
        self.__hpTotalVal = self._buildingDescr.levelRef.hp
        self.__hpVal = self._buildingDescr.hp
        self.__defResVal = self._buildingDescr.storage
        self.__maxDerResVal = self._buildingDescr.levelRef.storage
        self.__cost = self._buildingDescr.levelRef.upgradeCost
        fort = self.fortCtrl.getFort()
        self.__defencePeriod = fort.isDefenceHourEnabled()
        self.as_setDataS(self.__makeData())

    def applyAction(self):
        if self.intBuildingID == FORT_BUILDING_TYPE.MILITARY_BASE and self.nextLevel.level == FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel:
            DialogsInterface.showDialog(I18nConfirmDialogMeta('fortModernizationAbsoluteDivision'), self.__confirmationClosed)
        else:
            self.__requestToUpgrade()

    def __confirmationClosed(self, result):
        if result:
            self.__requestToUpgrade()

    def updateWindow(self, ctx):
        self.__uid = ctx.get('data', None)
        self._updateView()
        return

    def _updateView(self):
        buildingName = i18n.makeString(FORTIFICATIONS.buildings_buildingname(self.__uid))
        windowTitle = i18n.makeString(FORTIFICATIONS.MODERNIZATION_WINDOWTITLE, buildingName=buildingName)
        self.as_windowTitleS(windowTitle)
        self.as_applyButtonLblS(FORTIFICATIONS.MODERNIZATION_APPLYBUTTON_LABEL)
        self.as_cancelButtonS(FORTIFICATIONS.MODERNIZATION_CANCELBUTTON_LABEL)
        self.__buildData()

    @process
    def __requestToUpgrade(self):
        building = self.fortCtrl.getFort().getBuilding(self.intBuildingID)
        result = yield self.fortProvider.sendRequest(UpgradeCtx(self.intBuildingID, waitingID='fort/building/upgrade'))
        if result:
            g_fortSoundController.playUpgradeBuilding()
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_MODERNIZATIONBUILDING, buildingName=building.userName, buildingLevel=building.getUserLevel(True), type=SystemMessages.SM_TYPE.Warning)
        self.destroy()

    def _populate(self):
        super(FortModernizationWindow, self)._populate()
        self.startFortListening()
        self._updateView()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        self.stopFortListening()
        self.__uid = None
        self.intBuildingID = None
        self._buildingDescr = None
        self.__buildingLevel = None
        self.nextLevel = None
        self.__baseBuildingLevel = None
        self.__progress = None
        self.__hpTotalVal = None
        self.__hpVal = None
        self.__defResVal = None
        self.__maxDerResVal = None
        self.__cost = None
        self.__defencePeriod = False
        super(FortModernizationWindow, self)._dispose()
        return

    def onUpdated(self, isFullUpdate):
        self.__buildData()

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if self.intBuildingID == buildingTypeID and reason == BUILDING_UPDATE_REASON.DELETED:
            self.destroy()

    def __makeData(self):
        baseBuildingMaxLevel = MAX_LEVEL.MAX_BASE_LEVEL_SECOND_ITERATION if self.__isFortBattleAvailable else MAX_LEVEL.MAX_BASE_LEVEL_FIRST_ITERATION
        result = {}
        cndBody = ''
        limits = self.fortCtrl.getLimits()
        canUpgrade, upgradeRestriction = limits.canUpgrade(self.intBuildingID)
        LOG_DEBUG(upgradeRestriction)
        cndPostfix = ''
        isCanModernization = canUpgrade
        conditionIcon = icons.checkmark()
        canUpgradeByDefPeriod = True
        isBaseBuilding = self.__uid == FORTIFICATION_ALIASES.FORT_BASE_BUILDING
        if self.__uid != FORTIFICATION_ALIASES.FORT_BASE_BUILDING:
            cndBody = i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_GENERALCONDITION, level=fort_formatters.getTextLevel(self.__buildingLevel + 1))
            if canUpgrade:
                isCanModernization = True
            else:
                isCanModernization = False
            if self.__buildingLevel == MAX_LEVEL.MAX_BUILD_LEVEL:
                if self.__isFortBattleAvailable:
                    cndBody = i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_DEFENCEPERIODANDBASEBUILDING, level=fort_formatters.getTextLevel(self.__buildingLevel + 1))
                    if not self.__defencePeriod or self.__baseBuildingLevel < MAX_LEVEL.MAX_BASE_LEVEL_SECOND_ITERATION:
                        cndPostfix = text_styles.error(i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
                        isCanModernization = False
                        canUpgradeByDefPeriod = False
                        conditionIcon = text_styles.standard('-')
                elif self.__buildingLevel == self.__baseBuildingLevel:
                    cndPostfix = text_styles.error(i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
            elif self.__buildingLevel == self.__baseBuildingLevel:
                cndPostfix = text_styles.error(i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
                isCanModernization = False
        elif self.__buildingLevel == baseBuildingMaxLevel:
            cndBody = i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_BASEBUILDINGFIVELEVEL)
            if not self.__defencePeriod and self.__isFortBattleAvailable:
                cndPostfix = text_styles.error(i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
                isCanModernization = False
                canUpgradeByDefPeriod = False
                conditionIcon = text_styles.standard('-')
            elif not self.__isFortBattleAvailable:
                isCanModernization = False
                canUpgradeByDefPeriod = False
                cndBody = text_styles.alert(i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_FORTMAXLEVEL))
                conditionIcon = ''
        prefixBody = text_styles.main(cndBody)
        result['condition'] = prefixBody + cndPostfix
        result['costUpgrade'] = text_styles.defRes(i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_COUNTCOST))
        result['intBuildingID'] = self.intBuildingID
        if not canUpgrade and upgradeRestriction != FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE:
            conditionIcon = text_styles.standard('-')
        if self._buildingDescr.storage < self.__cost:
            costMsg = text_styles.error(BigWorld.wg_getIntegralFormat(self.__cost))
            constIcon = icons.nut()
            costMsg = costMsg + ' ' + constIcon
        else:
            costMsg = fort_formatters.getDefRes(self.__cost, True)
        result['costValue'] = costMsg
        if cndBody != '':
            result['conditionIcon'] = conditionIcon
        result['canUpgrade'] = isCanModernization
        if not isCanModernization:
            btnToolTip = {}
            if not canUpgradeByDefPeriod and self.__isFortBattleAvailable:
                btnToolTip['header'] = i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_NOTACTIVATEDDEFPERIOD_HEADER)
                btnToolTip['body'] = i18n.makeString(i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_NOTACTIVATEDDEFPERIOD_BODY))
            else:
                btnToolTip['header'] = i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_APPLYBUTTON_HEADER)
                if not self.__isFortBattleAvailable and isBaseBuilding and self.__buildingLevel == baseBuildingMaxLevel:
                    btnToolTip['header'] = i18n.makeString('#tooltips:fortification/popOver/upgradeFoundationBtn_Disabled/header')
                    btnToolTip['body'] = i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_FORTMAXLEVEL)
                elif upgradeRestriction == FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE_AND_LOW_LEVEL:
                    btnToolTip['body'] = i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_APPLYBUTTON_LOWLEVELANDRESOURCE, baseLevel=fort_formatters.getTextLevel(self.__baseBuildingLevel + 1))
                elif upgradeRestriction == FORT_RESTRICTION.BUILDING_FORT_LEVEL_TOO_LOW:
                    btnToolTip['body'] = i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_APPLYBUTTON_LOWBASELEVEL, baseLevel=fort_formatters.getTextLevel(self.__baseBuildingLevel + 1))
                elif upgradeRestriction == FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE:
                    btnToolTip['body'] = i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_APPLYBUTTON_NETENOUGHRESOURCE)
            result['btnToolTip'] = btnToolTip
        fort = self.fortCtrl.getFort()
        newCount = 0
        resLeft = 0
        orderCount = 0
        if self.__uid != FORTIFICATION_ALIASES.FORT_BASE_BUILDING:
            order = fort.getOrder(self._buildingDescr.typeRef.orderType)
            orderCount = order.count
            newCount, resLeft = fort.recalculateOrder(order.orderID, order.count, order.level, order.level + 1)
        inProcess, _ = fort.getDefenceHourProcessing()
        isDefenceOn = fort.isDefenceHourEnabled() or inProcess
        before = {}
        before['buildingType'] = self.__uid
        before['buildingLevel'] = self.__buildingLevel
        before['buildingIcon'] = FortViewHelper.getMapIconSource(self.__uid, self.__buildingLevel, isDefenceOn=isDefenceOn)
        before['buildingIndicators'] = self.__prepareIndicatorData(isCanModernization, False)
        before['defResInfo'] = self.__prepareOrderInfo(False, orderCount, self.__buildingLevel)
        before['titleText'] = text_styles.middleTitle(i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_BEFORELABEL))
        result['beforeUpgradeData'] = before
        after = {}
        after['buildingType'] = self.__uid
        after['buildingLevel'] = self.__buildingLevel + 1
        after['buildingIcon'] = FortViewHelper.getMapIconSource(self.__uid, self.__buildingLevel + 1)
        after['buildingIndicators'] = self.__prepareIndicatorData(isCanModernization, True, resLeft)
        after['defResInfo'] = self.__prepareOrderInfo(True, newCount, self.__buildingLevel + 1)
        after['titleText'] = text_styles.middleTitle(i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_AFTERLABEL))
        result['afterUpgradeData'] = after
        return result

    def __prepareIndicatorData(self, isCanModernization, increment = False, resLeft = 0):
        if increment:
            hpTotalVal = self.nextLevel.levelRef.hp
            hpVal = self.nextLevel.hp
            defResVal = self.__defResVal - self.__cost + resLeft
            maxDerResVal = self.nextLevel.levelRef.storage
        else:
            hpTotalVal = self.__hpTotalVal
            hpVal = self.__hpVal
            defResVal = self.__defResVal
            maxDerResVal = self.__maxDerResVal
        formatter = text_styles.defRes
        if self.__progress == FORTIFICATION_ALIASES.STATE_FOUNDATION_DEF or self.__progress == FORTIFICATION_ALIASES.STATE_FOUNDATION:
            formatter = text_styles.alert
        if not isCanModernization and increment:
            currentHpLabel = text_styles.main('--')
            currentHpValue = 0
        else:
            currentHpLabel = str(BigWorld.wg_getIntegralFormat(hpVal))
            currentHpValue = hpVal
        FORMAT_PATTERN = '###'
        formattedHpValue = formatter(FORMAT_PATTERN)
        formatter = text_styles.standard
        if increment:
            formatter = text_styles.neutral
        formattedHpTotal = formatter(str(BigWorld.wg_getIntegralFormat(hpTotalVal)))
        formattedHpTotal += ' ' + icons.nut()
        if not isCanModernization and increment:
            currentDefResLabel = text_styles.main('--')
            currentDefResValue = 0
        else:
            currentDefResLabel = str(BigWorld.wg_getIntegralFormat(defResVal))
            currentDefResValue = defResVal
        defResValueFormatter = text_styles.alert(FORMAT_PATTERN) if defResVal > maxDerResVal else text_styles.defRes(FORMAT_PATTERN)
        formattedDefResTotal = formatter(str(BigWorld.wg_getIntegralFormat(maxDerResVal)))
        formattedDefResTotal += ' ' + icons.nut()
        result = {}
        result['hpLabel'] = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_INDICATORS_HPLBL)
        result['defResLabel'] = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_INDICATORS_DEFRESLBL)
        result['hpCurrentValue'] = currentHpValue
        result['hpTotalValue'] = hpTotalVal
        result['defResCurrentValue'] = currentDefResValue
        result['defResTotalValue'] = maxDerResVal
        hpProgressLabels = {}
        hpProgressLabels['currentValue'] = currentHpLabel
        hpProgressLabels['currentValueFormatter'] = formattedHpValue
        hpProgressLabels['totalValue'] = formattedHpTotal
        hpProgressLabels['separator'] = '/'
        storeProgressLabels = {}
        storeProgressLabels['currentValue'] = currentDefResLabel
        storeProgressLabels['currentValueFormatter'] = defResValueFormatter
        storeProgressLabels['totalValue'] = formattedDefResTotal
        storeProgressLabels['separator'] = '/'
        result['hpProgressLabels'] = hpProgressLabels
        result['defResProgressLabels'] = storeProgressLabels
        return result

    def __prepareOrderInfo(self, increment = False, orderCount = 0, orderLevel = 1):
        result = {}
        if self.intBuildingID == FORT_BUILDING_TYPE.MILITARY_BASE:
            if increment:
                building_bonus = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_HEADER_LEVELSLBL, buildLevel=fort_formatters.getTextLevel(min(self.__baseBuildingLevel + 1, MAX_FORTIFICATION_LEVEL)))
                defresDescr = ''.join((text_styles.neutral(building_bonus + ' '), text_styles.main(i18n.makeString(FORTIFICATIONS.BUILDINGS_MODERNIZATIONDESCR_BASE_BUILDING))))
            else:
                building_bonus = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_HEADER_LEVELSLBL, buildLevel=fort_formatters.getTextLevel(self.__baseBuildingLevel))
                defresDescr = ''.join((text_styles.standard(building_bonus + ' '), text_styles.standard(i18n.makeString(FORTIFICATIONS.BUILDINGS_MODERNIZATIONDESCR_BASE_BUILDING))))
        else:
            orderTypeID = self.fortCtrl.getFort().getBuildingOrder(self.intBuildingID)
            _, _, foundedLevel, orderData = self.fortCtrl.getFort().getOrderData(orderTypeID)
            if increment:
                bodyStyle = text_styles.main
                bonusStyle = text_styles.neutral
                foundedLevel += 1
                _, _, _, orderData = self.fortCtrl.getFort().getOrderData(orderTypeID, foundedLevel)
                textPadding = '     '
            else:
                bodyStyle = text_styles.standard
                bonusStyle = text_styles.standard
                textPadding = ''
            if orderTypeID == FORT_ORDER_TYPE.SPECIAL_MISSION:
                awardText = textPadding + i18n.makeString(FORTIFICATIONS.ORDERS_SPECIALMISSION_POSSIBLEAWARD) + ' '
                bonusDescr = i18n.makeString(FORTIFICATIONS.orders_specialmission_possibleaward_description_level(foundedLevel))
                defresDescr = ''.join((bonusStyle(awardText), bodyStyle(bonusDescr)))
            elif orderTypeID in FORT_ORDER_TYPE.CONSUMABLES:
                battleOrder = FortOrder(orderTypeID, level=orderLevel)
                defresDescr = fort_formatters.getBonusText(textPadding, self.__uid, ctx=dict(battleOrder.getParams()), textsStyle=(bonusStyle, bodyStyle))
            else:
                colorStyle = (bonusStyle, bodyStyle)
                bonus = str(abs(orderData.effectValue))
                defresDescr = fort_formatters.getBonusText('%s+%s%%' % (textPadding, bonus), self.__uid, colorStyle)
        result['ordersCount'] = orderCount
        result['description'] = defresDescr
        result['buildingType'] = self.__uid
        result['showAlertIcon'] = False
        isCombatOrderBuilding = self.__uid in [FORTIFICATION_ALIASES.FORT_ARTILLERY_SHOP_BUILDING, FORTIFICATION_ALIASES.FORT_BOMBER_SHOP_BUILDING]
        result['descriptionLink'] = increment and isCombatOrderBuilding
        if self.__uid != FORTIFICATION_ALIASES.FORT_BASE_BUILDING:
            order = self.fortCtrl.getFort().getOrder(self._buildingDescr.typeRef.orderType)
            result['iconSource'] = order.icon
            result['iconLevel'] = order.level if not increment else order.level + 1
        if increment and self.__uid != FORTIFICATION_ALIASES.FORT_BASE_BUILDING:
            result['infoIconSource'] = RES_ICONS.MAPS_ICONS_LIBRARY_INFORMATIONICON
            toolTipData = {}
            toolTipData['header'] = i18n.makeString(TOOLTIPS.FORTIFICATION_DEFRESICONINFO_HEADER)
            toolTipData['body'] = i18n.makeString(TOOLTIPS.FORTIFICATION_DEFRESICONINFO_BODY, testData='test py var')
            result['infoIconToolTipData'] = toolTipData
        return result

    def openOrderDetailsWindow(self):
        fort = self.fortCtrl.getFort()
        order = fort.getOrder(self._buildingDescr.typeRef.orderType)
        orderID = order.orderID
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, ctx={'orderID': orderID,
         'orderLevel': self.__buildingLevel}), scope=EVENT_BUS_SCOPE.LOBBY)
