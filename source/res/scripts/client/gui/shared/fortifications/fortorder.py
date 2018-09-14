# Embedded file name: scripts/client/gui/shared/fortifications/FortOrder.py
from FortifiedRegionBase import FORT_EVENT_TYPE
from constants import FORT_ORDER_TYPE, FORT_ORDER_TYPE_NAMES
from gui.shared.fortifications import isFortificationBattlesEnabled
from gui.shared.utils.ItemsParameters import g_instance as g_itemsParams
from gui.shared.formatters import text_styles, time_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.genConsts.ORDER_TYPES import ORDER_TYPES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import time_utils, i18n

class FortOrder(object):
    ORDERS_ICONS = {FORT_ORDER_TYPE.SPECIAL_MISSION: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_RESERVEROULETTE, RES_ICONS.MAPS_ICONS_ORDERS_BIG_RESERVEROULETTE),
     FORT_ORDER_TYPE.COMBAT_PAYMENTS: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_COMBATPAYMENTS, RES_ICONS.MAPS_ICONS_ORDERS_BIG_COMBATPAYMENTS),
     FORT_ORDER_TYPE.MILITARY_EXERCISES: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_MILITARYEXERCISES, RES_ICONS.MAPS_ICONS_ORDERS_BIG_MILITARYEXERCISES),
     FORT_ORDER_TYPE.TACTICAL_TRAINING: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_TACTICALTRAINING, RES_ICONS.MAPS_ICONS_ORDERS_BIG_TACTICALTRAINING),
     FORT_ORDER_TYPE.REQUISITION: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_REQUISITION, RES_ICONS.MAPS_ICONS_ORDERS_BIG_REQUISITION),
     FORT_ORDER_TYPE.ADDITIONAL_BRIEFING: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_ADDITIONALBRIEFING, RES_ICONS.MAPS_ICONS_ORDERS_BIG_ADDITIONALBRIEFING),
     FORT_ORDER_TYPE.EVACUATION: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_EVACUATION, RES_ICONS.MAPS_ICONS_ORDERS_BIG_EVACUATION),
     FORT_ORDER_TYPE.HEAVY_TRANSPORT: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_HEAVYTRANSPORT, RES_ICONS.MAPS_ICONS_ORDERS_BIG_HEAVYTRANSPORT),
     FORT_ORDER_TYPE.ARTILLERY: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_ARTILLERY, RES_ICONS.MAPS_ICONS_ORDERS_BIG_ARTILLERY),
     FORT_ORDER_TYPE.BOMBER: (RES_ICONS.MAPS_ICONS_ORDERS_SMALL_BOMBER, RES_ICONS.MAPS_ICONS_ORDERS_BIG_BOMBER)}

    def __init__(self, orderID, proxy = None, level = 0):
        self.orderID = orderID
        self.buildingID = None
        self.count = 0
        self.maxCount = 0
        self.level = level
        self.finishTime = None
        self.effectTime = None
        self.effectValue = 0
        self.productionTime = None
        self.productionTotalTime = None
        self.productionCount = 0
        self.productionCost = 0
        self.isPermanent = False
        self.isCompatible = False
        self.hasBuilding = False
        self.isSupported = True
        if orderID in FORT_ORDER_TYPE.CONSUMABLES:
            self.group = ORDER_TYPES.FORT_ORDER_CONSUMABLES_GROUP
            self.type = ORDER_TYPES.FORT_ORDER_CONSUMABLES_ACTIVE_TYPE
        else:
            self.group = ORDER_TYPES.FORT_ORDER_GENERAL_GROUP
            self.type = ORDER_TYPES.FORT_ORDER_GENERAL_ACTIVE_TYPE
            if FORT_ORDER_TYPE.isOrderPermanent(orderID):
                self.type = ORDER_TYPES.FORT_ORDER_GENERAL_PASSIVE_TYPE
        if proxy is not None:
            self.buildingID, self.count, self.level, orderData = proxy.getOrderData(orderID)
            self.isPermanent = FORT_ORDER_TYPE.isOrderPermanent(orderID)
            self.isCompatible = FORT_ORDER_TYPE.isOrderCompatible(orderID)
            orderEvent = proxy.events.get(FORT_EVENT_TYPE.ACTIVE_ORDERS_BASE + orderID)
            if self.isPermanent and orderEvent is None:
                expireTypeName = FORT_ORDER_TYPE_NAMES[orderID] + '_EXPIRE'
                expireOrderID = getattr(FORT_ORDER_TYPE, expireTypeName)
                orderEvent = proxy.events.get(FORT_EVENT_TYPE.ACTIVE_ORDERS_BASE + expireOrderID)
            self.finishTime = orderEvent[0] if orderEvent is not None else None
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
    def isConsumable(self):
        return self.orderID in FORT_ORDER_TYPE.CONSUMABLES

    @property
    def userName(self):
        from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
        return i18n.makeString('#fortifications:General/orderType/%s' % FortViewHelper.getOrderUIDbyID(self.orderID))

    @property
    def description(self):
        from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
        if self.isSpecialMission:
            awardText = i18n.makeString(FORTIFICATIONS.ORDERS_SPECIALMISSION_POSSIBLEAWARD) + ' '
            bonusDescr = i18n.makeString(FORTIFICATIONS.orders_specialmission_possibleaward_description_level(self.level))
            return ''.join((text_styles.neutral(awardText), text_styles.main(bonusDescr)))
        elif self.isConsumable:
            return fort_formatters.getBonusText('', FortViewHelper.getBuildingUIDbyID(self.buildingID), ctx=dict(self.getParams()))
        else:
            effectValueStr = '+' + str(abs(self.effectValue))
            return fort_formatters.getBonusText('%s%%' % effectValueStr, FortViewHelper.getBuildingUIDbyID(self.buildingID))

    def _isSupported(self, orderID):
        if not isFortificationBattlesEnabled():
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
        return time_formatters.getTimeDurationStr(self.getProductionLeftTime())

    def getProductionLeftTime(self):
        if self.productionTime is not None:
            return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.productionTime))
        else:
            return 0

    def getProductionLeftTimeStr(self):
        return time_formatters.getTimeDurationStr(self.getProductionLeftTime())

    def getOperationDescription(self):
        if self.isConsumable:
            return i18n.makeString('#fortifications:fortConsumableOrder/descr/%d' % self.orderID)
        return ''

    def getUserType(self):
        i18nKey = 'battleConsumable' if self.isConsumable else 'consumable'
        return i18n.makeString('#fortifications:orderType/%s' % i18nKey, level=fort_formatters.getTextLevel(self.level))

    def getParams(self):
        if self.isConsumable:
            from ClientFortifiedRegion import getBattleEquipmentByOrderID
            eqDescr = getBattleEquipmentByOrderID(self.orderID, self.level)
            if eqDescr is not None:
                return g_itemsParams.getEquipment(eqDescr, isParameters=True)['parameters']
        return []
