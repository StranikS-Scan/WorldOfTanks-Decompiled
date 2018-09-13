# Embedded file name: scripts/client/gui/shared/fortifications/FortOrder.py
from constants import FORT_ORDER_TYPE
from gui.Scaleform.framework import AppRef
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import time_utils, i18n

class FortOrder(AppRef):
    ORDERS_ICONS = {FORT_ORDER_TYPE.SPECIAL_MISSION: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_RESERVEROULETTE, RES_ICONS.MAPS_ICONS_ORDERS_BIG_RESERVEROULETTE),
     FORT_ORDER_TYPE.COMBAT_PAYMENTS: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_COMBATPAYMENTS, RES_ICONS.MAPS_ICONS_ORDERS_BIG_COMBATPAYMENTS),
     FORT_ORDER_TYPE.MILITARY_EXERCISES: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_MILITARYEXERCISES, RES_ICONS.MAPS_ICONS_ORDERS_BIG_MILITARYEXERCISES),
     FORT_ORDER_TYPE.TACTICAL_TRAINING: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_TACTICALTRAINING, RES_ICONS.MAPS_ICONS_ORDERS_BIG_TACTICALTRAINING),
     FORT_ORDER_TYPE.REQUISITION: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_REQUISITION, RES_ICONS.MAPS_ICONS_ORDERS_BIG_REQUISITION),
     FORT_ORDER_TYPE.ADDITIONAL_BRIEFING: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_ADDITIONALBRIEFING, RES_ICONS.MAPS_ICONS_ORDERS_BIG_ADDITIONALBRIEFING),
     FORT_ORDER_TYPE.EVACUATION: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_EVACUATION, RES_ICONS.MAPS_ICONS_ORDERS_BIG_EVACUATION),
     FORT_ORDER_TYPE.HEAVY_TRANSPORT: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_HEAVYTRANSPORT, RES_ICONS.MAPS_ICONS_ORDERS_BIG_HEAVYTRANSPORT)}

    def __init__(self, orderID, proxy = None):
        self.orderID = orderID
        self.buildingID = None
        self.count = 0
        self.maxCount = 0
        self.level = 0
        self.finishTime = None
        self.effectTime = None
        self.effectValue = 0
        self.productionTime = None
        self.productionTotalTime = None
        self.productionCount = 0
        self.productionCost = 0
        self.isPermanent = False
        self.hasBuilding = False
        self.isSupported = True
        if proxy is not None:
            self.buildingID, self.count, self.level, orderData = proxy.getOrderData(orderID)
            orderEvent = proxy.events.get(orderID)
            self.finishTime = orderEvent[0] if orderEvent is not None else None
            self.isPermanent = self._isPermanent(orderID)
            self.isSupported = self._isSupported(orderID)
            if orderData is not None:
                self.effectTime = orderData.effectTime
                self.effectValue = orderData.effectValue
                self.productionTotalTime = orderData.productionTime
                self.productionCost = orderData.productionCost
            building = proxy.getBuilding(self.buildingID)
            if building is not None:
                self.hasBuilding = building.level > 0
                self.productionTime = building.orderInProduction.get('timeFinish')
                self.productionCount = building.orderInProduction.get('count', 0)
                self.maxCount = building.levelRef.maxOrdersCount
        return

    @property
    def icon(self):
        icons = self.ORDERS_ICONS.get(self.orderID, None)
        if icons:
            return icons[0]
        else:
            return

    @property
    def bigIcon(self):
        icons = self.ORDERS_ICONS.get(self.orderID, None)
        if icons:
            return icons[1]
        else:
            return

    @property
    def inProgress(self):
        return self.productionCount > 0

    @property
    def inCooldown(self):
        return self.getUsageLeftTime() > 0

    @property
    def isSpecialMission(self):
        return self.orderID == FORT_ORDER_TYPE.SPECIAL_MISSION

    @property
    def userName(self):
        from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
        return i18n.makeString('#fortifications:General/orderType/%s' % FortViewHelper.UI_ORDERS_BIND[self.orderID])

    @property
    def description(self):
        if self.isSpecialMission:
            awardText = i18n.makeString(FORTIFICATIONS.ORDERS_SPECIALMISSION_POSSIBLEAWARD) + ' '
            bonusDescr = i18n.makeString(FORTIFICATIONS.orders_specialmission_possibleaward_description_level(self.level))
            return fort_text.concatStyles(((fort_text.NEUTRAL_TEXT, awardText), (fort_text.MAIN_TEXT, bonusDescr)))
        else:
            from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
            effectValueStr = '+' + str(abs(self.effectValue))
            return fort_formatters.getBonusText('%s%%' % effectValueStr, FortViewHelper.UI_BUILDINGS_BIND[self.buildingID])

    def _isPermanent(self, orderID):
        if orderID in (FORT_ORDER_TYPE.EVACUATION, FORT_ORDER_TYPE.REQUISITION):
            return True
        return False

    def _isSupported(self, orderID):
        if not self.app.varsManager.isFortificationBattleAvailable():
            if orderID in (FORT_ORDER_TYPE.EVACUATION, FORT_ORDER_TYPE.REQUISITION):
                return False
        return True

    def getCooldownAsPercent(self):
        percent = 0
        if not self.isPermanent and self.finishTime is not None and self.effectTime is not None:
            leftTime = self.getUsageLeftTime()
            percent = float(max(self.effectTime - leftTime, 0)) / self.effectTime * 100
        return percent

    def getUsageLeftTime(self):
        if self.finishTime is not None:
            return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.finishTime))
        else:
            return 0

    def getUsageLeftTimeStr(self):
        return fort_text.getTimeDurationStr(self.getProductionLeftTime())

    def getProductionLeftTime(self):
        if self.productionTime is not None:
            return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.productionTime))
        else:
            return 0

    def getProductionLeftTimeStr(self):
        return fort_text.getTimeDurationStr(self.getProductionLeftTime())
