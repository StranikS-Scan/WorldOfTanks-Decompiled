# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/FortViewHelper.py
import time
import BigWorld
from constants import FORT_BUILDING_TYPE, CLAN_MEMBER_FLAGS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.ORDER_TYPES import ORDER_TYPES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.ClanCache import g_clanCache
from fortified_regions import g_cache as g_fortCache
from gui.shared.fortifications.fort_helpers import FortListener
from helpers import i18n

class FortViewHelper(FortListener):
    FORT_UNKNOWN = FORTIFICATION_ALIASES.FORT_UNKNOWN
    BUILDINGS = [FORT_BUILDING_TYPE.FINANCIAL_DEPT,
     FORT_BUILDING_TYPE.MILITARY_ACADEMY,
     FORT_BUILDING_TYPE.TANKODROME,
     FORT_BUILDING_TYPE.TRAINING_DEPT,
     FORT_BUILDING_TYPE.TRANSPORT_DEPT,
     FORT_BUILDING_TYPE.TROPHY_BRIGADE,
     FORT_BUILDING_TYPE.INTENDANT_SERVICE]
    UI_BUILDINGS_BIND = [FORT_UNKNOWN,
     FORTIFICATION_ALIASES.FORT_BASE_BUILDING,
     FORTIFICATION_ALIASES.FORT_FINANCE_BUILDING,
     FORTIFICATION_ALIASES.FORT_TANKODROM_BUILDING,
     FORTIFICATION_ALIASES.FORT_TRAINING_BUILDING,
     FORTIFICATION_ALIASES.FORT_WAR_SCHOOL_BUILDING,
     FORTIFICATION_ALIASES.FORT_CAR_BUILDING,
     FORTIFICATION_ALIASES.FORT_INTENDANCY_BUILDING,
     FORTIFICATION_ALIASES.FORT_TROPHY_BUILDING]
    UI_ORDERS_BIND = [FORT_UNKNOWN,
     ORDER_TYPES.BATTLE_PAYMENTS,
     ORDER_TYPES.TACTICAL_TRAINING,
     ORDER_TYPES.ADDITIONAL_BRIEFING,
     ORDER_TYPES.MILITARY_MANEUVERS,
     ORDER_TYPES.HEAVY_TRUCKS,
     ORDER_TYPES.EVACUATION,
     ORDER_TYPES.REQUISITION]
    UI_ROLES_BIND = {CLAN_MEMBER_FLAGS.LEADER: FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_LEADER,
     CLAN_MEMBER_FLAGS.VICE_LEADER: FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_VICE_LEADER,
     CLAN_MEMBER_FLAGS.RECRUITER: FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_RECRUITER,
     CLAN_MEMBER_FLAGS.TREASURER: FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_TREASURER,
     CLAN_MEMBER_FLAGS.DIPLOMAT: FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_DIPLOMAT,
     CLAN_MEMBER_FLAGS.COMMANDER: FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_COMMANDER,
     CLAN_MEMBER_FLAGS.PRIVATE: FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_PRIVATE,
     CLAN_MEMBER_FLAGS.RECRUIT: FORTIFICATIONS.FORTIFICATION_CLAN_POSITION_RECRUIT}

    def getData(self):
        data = self._getBaseFortificationData()
        data.update(self._getCustomData())
        return data

    def _getBaseFortificationData(self):
        level = 0
        if not self.fortState.isInitial():
            fort = self.fortCtrl.getFort()
            if not fort.isEmpty():
                level = fort.level
        return {'isCommander': g_clanCache.isClanLeader,
         'clanSize': len(g_clanCache.clanMembers),
         'minClanSize': g_fortCache.clanMembersForStart,
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
                order = self.fortCtrl.getFort().getOrder(self.fortCtrl.getFort().getBuildingOrder(buildingDescr.typeID))
                orderTime = fort_text.getTimeDurationStr(order.getProductionLeftTime())
                orderTooltipData = i18n.makeString(FORTIFICATIONS.BUILDINGS_BUILDINGTOOLTIP_ORDER, order.productionCount, orderTime)
        toolTipData = self.getBuildingTooltipBody(hpVal, maxHpValue, defResVal, maxDefResValue)
        if orderTooltipData is not None:
            toolTipData += orderTooltipData
        return toolTipData

    def _isBaseBuildingDamaged(self):
        baseBuildingDescr = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        baseHpVal = baseBuildingDescr.hp
        baseMaxHpValue = baseBuildingDescr.levelRef.hp
        return baseHpVal < baseMaxHpValue

    def _isBuildingDamaged(self, buildingDescr):
        if buildingDescr is None:
            return False
        else:
            hpVal = buildingDescr.hp
            maxHpValue = buildingDescr.levelRef.hp
            return hpVal < maxHpValue and buildingDescr.level > 0
            return

    def _isProductionInPause(self, buildingDescr):
        return self._isBaseBuildingDamaged() or self._isBuildingDamaged(buildingDescr)

    def _getProgress(self, typeID, level):
        if level == 0:
            if typeID == 0:
                return FORTIFICATION_ALIASES.STATE_TROWEL
            else:
                return FORTIFICATION_ALIASES.STATE_FOUNDATION
        else:
            return FORTIFICATION_ALIASES.STATE_BUILDING

    def _makeBuildingData(self, buildingDescr, direction, position, onlyBaseData = True):
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
            uid = self.UI_BUILDINGS_BIND[buildingDescr.typeID]
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
                isLevelUp = canUpgrade and self._isAvailableBlinking() and buildingID not in self.fortCtrl.getUpgradeVisitedBuildings()
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
         'buildingLevel': level}
        if not onlyBaseData:
            data.update({'isAvailable': True,
             'isExportAvailable': isExportAvailable,
             'isImportAvailable': isImportAvailable,
             'cooldown': cooldownStr,
             'direction': direction,
             'position': position,
             'progress': progress,
             'toolTipData': [uid, self.getCommonBuildTooltipData(buildingDescr)],
             'orderTime': orderTime,
             'isLevelUp': isLevelUp,
             'isOpenCtxMenu': self._isChiefRoles(),
             'ctxMenuData': self.__makeContextMenuData(buildingDescr)})
        return data

    def __makeContextMenuData(self, buildingDescr):
        if buildingDescr is None or not self._isChiefRoles():
            return
        else:
            result = []
            canModernization = self._canModernization(buildingDescr)
            enableModernizationBtn = self._isEnableModernizationBtn(buildingDescr)
            if self._isMilitaryBase(buildingDescr.typeID):
                cxtMaps = [(FORTIFICATION_ALIASES.CTX_ACTION_DIRECTION_CONTROL, MENU.FORTIFICATIONCTX_DIRECTIONCONTROL), (FORTIFICATION_ALIASES.CTX_ACTION_ASSIGN_PLAYERS,
                  MENU.FORTIFICATIONCTX_ASSIGNEDPLAYERS,
                  None,
                  None), (FORTIFICATION_ALIASES.CTX_ACTION_MODERNIZATION, MENU.FORTIFICATIONCTX_MODERNIZATION)]
                if self._isVisibleDirectionCtrlBtn(buildingDescr):
                    result.append(self.__createItem(cxtMaps[0], self._isEnableDirectionControl()))
                result.append(self.__createItem(cxtMaps[1], True))
                if canModernization:
                    result.append(self.__createItem(cxtMaps[2], enableModernizationBtn))
            else:
                cxtMaps = [(FORTIFICATION_ALIASES.CTX_ACTION_PREPARE_ORDER, MENU.FORTIFICATIONCTX_PREPAREORDER),
                 (FORTIFICATION_ALIASES.CTX_ACTION_ASSIGN_PLAYERS, MENU.FORTIFICATIONCTX_ASSIGNEDPLAYERS),
                 (FORTIFICATION_ALIASES.CTX_ACTION_MODERNIZATION, MENU.FORTIFICATIONCTX_MODERNIZATION),
                 (FORTIFICATION_ALIASES.CTX_ACTION_DESTROY, MENU.FORTIFICATIONCTX_DESTROY)]
                if self._isVisibleActionBtn(buildingDescr):
                    result.append(self.__createItem(cxtMaps[0], self._isEnableActionBtn(buildingDescr)))
                result.append(self.__createItem(cxtMaps[1], True))
                if canModernization:
                    result.append(self.__createItem(cxtMaps[2], enableModernizationBtn))
                if self._isVisibleDemountBtn(buildingDescr):
                    result.append(self.__createItem(cxtMaps[3], self._isEnableDemountBtn()))
            return result

    def _isEnableActionBtn(self, descr):
        order = self.__getOrderByBuildingID(descr.typeID)
        result = descr.storage >= order.productionCost and order.maxCount > order.count and not self._isTutorial()
        return result

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
        return isBase and self._isChiefRoles()

    def _isEnableDirectionControl(self):
        return not self._isTutorial()

    def _isTutorial(self):
        return not self.fortCtrl.getFort().isStartingScriptDone()

    def _canModernization(self, descr):
        return descr.level < 10 and self._isAvailableBlinking()

    def _isEnableModernizationBtn(self, descr):
        progressFoundation = descr.level == 0 and descr.hp < descr.levelRef.hp
        result = not progressFoundation and not self._isTutorial()
        return self.fortCtrl.getPermissions().canUpgradeBuilding() and result

    def _isMilitaryBase(self, typeID):
        return typeID == FORT_BUILDING_TYPE.MILITARY_BASE

    def _isVisibleDemountBtn(self, descr):
        isBaseBuilding = self._isMilitaryBase(descr.typeID)
        return self.fortCtrl.getPermissions().canDeleteBuilding() and not isBaseBuilding

    def _isEnableDemountBtn(self):
        return not self._isTutorial()

    def _isChiefRoles(self):
        isViceCommander = g_clanCache.clanRole == CLAN_MEMBER_FLAGS.VICE_LEADER
        return g_clanCache.isClanLeader or isViceCommander

    def getBuildingTooltipBody(self, hpVal, maxHpValue, defResVal, maxDefResValue):
        nutIcon = ' ' + fort_text.getIcon(fort_text.NUT_ICON)
        labelOne = i18n.makeString(FORTIFICATIONS.BUILDINGS_BUILDINGTOOLTIP_STRENGTH)
        labelTwo = i18n.makeString(FORTIFICATIONS.BUILDINGS_BUILDINGTOOLTIP_STORE)
        fstLine = labelOne + self.__toFormattedStr(hpVal) + '/' + self.__toFormattedStr(maxHpValue) + nutIcon
        secLine = labelTwo + self.__toFormattedStr(defResVal) + '/' + self.__toFormattedStr(maxDefResValue) + nutIcon
        toolTipData = fstLine + secLine
        return toolTipData

    def _isAvailableBlinking(self):
        return g_clanCache.isClanLeader or g_clanCache.clanRole == CLAN_MEMBER_FLAGS.VICE_LEADER

    def __toFormattedStr(self, value):
        return str(BigWorld.wg_getIntegralFormat(value))

    def __createItem(self, maps, isEnable):
        return {'actionID': maps[0],
         'menuItem': maps[1],
         'isEnabled': isEnable}
