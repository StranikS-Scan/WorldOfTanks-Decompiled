# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortModernizationWindow.py
import BigWorld
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from adisp import process
from constants import FORT_BUILDING_TYPE, MAX_FORTIFICATION_LEVEL, FORT_ORDER_TYPE
from FortifiedRegionBase import BuildingDescr
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortModernizationWindowMeta import FortModernizationWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.fortifications.context import UpgradeCtx
from gui.shared.fortifications.settings import FORT_RESTRICTION
from helpers import i18n

class MAX_LEVEL:
    MAX_BUILD_LEVEL = 4
    MAX_BASE_LEVEL_FIRST_ITERATION = 4
    MAX_BASE_LEVEL_SECOND_ITERATION = 5


class FortModernizationWindow(AbstractWindowView, View, FortModernizationWindowMeta, AppRef, FortViewHelper):

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
        self.__isFortBattleAvailable = self.app.varsManager.isFortificationBattleAvailable()
        return

    def __buildData(self):
        self.intBuildingID = self.UI_BUILDINGS_BIND.index(self.__uid)
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
        conditionIcon = self.app.utilsManager.textManager.getIcon(TextIcons.CHECKMARK_ICON)
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
                        cndPostfix = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
                        isCanModernization = False
                        canUpgradeByDefPeriod = False
                        conditionIcon = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, '-')
                elif self.__buildingLevel == self.__baseBuildingLevel:
                    cndPostfix = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
            elif self.__buildingLevel == self.__baseBuildingLevel:
                cndPostfix = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
                isCanModernization = False
        elif self.__buildingLevel == baseBuildingMaxLevel:
            cndBody = i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_BASEBUILDINGFIVELEVEL)
            if not self.__defencePeriod and self.__isFortBattleAvailable:
                cndPostfix = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
                isCanModernization = False
                canUpgradeByDefPeriod = False
                conditionIcon = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, '-')
            elif not self.__isFortBattleAvailable:
                isCanModernization = False
                canUpgradeByDefPeriod = False
                cndBody = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_FORTMAXLEVEL))
                conditionIcon = ''
        prefixBody = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, cndBody)
        result['condition'] = prefixBody + cndPostfix
        result['costUpgrade'] = self.app.utilsManager.textManager.getText(TextType.DEFRES_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_COUNTCOST))
        result['intBuildingID'] = self.intBuildingID
        if not canUpgrade and upgradeRestriction != FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE:
            conditionIcon = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, '-')
        if self._buildingDescr.storage < self.__cost:
            costMsg = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, BigWorld.wg_getIntegralFormat(self.__cost))
            constIcon = self.app.utilsManager.textManager.getIcon(TextIcons.NUT_ICON)
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
        before = {}
        before['buildingType'] = self.__uid
        before['buildingLevel'] = self.__buildingLevel
        before['buildingIndicators'] = self.__prepareIndicatorData(isCanModernization, False)
        before['defResInfo'] = self.__prepareOrderInfo(False, orderCount)
        before['titleText'] = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_BEFORELABEL))
        result['beforeUpgradeData'] = before
        after = {}
        after['buildingType'] = self.__uid
        after['buildingLevel'] = self.__buildingLevel + 1
        after['buildingIndicators'] = self.__prepareIndicatorData(isCanModernization, True, resLeft)
        after['defResInfo'] = self.__prepareOrderInfo(True, newCount)
        after['titleText'] = self.app.utilsManager.textManager.getText(TextType.MIDDLE_TITLE, i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_AFTERLABEL))
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
        textStyle = TextType.DEFRES_TEXT
        if self.__progress == FORTIFICATION_ALIASES.STATE_FOUNDATION_DEF or self.__progress == FORTIFICATION_ALIASES.STATE_FOUNDATION:
            textStyle = TextType.ALERT_TEXT
        if not isCanModernization and increment:
            currentHpLabel = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, '--')
            currentHpValue = 0
        else:
            currentHpLabel = str(BigWorld.wg_getIntegralFormat(hpVal))
            currentHpValue = hpVal
        formattedHpValue = self.app.utilsManager.textManager.getText(textStyle, currentHpLabel)
        hpTextColor = TextType.STANDARD_TEXT
        if increment:
            hpTextColor = TextType.NEUTRAL_TEXT
        formattedHpTotal = self.app.utilsManager.textManager.getText(hpTextColor, str(BigWorld.wg_getIntegralFormat(hpTotalVal)))
        formattedHpTotal += ' ' + self.app.utilsManager.textManager.getIcon(TextIcons.NUT_ICON)
        if not isCanModernization and increment:
            currentDefResLabel = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, '--')
            currentDefResValue = 0
        else:
            currentDefResLabel = str(BigWorld.wg_getIntegralFormat(defResVal))
            currentDefResValue = defResVal
        formattedDefResValue = self.app.utilsManager.textManager.getText(TextType.DEFRES_TEXT, currentDefResLabel)
        formattedDefResTotal = self.app.utilsManager.textManager.getText(hpTextColor, str(BigWorld.wg_getIntegralFormat(maxDerResVal)))
        formattedDefResTotal += ' ' + self.app.utilsManager.textManager.getIcon(TextIcons.NUT_ICON)
        result = {}
        result['hpLabel'] = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_INDICATORS_HPLBL)
        result['defResLabel'] = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_INDICATORS_DEFRESLBL)
        result['hpCurrentValue'] = currentHpValue
        result['hpTotalValue'] = hpTotalVal
        result['defResCurrentValue'] = currentDefResValue
        result['defResTotalValue'] = maxDerResVal
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

    def __prepareOrderInfo(self, increment = False, orderCount = 0):
        result = {}
        if self.__uid == 'base_building':
            if increment:
                building_bonus = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_HEADER_LEVELSLBL, buildLevel=fort_formatters.getTextLevel(min(self.__baseBuildingLevel + 1, MAX_FORTIFICATION_LEVEL)))
                defresDescr = self.app.utilsManager.textManager.concatStyles(((TextType.NEUTRAL_TEXT, building_bonus + ' '), (TextType.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.BUILDINGS_MODERNIZATIONDESCR_BASE_BUILDING))))
            else:
                building_bonus = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_HEADER_LEVELSLBL, buildLevel=fort_formatters.getTextLevel(self.__baseBuildingLevel))
                defresDescr = self.app.utilsManager.textManager.concatStyles(((TextType.STANDARD_TEXT, building_bonus + ' '), (TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.BUILDINGS_MODERNIZATIONDESCR_BASE_BUILDING))))
        else:
            orderTypeID = self._buildingDescr.typeRef.orderType
            _, _, orderLevel, orderData = self.fortCtrl.getFort().getOrderData(orderTypeID)
            foundedLevel = orderLevel
            if increment:
                bodyTextColor = TextType.MAIN_TEXT
                bonusTextColor = TextType.NEUTRAL_TEXT
                foundedLevel = orderLevel + 1
                _, _, _, orderData = self.fortCtrl.getFort().getOrderData(orderTypeID, foundedLevel)
                textPadding = '     '
            else:
                bodyTextColor = TextType.STANDARD_TEXT
                bonusTextColor = TextType.STANDARD_TEXT
                textPadding = ''
            if orderTypeID == FORT_ORDER_TYPE.SPECIAL_MISSION:
                awardText = textPadding + i18n.makeString(FORTIFICATIONS.ORDERS_SPECIALMISSION_POSSIBLEAWARD) + ' '
                bonusDescr = i18n.makeString(FORTIFICATIONS.orders_specialmission_possibleaward_description_level(foundedLevel))
                defresDescr = self.app.utilsManager.textManager.concatStyles(((bonusTextColor, awardText), (bodyTextColor, bonusDescr)))
            else:
                colorStyle = (bonusTextColor, bodyTextColor)
                bonus = str(abs(orderData.effectValue))
                defresDescr = fort_formatters.getBonusText('%s+%s%%' % (textPadding, bonus), self.__uid, colorStyle)
        result['ordersCount'] = orderCount
        result['description'] = defresDescr
        result['buildingType'] = self.__uid
        result['showAlertIcon'] = False
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
