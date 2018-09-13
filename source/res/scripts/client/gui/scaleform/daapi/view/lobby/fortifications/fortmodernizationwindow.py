# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortModernizationWindow.py
import BigWorld
from adisp import process
from constants import FORT_BUILDING_TYPE, MAX_FORTIFICATION_LEVEL
from FortifiedRegionBase import BuildingDescr
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortModernizationWindowMeta import FortModernizationWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.fortifications.context import UpgradeCtx
from gui.shared.fortifications.settings import FORT_RESTRICTION
from helpers import i18n

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
        self.__isCommander = None
        self.__hpTotalVal = None
        self.__hpVal = None
        self.__defResVal = None
        self.__maxDerResVal = None
        self.__cost = None
        self.__defencePeriod = 0
        return

    def __buildData(self):
        self.intBuildingID = self.UI_BUILDINGS_BIND.index(self.__uid)
        self._buildingDescr = self.fortCtrl.getFort().getBuilding(self.intBuildingID)
        self.__buildingLevel = max(self._buildingDescr.level, 1)
        self.nextLevel = BuildingDescr(typeID=self.intBuildingID, level=self.__buildingLevel + 1)
        baseBuilding = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        self.__baseBuildingLevel = baseBuilding.level
        self.__progress = self._getProgress(self._buildingDescr.typeID, self.__buildingLevel)
        self.__isCommander = g_clanCache.isClanLeader
        self.__hpTotalVal = self._buildingDescr.levelRef.hp
        self.__hpVal = self._buildingDescr.hp
        self.__defResVal = self._buildingDescr.storage
        self.__maxDerResVal = self._buildingDescr.levelRef.storage
        self.__cost = self._buildingDescr.levelRef.upgradeCost
        self.__defencePeriod = 0
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
            if self.app.soundManager is not None:
                self.app.soundManager.playEffectSound(SoundEffectsId.FORT_UPGRADE_BUILDING)
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_MODERNIZATIONBUILDING, buildingName=building.userName, buildingLevel=building.getUserLevel(True), type=SystemMessages.SM_TYPE.Warning)
            self.onWindowClose()
        return

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
        self.__isCommander = None
        self.__hpTotalVal = None
        self.__hpVal = None
        self.__defResVal = None
        self.__maxDerResVal = None
        self.__cost = None
        self.__defencePeriod = 0
        super(FortModernizationWindow, self)._dispose()
        return

    def onUpdated(self):
        self.__buildData()

    def onBuildingRemoved(self, buildingTypeID):
        if self.intBuildingID == buildingTypeID:
            self.destroy()

    def __makeData(self):
        result = {}
        if self.__uid != FORTIFICATION_ALIASES.FORT_BASE_BUILDING:
            if self.nextLevel.level > self.__baseBuildingLevel:
                baseBuildingLbl = self.nextLevel.level
        cndBody = ''
        limits = self.fortCtrl.getLimits()
        canUpgrade, upgradeRestriction = limits.canUpgrade(self.intBuildingID)
        LOG_DEBUG(upgradeRestriction)
        cndPostfix = ''
        isCanModernization = canUpgrade
        if self.__uid != FORTIFICATION_ALIASES.FORT_BASE_BUILDING:
            cndBody = i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_GENERALCONDITION, level=fort_formatters.getTextLevel(self.__buildingLevel + 1))
            if canUpgrade:
                isCanModernization = True
            else:
                isCanModernization = False
            if self.__defencePeriod != 0:
                cndBody = i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_DEFENCEPERIOD)
                cndPostfix = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
                isCanModernization = False
            elif self.__buildingLevel == self.__baseBuildingLevel:
                cndPostfix = fort_text.getText(fort_text.ERROR_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_NOTFULFILLED))
                isCanModernization = False
        elif self.__baseBuildingLevel == MAX_FORTIFICATION_LEVEL:
            cndPostfix = fort_text.getText(fort_text.ALERT_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_CONDITIONS_FORTMAXLEVEL))
        prefixBody = fort_text.getText(fort_text.MAIN_TEXT, cndBody)
        result['condition'] = prefixBody + cndPostfix
        result['costUpgrade'] = fort_text.getText(fort_text.PURPLE_TEXT, i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_COUNTCOST))
        result['intBuildingID'] = self.intBuildingID
        conditionIcon = fort_text.getIcon(fort_text.CHECKMARK_ICON)
        if not canUpgrade and upgradeRestriction != FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE:
            conditionIcon = fort_text.getText(fort_text.STANDARD_TEXT, '-')
        if self._buildingDescr.storage < self.__cost:
            costMsg = fort_text.getText(fort_text.ERROR_TEXT, BigWorld.wg_getIntegralFormat(self.__cost))
            constIcon = fort_text.getIcon(fort_text.NUT_ICON)
            costMsg = costMsg + ' ' + constIcon
        else:
            costMsg = fort_formatters.getDefRes(self.__cost, True)
        result['costValue'] = costMsg
        result['conditionIcon'] = conditionIcon if not self._isMilitaryBase(self.intBuildingID) else ''
        result['canUpgrade'] = isCanModernization
        if not isCanModernization:
            btnToolTip = {}
            btnToolTip['header'] = i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_APPLYBUTTON_HEADER)
            if upgradeRestriction == FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE_AND_LOW_LEVEL:
                btnToolTip['body'] = i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_APPLYBUTTON_LOWLEVELANDRESOURCE, baseLevel=fort_formatters.getTextLevel(self.__baseBuildingLevel + 1))
            if upgradeRestriction == FORT_RESTRICTION.BUILDING_FORT_LEVEL_TOO_LOW:
                btnToolTip['body'] = i18n.makeString(TOOLTIPS.FORTIFICATION_MODERNIZATION_APPLYBUTTON_LOWBASELEVEL, baseLevel=fort_formatters.getTextLevel(self.__baseBuildingLevel + 1))
            if upgradeRestriction == FORT_RESTRICTION.BUILDING_NOT_ENOUGH_RESOURCE:
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
        before['titleText'] = fort_text.getText(fort_text.MIDDLE_TITLE, i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_BEFORELABEL))
        result['beforeUpgradeData'] = before
        after = {}
        after['buildingType'] = self.__uid
        after['buildingLevel'] = self.__buildingLevel + 1
        after['buildingIndicators'] = self.__prepareIndicatorData(isCanModernization, True, resLeft)
        after['defResInfo'] = self.__prepareOrderInfo(True, newCount)
        after['titleText'] = fort_text.getText(fort_text.MIDDLE_TITLE, i18n.makeString(FORTIFICATIONS.MODERNIZATION_MODERNIZATIONINFO_AFTERLABEL))
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
        textStyle = fort_text.PURPLE_TEXT
        if self.__progress == FORTIFICATION_ALIASES.STATE_FOUNDATION_DEF or self.__progress == FORTIFICATION_ALIASES.STATE_FOUNDATION:
            textStyle = fort_text.ALERT_TEXT
        if not isCanModernization and increment:
            currentHpLabel = fort_text.getText(fort_text.MAIN_TEXT, '--')
            currentHpValue = 0
        else:
            currentHpLabel = str(BigWorld.wg_getIntegralFormat(hpVal))
            currentHpValue = hpVal
        formattedHpValue = fort_text.getText(textStyle, currentHpLabel)
        hpTextColor = fort_text.STANDARD_TEXT
        if increment:
            hpTextColor = fort_text.NEUTRAL_TEXT
        formattedHpTotal = fort_text.getText(hpTextColor, str(BigWorld.wg_getIntegralFormat(hpTotalVal)))
        formattedHpTotal += ' ' + fort_text.getIcon(fort_text.NUT_ICON)
        if not isCanModernization and increment:
            currentDefResLabel = fort_text.getText(fort_text.MAIN_TEXT, '--')
            currentDefResValue = 0
        else:
            currentDefResLabel = str(BigWorld.wg_getIntegralFormat(defResVal))
            currentDefResValue = defResVal
        formattedDefResValue = fort_text.getText(fort_text.PURPLE_TEXT, currentDefResLabel)
        formattedDefResTotal = fort_text.getText(hpTextColor, str(BigWorld.wg_getIntegralFormat(maxDerResVal)))
        formattedDefResTotal += ' ' + fort_text.getIcon(fort_text.NUT_ICON)
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
        maxOrdersCount = 0
        if self.__uid == 'base_building':
            if increment:
                building_bonus = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_HEADER_LEVELSLBL, buildLevel=fort_formatters.getTextLevel(min(self.__baseBuildingLevel + 1, MAX_FORTIFICATION_LEVEL)))
                defresDescr = fort_text.concatStyles(((fort_text.NEUTRAL_TEXT, building_bonus + ' '), (fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.BUILDINGS_MODERNIZATIONDESCR_BASE_BUILDING))))
            else:
                building_bonus = i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_HEADER_LEVELSLBL, buildLevel=fort_formatters.getTextLevel(self.__baseBuildingLevel))
                defresDescr = fort_text.concatStyles(((fort_text.STANDARD_TEXT, building_bonus + ' '), (fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.BUILDINGS_MODERNIZATIONDESCR_BASE_BUILDING))))
        else:
            orderTypeID = self._buildingDescr.typeRef.orderType
            _, _, orderLevel, orderData = self.fortCtrl.getFort().getOrderData(orderTypeID)
            if increment:
                _, _, _, orderData = self.fortCtrl.getFort().getOrderData(orderTypeID, orderLevel + 1)
                maxOrdersCount = self.nextLevel.levelRef.maxOrdersCount
            else:
                maxOrdersCount = self._buildingDescr.levelRef.maxOrdersCount
            bonus = orderData.effectValue
            bonusTextColor = fort_text.NEUTRAL_TEXT
            textPadding = '     '
            if increment == False:
                bonusTextColor = fort_text.STANDARD_TEXT
                textPadding = ''
            colorStyle = (bonusTextColor, fort_text.STANDARD_TEXT)
            defresDescr = fort_formatters.getBonusText('%s+%d%%' % (textPadding, bonus), self.__uid, colorStyle)
        result['ordersCount'] = orderCount
        result['description'] = defresDescr
        result['buildingType'] = self.__uid
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
