# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/FortViewHelper.py
import calendar
import BigWorld
from FortifiedRegionBase import NOT_ACTIVATED
from debug_utils import LOG_DEBUG
import fortified_regions
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from constants import FORT_BUILDING_TYPE, CLAN_MEMBER_FLAGS, FORT_ORDER_TYPE
from gui.Scaleform.framework.managers.TextManager import TextIcons, TextManager
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.ORDER_TYPES import ORDER_TYPES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications.fort_helpers import FortListener
from gui.shared.utils import findFirst
from helpers import i18n, time_utils

class FortViewHelper(FortListener):
    FORT_UNKNOWN = FORTIFICATION_ALIASES.FORT_UNKNOWN
    BUILDINGS = [FORT_BUILDING_TYPE.ARTILLERY_SHOP,
     FORT_BUILDING_TYPE.BOMBER_SHOP,
     FORT_BUILDING_TYPE.OFFICE,
     FORT_BUILDING_TYPE.FINANCIAL_DEPT,
     FORT_BUILDING_TYPE.MILITARY_ACADEMY,
     FORT_BUILDING_TYPE.TANKODROME,
     FORT_BUILDING_TYPE.TRAINING_DEPT,
     FORT_BUILDING_TYPE.TRANSPORT_DEPT,
     FORT_BUILDING_TYPE.TROPHY_BRIGADE,
     FORT_BUILDING_TYPE.INTENDANT_SERVICE]
    UI_BUILDINGS_BIND = {FORT_BUILDING_TYPE.MILITARY_BASE: FORTIFICATION_ALIASES.FORT_BASE_BUILDING,
     FORT_BUILDING_TYPE.FINANCIAL_DEPT: FORTIFICATION_ALIASES.FORT_FINANCE_BUILDING,
     FORT_BUILDING_TYPE.TANKODROME: FORTIFICATION_ALIASES.FORT_TANKODROM_BUILDING,
     FORT_BUILDING_TYPE.TRAINING_DEPT: FORTIFICATION_ALIASES.FORT_TRAINING_BUILDING,
     FORT_BUILDING_TYPE.MILITARY_ACADEMY: FORTIFICATION_ALIASES.FORT_WAR_SCHOOL_BUILDING,
     FORT_BUILDING_TYPE.TRANSPORT_DEPT: FORTIFICATION_ALIASES.FORT_CAR_BUILDING,
     FORT_BUILDING_TYPE.INTENDANT_SERVICE: FORTIFICATION_ALIASES.FORT_INTENDANCY_BUILDING,
     FORT_BUILDING_TYPE.TROPHY_BRIGADE: FORTIFICATION_ALIASES.FORT_TROPHY_BUILDING,
     FORT_BUILDING_TYPE.OFFICE: FORTIFICATION_ALIASES.FORT_OFFICE_BUILDING,
     FORT_BUILDING_TYPE.ARTILLERY_SHOP: FORTIFICATION_ALIASES.FORT_ARTILLERY_SHOP_BUILDING,
     FORT_BUILDING_TYPE.BOMBER_SHOP: FORTIFICATION_ALIASES.FORT_BOMBER_SHOP_BUILDING}
    UI_ORDERS_BIND = {FORT_ORDER_TYPE.COMBAT_PAYMENTS: ORDER_TYPES.BATTLE_PAYMENTS,
     FORT_ORDER_TYPE.TACTICAL_TRAINING: ORDER_TYPES.TACTICAL_TRAINING,
     FORT_ORDER_TYPE.ADDITIONAL_BRIEFING: ORDER_TYPES.ADDITIONAL_BRIEFING,
     FORT_ORDER_TYPE.MILITARY_EXERCISES: ORDER_TYPES.MILITARY_MANEUVERS,
     FORT_ORDER_TYPE.HEAVY_TRANSPORT: ORDER_TYPES.HEAVY_TRUCKS,
     FORT_ORDER_TYPE.EVACUATION: ORDER_TYPES.EVACUATION,
     FORT_ORDER_TYPE.REQUISITION: ORDER_TYPES.REQUISITION,
     FORT_ORDER_TYPE.SPECIAL_MISSION: ORDER_TYPES.SPECIAL_MISSION,
     FORT_ORDER_TYPE.ARTILLERY: ORDER_TYPES.ARTILLERY,
     FORT_ORDER_TYPE.BOMBER: ORDER_TYPES.BOMBER}
    BUILDING_ANIMATIONS = {BUILDING_UPDATE_REASON.ADDED: FORTIFICATION_ALIASES.BUILD_FOUNDATION_ANIMATION,
     BUILDING_UPDATE_REASON.UPGRADED: FORTIFICATION_ALIASES.UPGRADE_BUILDING_ANIMATION,
     BUILDING_UPDATE_REASON.DELETED: FORTIFICATION_ALIASES.DEMOUNT_BUILDING_ANIMATION}
    CLAN_MEMBER_ROLES = [CLAN_MEMBER_FLAGS.RESERVIST,
     CLAN_MEMBER_FLAGS.RECRUIT,
     CLAN_MEMBER_FLAGS.PRIVATE,
     CLAN_MEMBER_FLAGS.JUNIOR,
     CLAN_MEMBER_FLAGS.COMMANDER,
     CLAN_MEMBER_FLAGS.RECRUITER,
     CLAN_MEMBER_FLAGS.TREASURER,
     CLAN_MEMBER_FLAGS.DIPLOMAT,
     CLAN_MEMBER_FLAGS.STAFF,
     CLAN_MEMBER_FLAGS.VICE_LEADER,
     CLAN_MEMBER_FLAGS.LEADER]

    def getData(self):
        data = self._getBaseFortificationData()
        data.update(self._getCustomData())
        return data

    @classmethod
    def getBuildingUIDbyID(cls, buildingID):
        raise isinstance(buildingID, int) or AssertionError('getBuildingUIDbyID requires INT, got %s' % str(buildingID))
        return cls.UI_BUILDINGS_BIND.get(buildingID, cls.FORT_UNKNOWN)

    @classmethod
    def getBuildingIDbyUID(cls, buildingUID):
        raise isinstance(buildingUID, str) or AssertionError('getBuildingUIDbyID requires STR, got %s' % str(buildingUID))
        return findFirst(lambda k: cls.UI_BUILDINGS_BIND[k] == buildingUID, cls.UI_BUILDINGS_BIND)

    @classmethod
    def getOrderUIDbyID(cls, orderID):
        raise isinstance(orderID, int) or AssertionError('getOrderUIDbyID requires INT, got %s' % str(orderID))
        return cls.UI_ORDERS_BIND.get(orderID, cls.FORT_UNKNOWN)

    @classmethod
    def getOrderIDbyUID(cls, orderUID):
        raise isinstance(orderUID, str) or AssertionError('getOrderIDbyUID requires STR, got %s' % str(orderUID))
        return findFirst(lambda k: cls.UI_ORDERS_BIND[k] == orderUID, cls.UI_ORDERS_BIND)

    def _getBaseFortificationData(self):
        level = 0
        if not self.fortState.isInitial():
            fort = self.fortCtrl.getFort()
            if not fort.isEmpty():
                level = fort.level
        return {'clanSize': len(g_clanCache.clanMembers),
         'minClanSize': fortified_regions.g_cache.clanMembersForStart,
         'clanCommanderName': g_clanCache.clanCommanderName,
         'level': level}

    def _getCustomData(self):
        return {}

    def getCommonBuildTooltipData(self, buildingDescr):
        hpVal = 0
        maxHpValue = 0
        defResVal = 0
        maxDefResValue = 0
        orderTooltipData = None
        if buildingDescr is not None:
            hpVal = buildingDescr.hp
            maxHpValue = buildingDescr.levelRef.hp
            defResVal = buildingDescr.storage
            maxDefResValue = buildingDescr.levelRef.storage
            if buildingDescr.orderInProduction:
                if self._isProductionInPause(buildingDescr):
                    orderTooltipData = '\n' + i18n.makeString(TOOLTIPS.FORTIFICATION_ORDERPROCESS_INPAUSE)
                else:
                    order = self.fortCtrl.getFort().getOrder(self.fortCtrl.getFort().getBuildingOrder(buildingDescr.typeID))
                    orderTime = TextManager.reference().getTimeDurationStr(order.getProductionLeftTime())
                    orderTooltipData = i18n.makeString(FORTIFICATIONS.BUILDINGS_BUILDINGTOOLTIP_ORDER, order.productionCount, orderTime)
        toolTipData = self.getBuildingTooltipBody(hpVal, maxHpValue, defResVal, maxDefResValue)
        if orderTooltipData is not None:
            toolTipData += orderTooltipData
        return toolTipData

    def _isBaseBuildingDamaged(self):
        baseBuilding = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        return self._isBuildingDamaged(baseBuilding)

    def _isBuildingDamaged(self, building):
        if building is None:
            return False
        else:
            hpVal = building.hp
            maxHpValue = building.levelRef.hp
            return hpVal < maxHpValue and building.level > 0
            return

    def _isFortFrozen(self):
        return self.fortCtrl.getFort().isFrozen()

    def _isProductionInPause(self, buildingDescr):
        return self._isBaseBuildingDamaged() or self._isBuildingDamaged(buildingDescr) or self._isFortFrozen()

    def _getProgress(self, typeID, level):
        if level == 0:
            if typeID == 0:
                return FORTIFICATION_ALIASES.STATE_TROWEL
            else:
                return FORTIFICATION_ALIASES.STATE_FOUNDATION_DEF
        else:
            return FORTIFICATION_ALIASES.STATE_BUILDING

    def _makeBuildingData(self, buildingDescr, direction, position, onlyBaseData = True, animation = FORTIFICATION_ALIASES.WITHOUT_ANIMATION):
        uid = self.FORT_UNKNOWN
        hpVal = 0
        maxHpValue = 0
        defResVal = 0
        maxDefResValue = 0
        level = 0
        orderTime = None
        isExportAvailable = False
        isImportAvailable = False
        progress = FORTIFICATION_ALIASES.STATE_TROWEL
        isLevelUp = False
        cooldownStr = None
        if buildingDescr is not None:
            uid = self.getBuildingUIDbyID(buildingDescr.typeID)
            defResVal = buildingDescr.storage
            maxDefResValue = buildingDescr.levelRef.storage
            hpVal = buildingDescr.hp
            maxHpValue = buildingDescr.levelRef.hp
            level = buildingDescr.level
            if not onlyBaseData:
                fort = self.fortCtrl.getFort()
                progress = self._getProgress(buildingDescr.typeID, level)
                buildingID = buildingDescr.typeID
                limits = self.fortCtrl.getLimits()
                canUpgrade, _ = limits.canUpgrade(buildingDescr.typeID)
                isLevelUp = canUpgrade and self._isAvailableBlinking() and self._isEnableModernizationBtnByDamaged(buildingDescr) and buildingID not in self.fortCtrl.getUpgradeVisitedBuildings()
                if buildingDescr.orderInProduction:
                    order = fort.getOrder(self.fortCtrl.getFort().getBuildingOrder(buildingID))
                    orderTime = order.getProductionLeftTimeStr()
                if buildingDescr.isInCooldown():
                    cooldownStr = buildingDescr.getEstimatedCooldownStr()
                isExportAvailable, isImportAvailable = fort.getBuildingState(buildingID)
                if isExportAvailable:
                    isExportAvailable = len(fort.getBuildingsAvailableForImport(buildingID)) > 0
                if isImportAvailable:
                    isImportAvailable = len(fort.getBuildingsAvailableForExport(buildingID)) > 0
        data = {'uid': uid,
         'defResVal': defResVal,
         'maxDefResValue': maxDefResValue,
         'hpVal': hpVal,
         'maxHpValue': maxHpValue,
         'buildingLevel': level,
         'animationType': animation}
        if not onlyBaseData:
            isDefenceHour = progress == FORTIFICATION_ALIASES.STATE_TROWEL and direction in self.fortCtrl.getFort().getDirectionsInBattle()
            data.update({'isDefenceHour': isDefenceHour,
             'isAvailable': True,
             'isExportAvailable': isExportAvailable,
             'isImportAvailable': isImportAvailable,
             'cooldown': cooldownStr,
             'direction': direction,
             'position': position,
             'progress': progress,
             'toolTipData': [uid, self.getCommonBuildTooltipData(buildingDescr)],
             'orderTime': orderTime,
             'isLevelUp': isLevelUp,
             'isOpenCtxMenu': self.fortCtrl.getPermissions().canViewContext(),
             'productionInPause': self._isProductionInPause(buildingDescr),
             'animationType': animation,
             'isBaseBuildingDamaged': self._isBaseBuildingDamaged(),
             'isFortFrozen': self._isFortFrozen()})
        return data

    def _isEnableActionBtn(self, descr):
        order = self.__getOrderByBuildingID(descr.typeID)
        result = descr.storage >= order.productionCost and order.maxCount > order.count and not self._isTutorial()
        return result and not self._isBaseBuildingDamaged() and not self._isFortFrozen()

    def _showOrderAlertIcon(self, order):
        return order.isPermanent and not self.fortCtrl.getFort().isDefenceHourEnabled() or not order.isSupported

    def _isVisibleActionBtn(self, descr):
        return not self._isMilitaryBase(descr.typeID) and not self.__orderIsInProgress(descr.typeID)

    def __orderIsInProgress(self, buildingID):
        order = self.__getOrderByBuildingID(buildingID)
        if order is None:
            return False
        else:
            return order.inProgress

    def __getOrderByBuildingID(self, buildingID):
        return self.fortCtrl.getFort().getOrder(self.fortCtrl.getFort().getBuildingOrder(buildingID))

    def _isVisibleDirectionCtrlBtn(self, descr):
        isBase = self._isMilitaryBase(descr.typeID)
        return isBase and self.fortCtrl.getPermissions().canOpenDirection()

    def _isEnableDirectionControl(self):
        return not self._isTutorial()

    def _isTutorial(self):
        return not self.fortCtrl.getFort().isStartingScriptDone()

    def _canModernization(self, descr):
        return descr.level < 10 and self._isAvailableBlinking()

    def _isEnableModernizationBtnByProgress(self, buildingDescr):
        progressFoundation = buildingDescr.level == 0 and buildingDescr.hp < buildingDescr.levelRef.hp
        isOnDefenceHour = buildingDescr.direction in self.fortCtrl.getFort().getDirectionsInBattle()
        result = not progressFoundation and not self._isTutorial() and not isOnDefenceHour
        return self.fortCtrl.getPermissions().canUpgradeBuilding() and result

    def _isEnableModernizationBtnByDamaged(self, buildingDescr):
        isBuildingDamaged = self._isBuildingDamaged(buildingDescr)
        isBaseBuildingDamaged = self._isBaseBuildingDamaged()
        isFortFrozen = self._isFortFrozen()
        isOnDefenceHour = buildingDescr.direction in self.fortCtrl.getFort().getDirectionsInBattle()
        isDamaged = (isBuildingDamaged or isBaseBuildingDamaged or isFortFrozen) and not isOnDefenceHour
        return not isDamaged

    def _isMilitaryBase(self, typeID):
        return typeID == FORT_BUILDING_TYPE.MILITARY_BASE

    def _isVisibleDemountBtn(self, descr):
        isBaseBuilding = self._isMilitaryBase(descr.typeID)
        return self.fortCtrl.getPermissions().canDeleteBuilding() and not isBaseBuilding

    def _isEnableDemountBtn(self, buildingDescr):
        isOnDefenceHour = buildingDescr.direction in self.fortCtrl.getFort().getDirectionsInBattle()
        return not self._isTutorial() and not isOnDefenceHour

    def getBuildingTooltipBody(self, hpVal, maxHpValue, defResVal, maxDefResValue):
        nutIcon = ' ' + TextManager.reference().getIcon(TextIcons.NUT_ICON)
        labelOne = i18n.makeString(FORTIFICATIONS.BUILDINGS_BUILDINGTOOLTIP_STRENGTH)
        labelTwo = i18n.makeString(FORTIFICATIONS.BUILDINGS_BUILDINGTOOLTIP_STORE)
        fstLine = labelOne + self.__toFormattedStr(hpVal) + '/' + self.__toFormattedStr(maxHpValue) + nutIcon
        secLine = labelTwo + self.__toFormattedStr(defResVal) + '/' + self.__toFormattedStr(maxDefResValue) + nutIcon
        toolTipData = fstLine + secLine
        return toolTipData

    def _isAvailableBlinking(self):
        return self.fortCtrl.getPermissions().canUpgradeBuilding()

    def __toFormattedStr(self, value):
        return str(BigWorld.wg_getIntegralFormat(value))

    def __createItem(self, maps, isEnable):
        return {'actionID': maps[0],
         'menuItem': maps[1],
         'isEnabled': isEnable}

    def _getDayoffsList(self):
        source = list(MENU.DATETIME_WEEKDAYS_FULL_ENUM)
        result = []
        result.append({'id': NOT_ACTIVATED,
         'label': FORTIFICATIONS.PERIODDEFENCEWINDOW_DROPDOWNBTN_WHITHOUTHOLIDAY})
        for day in calendar.Calendar().iterweekdays():
            name = i18n.makeString(source[day])
            result.append({'id': day,
             'label': name})

        return result

    def _isWrongLocalTime(self):
        return time_utils.getLocalDelta() >= 5 * time_utils.ONE_MINUTE
