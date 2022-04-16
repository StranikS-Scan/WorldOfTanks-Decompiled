# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/spawn_menu.py
import logging
import math
import typing
from enum import Enum
import BigWorld
import constants
import nations
from RTSShared import RTSSupply
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.SpawnMenuMeta import SpawnMenuMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.genConsts.RTS_SPAWN_MENU_ENTRY_TYPES import RTS_SPAWN_MENU_ENTRY_TYPES
from gui.Scaleform.genConsts.RTS_SUPPLY_TYPE import RTS_SUPPLY_TYPE
from gui.Scaleform.locale.RTS_BATTLES import RTS_BATTLES
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control.avatar_getter import getPlayerTeam
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.commander.spawn_ctrl.interfaces import IRTSSpawnListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.badges import buildBadge
from gui.shared.gui_items.Vehicle import getIconPath, getSizedIconPath
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
from items.vehicles import VehicleDescr
from gui.Scaleform.framework.entities.View import ViewKey
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IRTSSpawnController
    from gui.Scaleform.daapi.view.battle.commander.stats_exchange import RTSStatisticsDataController
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
_logger = logging.getLogger(__name__)
_SUPPLY_ID_TO_GUI_TYPE = {RTSSupply.BARRICADES: RTS_SUPPLY_TYPE.BARRICADES,
 RTSSupply.BUNKER: RTS_SUPPLY_TYPE.GUN,
 RTSSupply.AT_GUN: RTS_SUPPLY_TYPE.AT_GUN,
 RTSSupply.PILLBOX: RTS_SUPPLY_TYPE.PILL_BOX,
 RTSSupply.WATCH_TOWER: RTS_SUPPLY_TYPE.WATCH_TOWER,
 RTSSupply.MORTAR: RTS_SUPPLY_TYPE.MORTAR,
 RTSSupply.FLAMER: RTS_SUPPLY_TYPE.FLAMER}
_SUPPLY_GUI_TYPE_TO_ID = {classTag:supplyID for supplyID, classTag in _SUPPLY_ID_TO_GUI_TYPE.items()}
_HALF_PI = math.pi / 2
_ARENATYPE_TO_BATTLEPAGE = {constants.ARENA_BONUS_TYPE.RTS: VIEW_ALIAS.COMMANDER_BATTLE_PAGE,
 constants.ARENA_BONUS_TYPE.RTS_1x1: VIEW_ALIAS.COMMANDER_BATTLE_PAGE,
 constants.ARENA_BONUS_TYPE.RTS_BOOTCAMP: ''}

def _convertGuiSupplyTypeToTag(guiType):
    return RTSSupply.SUPPLY_ID_TO_TAG[_SUPPLY_GUI_TYPE_TO_ID[guiType]] if guiType in _SUPPLY_GUI_TYPE_TO_ID else guiType


def convertTagToGuiSupplyType(tagName):
    return _SUPPLY_ID_TO_GUI_TYPE[RTSSupply.TAG_TO_SUPPLY[tagName]] if tagName in RTSSupply.TAG_TO_SUPPLY else tagName


def _createBaseEntryVO(entryID, entryType, x, y):
    return {'entryID': entryID,
     'entryType': entryType,
     'x': x,
     'y': y}


def _createPlacePointEntryVO(pointData, entryType, vehicleType, visionRadius=0, engagementRadius=0, yawLeftLimit=0.0, yawRightLimit=0.0):
    pointVO = _createBaseEntryVO(pointData.guid, entryType, pointData.x, pointData.y)
    pointVO.update({'vehicleType': vehicleType,
     'visionRadius': visionRadius,
     'engagementRadius': engagementRadius,
     'yawLeftLimit': yawLeftLimit,
     'yawRightLimit': yawRightLimit})
    return pointVO


def _createOccupiedPointEntryVO(pointData, entryType, vehicleType, isSelected, vehicleID=0, title='', visionRadius=0, engagementRadius=0, yawLeftLimit=0.0, yawRightLimit=0.0):
    pointVO = _createBaseEntryVO(pointData.guid, entryType, pointData.x, pointData.y)
    pointVO.update({'vehicleType': vehicleType,
     'vehicleName': title,
     'isSelected': isSelected,
     'vehicleID': vehicleID,
     'visionRadius': visionRadius,
     'engagementRadius': engagementRadius,
     'yawLeftLimit': yawLeftLimit,
     'yawRightLimit': yawRightLimit})
    return pointVO


class SpawnMenuMap(object):
    _IMG_PATH_FORMAT = 'img://%s'
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SpawnMenuMap, self).__init__()
        self.__playerTeam = 0

    def getVO(self):
        mapVO = {}
        self.__fillMapData(mapVO)
        return mapVO

    def __fillMapData(self, initialVO):
        self.__playerTeam = getPlayerTeam()
        sessionProvider = self.__sessionProvider
        battleCtx = sessionProvider.getCtx()
        arenaVisitor = sessionProvider.arenaVisitor
        arenaType = arenaVisitor.type
        bottomLeft, topRight = arenaType.getBoundingBox()
        mapWidth = (topRight - bottomLeft)[0]
        if self.__sessionProvider.arenaVisitor.getArenaBonusType() == constants.ARENA_BONUS_TYPE.RTS_BOOTCAMP:
            mapWidth = 600
        spawnBasePointsInfo = []
        for team in arenaType.getTeamsOnArenaRange():
            spawnBasePointsInfo.extend(tuple(arenaVisitor.getTeamSpawnPointsIterator(team)))

        initialVO.update({'basePointsData': map(self.__createBasePointVO, arenaType.getTeamBasePositionsIterator()),
         'controlPointsData': map(self.__createControlPointVO, arenaType.getControlPointsIterator()),
         'spawnBasePointsData': map(self.__createSpawnBasePointVO, spawnBasePointsInfo),
         'bgPath': self._IMG_PATH_FORMAT % battleCtx.getArenaScreenIcon(),
         'mapPath': self._IMG_PATH_FORMAT % arenaType.getMinimapTexture(),
         'mapIconPath': self._IMG_PATH_FORMAT % battleCtx.getArenaSmallIcon().replace('../', 'gui/'),
         'name': battleCtx.getArenaTypeName(isInBattle=True),
         'size': mapWidth})

    def __createBasePointVO(self, basePointInfo):
        team, position, baseID = basePointInfo
        pointVO = self.__createControlPointVO((position, baseID))
        pointVO.update({'entryType': RTS_SPAWN_MENU_ENTRY_TYPES.BASE_POINT,
         'isPlayerTeam': team == self.__playerTeam})
        return pointVO

    @staticmethod
    def __createControlPointVO(controlPointInfo):
        position, baseID = controlPointInfo
        pointVO = _createBaseEntryVO('', RTS_SPAWN_MENU_ENTRY_TYPES.CONTROL_POINT, position[0], position[2])
        pointVO.update({'baseID': baseID})
        return pointVO

    def __createSpawnBasePointVO(self, spawnBasePointInfo):
        spawnBasePointVO = self.__createBasePointVO(spawnBasePointInfo)
        spawnBasePointVO.update({'entryType': RTS_SPAWN_MENU_ENTRY_TYPES.SPAWN_BASE_POINT})
        return spawnBasePointVO


class VisionData(Enum):
    VISION_RADIUS = 'visionRadius'
    ENGAGEMENT_RADIUS = 'engagementRadius'
    YAW_LIMITS = 'yawLimits'


class SpawnMenu(SpawnMenuMeta, IRTSSpawnListener, IAbstractPeriodView):
    _SUPPLY_ITEM_SIZE = '80x50'
    _ALERT_HINT_STATE = 0
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SpawnMenu, self).__init__()
        self.__map = SpawnMenuMap()
        self.__lastState = None
        self.__vehiclesVOs = []
        self.__suppliesVOs = []
        self.__totalMapEntriesCount = 0
        return

    def _populate(self):
        super(SpawnMenu, self)._populate()
        g_playerEvents.onAvatarReady += self.__onAvatarReady
        self.as_setIsResetBtnEnabledS(False)
        self.as_setIsAutoSetBtnEnabledS(True)
        self.as_setIsBattleBtnEnabledS(False)
        self.as_showMapHintS(True, self._ALERT_HINT_STATE, RTS_BATTLES.SPAWNMENU_MAP_ALERT)

    def _dispose(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__vehiclesVOs = None
        self.__suppliesVOs = None
        super(SpawnMenu, self)._dispose()
        return

    def onBattleBtnClick(self):
        self._getSpawnCtrl().applySelection()

    def onAutoSetBtnClick(self):
        self._getSpawnCtrl().autoChoosePoints()

    def onResetBtnClick(self):
        self._getSpawnCtrl().resetSelection()

    def onBGClick(self):
        self._getSpawnCtrl().unselectEntity()

    def onSupplySelect(self, guiSupplyType):
        self._getSpawnCtrl().selectSupplyByClassTag(_convertGuiSupplyTypeToTag(guiSupplyType))

    def onVehicleSelect(self, vehicleID):
        vehicleID = int(vehicleID)
        self._getSpawnCtrl().selectEntity(vehicleID)

    def onPointClick(self, pointID):
        self._getSpawnCtrl().chooseSpawnKeyPoint(pointID)

    def setCountdown(self, state, timeLeft):
        if state == self.__lastState:
            return
        self.as_setIsWaitingPlayersS(state == COUNTDOWN_STATE.WAIT)
        self.__lastState = state

    def updatePoint(self, vehicleId, pointId, prevPointId):
        pass

    def updatePointsList(self):
        self.__updateEntities()

    def onEntitySelected(self):
        self.__updateEntities()

    def __updateEntities(self):
        selectedEntityID = self._getSpawnCtrl().selectedEntityID
        self.__sendUIPointsUpdate(selectedEntityID)
        self.__sendUIButtonsUpdate(selectedEntityID)

    def __onAvatarReady(self):
        dataVO = {}
        self.__fillCommonData(dataVO)
        self.__fillButtonsData(dataVO)
        self.__fillVehiclesData(dataVO)
        self.as_setDataS(dataVO, self.__map.getVO())

    def __createRoosterVehicleVO(self, vehicleInfo):
        vType = vehicleInfo.vehicleType
        groupID = 0
        vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleInfo.vehicleID)
        if vehicle is not None and vehicle.isAllyBot:
            groupID = vehicle.groupID
        return {'vehicleID': vehicleInfo.vehicleID,
         'vehicleIcon': getIconPath(vType.iconName),
         'vehicleName': vType.shortName,
         'vehicleType': vType.classTag,
         'vehicleLevel': vType.level,
         'nation': nations.NAMES[vType.nationID],
         'groupID': groupID}

    def __createEnemyPlayerVO(self, vehicleInfo):
        vType = vehicleInfo.vehicleType
        data = {'vehicleID': vehicleInfo.vehicleID,
         'vehicleContour': vType.iconName,
         'vehicleName': vType.shortName,
         'vehicleType': vType.classTag,
         'vehicleLevel': vType.level,
         'playerName': vehicleInfo.player.getPlayerLabel(),
         'badgeData': self.__getBadgeData(vehicleInfo)}
        selSuffix = vehicleInfo.selectedSuffixBadge
        if selSuffix:
            data['suffixBadgeType'], data['suffixBadgeStripType'] = self.__getSuffixBageData(selSuffix)
        return data

    def __createSupplyVO(self, vehicleInfo, classTagOverride):
        vType = vehicleInfo.vehicleType
        return {'vehicleIcon': getSizedIconPath(vType.iconName, self._SUPPLY_ITEM_SIZE),
         'vehicleName': vType.shortName,
         'vehicleType': classTagOverride,
         'vehicleLevel': 0,
         'settledCount': 0,
         'totalCount': 0}

    @staticmethod
    def __getBadgeData(vehicleInfo):
        badgeID = vehicleInfo.selectedBadge
        badge = buildBadge(badgeID, vehicleInfo.getBadgeExtraInfo())
        return None if badge is None else badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True)

    def __fillCommonData(self, initialVO):
        sessionProvider = self.__sessionProvider
        battleCtx = sessionProvider.getCtx()
        arenaDP = sessionProvider.getArenaDP()
        if arenaDP is None:
            logging.error("RTS spawn menu can't get arenaDP.")
            return
        else:
            enemyStrategistName = ''
            enemyStrategistBadgeInfo = None
            for vInfo in self._getSpawnCtrl().getSortedVehicleInfos():
                if vInfo.isCommander() and arenaDP.isEnemyTeam(vInfo.team):
                    enemyStrategistName = vInfo.player.getPlayerLabel()
                    enemyStrategistBadgeInfo = self.__getBadgeData(vInfo)
                    selSuffix = vInfo.selectedSuffixBadge
                    if selSuffix:
                        sBt, sBsT = self.__getSuffixBageData(selSuffix)
                        initialVO['enemySuffixBadgeType'] = sBt
                        initialVO['enemySuffixBadgeStripType'] = sBsT
                    break

            vehicleInfo = arenaDP.getVehicleInfo()
            playerVO = vehicleInfo.player
            sessionID = playerVO.avatarSessionID
            region = ''
            playerFakeName = ''
            userTags = []
            arenaBonusType = sessionProvider.arenaVisitor.getArenaBonusType()
            pageViewAlias = _ARENATYPE_TO_BATTLEPAGE.get(arenaBonusType)
            if pageViewAlias is not None:
                if pageViewAlias != '':
                    commanderBattlePage = self.app.containerManager.getViewByKey(ViewKey(pageViewAlias))
                    if commanderBattlePage:
                        statisticDataCtrlView = commanderBattlePage.components.get(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER)
                        if statisticDataCtrlView:
                            exchangeCtx = statisticDataCtrlView.getExchangeContext()
                            parts = exchangeCtx.getPlayerFullName(vehicleInfo)
                            region = parts.regionCode
                            playerFakeName = parts.playerFakeName
                            userTags = exchangeCtx.getUserTags(sessionID, playerVO.igrType)
                        else:
                            _logger.error("% component has not been found in %s! Anonimizer data can't be obtained!", BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, pageViewAlias)
                    else:
                        _logger.error("%s has not been found, Anonimizer data can't be obtained!", pageViewAlias)
                else:
                    _logger.info('Anonimaizer is not required for this arena bonus type %s', arenaBonusType)
            else:
                _logger.error("Couldn't find commander page view alias for %s arena bonus type. Anonimizer data can't be obtained!", arenaBonusType)
            selSuffix = vehicleInfo.selectedSuffixBadge
            if selSuffix:
                sBt, sBsT = self.__getSuffixBageData(selSuffix)
                initialVO['playerSuffixBadgeType'] = sBt
                initialVO['playerSuffixBadgeStripType'] = sBsT
            initialVO.update({'winConditionText': battleCtx.getArenaWinString(),
             'playerName': battleCtx.getPlayerName(arenaDP.getPlayerVehicleID()),
             'clanAbbrev': playerVO.clanAbbrev,
             'region': region,
             'playerFakeName': playerFakeName,
             'userTags': userTags,
             'playerBadgeInfo': self.__getBadgeData(vehicleInfo),
             'enemyStrategistName': enemyStrategistName,
             'enemyStrategistBadgeInfo': enemyStrategistBadgeInfo})
            return

    @staticmethod
    def __getSuffixBageData(selSuffix):
        return ('badge_{}'.format(selSuffix), 'strip_{}'.format(selSuffix))

    @staticmethod
    def __fillButtonsData(initialVO):
        buttonsResShortcut = R.strings.rts_battles.spawnMenu.button
        initialVO.update({'autoSetBtnText': backport.text(buttonsResShortcut.autoSet()),
         'resetBtnText': backport.text(buttonsResShortcut.reset()),
         'battleBtnText': backport.text(buttonsResShortcut.battle())})

    def __fillVehiclesData(self, initialVO):
        arenaDP = self.__sessionProvider.getArenaDP()
        if arenaDP is None:
            logging.error("RTS spawn menu can't get arenaDP.")
            return
        else:
            self.__totalMapEntriesCount = 0
            enemyPlayers = []
            self.__vehiclesVOs, playerSupplies, enemyRosterVehicles, enemyRosterSupplies = ([],
             {},
             [],
             {})
            playerSupplyList = []
            enemySupplyList = []
            for vInfo in self._getSpawnCtrl().getSortedVehicleInfos():
                if vInfo.isObserver() or vInfo.isCommander():
                    continue
                if vInfo.isSupply():
                    guiSupplyType = convertTagToGuiSupplyType(vInfo.vehicleType.classTag)
                    if guiSupplyType is None:
                        continue
                    supplyContainer = enemyRosterSupplies if arenaDP.isEnemyTeam(vInfo.team) else playerSupplies
                    supplyList = enemySupplyList if arenaDP.isEnemyTeam(vInfo.team) else playerSupplyList
                    if guiSupplyType not in supplyContainer:
                        supplyContainer[guiSupplyType] = self.__createSupplyVO(vInfo, guiSupplyType)
                        supplyList.append(supplyContainer[guiSupplyType])
                    supplyContainer[guiSupplyType]['totalCount'] += 1
                    if not arenaDP.isEnemyTeam(vInfo.team):
                        self.__totalMapEntriesCount += 1
                if arenaDP.isEnemyTeam(vInfo.team):
                    if self._isStrategistEnemyVehicle(vInfo):
                        enemyRosterVehicles.append(self.__createRoosterVehicleVO(vInfo))
                    else:
                        enemyPlayers.append(self.__createEnemyPlayerVO(vInfo))
                self.__vehiclesVOs.append(self.__createRoosterVehicleVO(vInfo))
                self.__totalMapEntriesCount += 1

            self.__suppliesVOs = playerSupplyList
            initialVO.update({'playerRosterVehicles': self.__vehiclesVOs,
             'enemiesData': enemyPlayers,
             'playerRosterSupplies': self.__suppliesVOs,
             'enemyRosterVehicles': enemyRosterVehicles,
             'enemyRosterSupplies': enemySupplyList})
            return

    def _isStrategistEnemyVehicle(self, vInfo):
        arena = BigWorld.player().arena
        vehicle = arena.vehicles.get(vInfo.vehicleID, {})
        return vehicle.get('accountDBID') == 0 and arena.bonusType == constants.ARENA_BONUS_TYPE.RTS_1x1 if vehicle is not None else True

    def __sendUIPointsUpdate(self, selectedEntityID):
        processedPointIDs = set()
        placePointsData = []
        suppliesPointsData = []
        vehiclesPointsData = []
        getVehicleInfo = self.__sessionProvider.getArenaDP().getVehicleInfo
        spawnCtrl = self._getSpawnCtrl()
        for entityID, entity in spawnCtrl.placedEntities.iteritems():
            chosenPointData = entity.chosenPointData
            processedPointIDs.add(chosenPointData.guid)
            pointVehicleInfo = getVehicleInfo(entityID)
            vehicleType = pointVehicleInfo.vehicleType
            if pointVehicleInfo.isSupply():
                visionRadius, engagementRadius, yawLeftLimit, yawRightLimit = self.__getVehicleVisionData(pointVehicleInfo.vehicleID)
                suppliesPointsData.append(_createOccupiedPointEntryVO(chosenPointData, RTS_SPAWN_MENU_ENTRY_TYPES.SUPPLY, vehicleType=convertTagToGuiSupplyType(vehicleType.classTag), isSelected=entityID == selectedEntityID, title=vehicleType.shortName, visionRadius=visionRadius, engagementRadius=engagementRadius, yawLeftLimit=self.__prepareYawForUI(yawLeftLimit, chosenPointData.yaw), yawRightLimit=self.__prepareYawForUI(yawRightLimit, chosenPointData.yaw)))
            vehiclesPointsData.append(_createOccupiedPointEntryVO(chosenPointData, RTS_SPAWN_MENU_ENTRY_TYPES.ALLY_VEHICLE, vehicleType=vehicleType.classTag, isSelected=entityID == selectedEntityID, title=vehicleType.shortName, vehicleID=pointVehicleInfo.vehicleID))

        for pointID, pointData in spawnCtrl.iterAvailablePointsByEntityID(selectedEntityID):
            if pointID in processedPointIDs:
                continue
            pointVehicleInfo = getVehicleInfo(selectedEntityID)
            vehicleType = pointVehicleInfo.vehicleType
            if pointVehicleInfo.isSupply():
                vehicleTypeTag = convertTagToGuiSupplyType(vehicleType.classTag)
            else:
                vehicleTypeTag = vehicleType.classTag
            visionRadius, engagementRadius, yawLeftLimit, yawRightLimit = self.__getVehicleVisionData(pointVehicleInfo.vehicleID)
            placePointsData.append(_createPlacePointEntryVO(pointData, RTS_SPAWN_MENU_ENTRY_TYPES.PLACE_POINT, vehicleType=vehicleTypeTag, visionRadius=visionRadius, engagementRadius=engagementRadius, yawLeftLimit=self.__prepareYawForUI(yawLeftLimit, pointData.yaw), yawRightLimit=self.__prepareYawForUI(yawRightLimit, pointData.yaw)))

        self.as_updateEntriesDataS(placePointsData, suppliesPointsData, vehiclesPointsData)

    def __prepareYawForUI(self, targetYaw, chosenPointDataYaw):
        return 0 if targetYaw is None else targetYaw + chosenPointDataYaw - _HALF_PI

    def __sendUIButtonsUpdate(self, selectedEntityID):
        spawnCtrl = self._getSpawnCtrl()
        placedEntities = spawnCtrl.placedEntities
        for vo in self.__vehiclesVOs:
            vehicleID = vo['vehicleID']
            vo['isSelected'] = isSelected = selectedEntityID == vehicleID
            vo['isSettled'] = isSettled = vehicleID in placedEntities
            vo['isDragged'] = isSelected and (not isSettled or selectedEntityID is not None)

        selectedEntityType = spawnCtrl.selectedEntityType
        for sVo in self.__suppliesVOs:
            classTag = _convertGuiSupplyTypeToTag(sVo['vehicleType'])
            suppliesContainer = spawnCtrl.getSuppliesByClassTag(classTag)
            if suppliesContainer is None:
                continue
            sVo['isSelected'] = isSelected = selectedEntityType == classTag
            sVo['isSettled'] = isSettled = suppliesContainer.isSettled
            sVo['settledCount'] = suppliesContainer.settledCount
            sVo['isDragged'] = isSelected and (not isSettled or selectedEntityID is not None)

        self.as_setItemsDataS(self.__vehiclesVOs, self.__suppliesVOs)
        self._updateResetButtonState()
        isAllPointsApplied = self.__totalMapEntriesCount == len(spawnCtrl.placedEntities)
        self.as_setIsAutoSetBtnEnabledS(not isAllPointsApplied)
        self.as_setIsBattleBtnEnabledS(isAllPointsApplied)
        return

    def _updateResetButtonState(self):
        self.as_setIsResetBtnEnabledS(len(self._getSpawnCtrl().placedEntities) > 0)

    def __getVehicleVisionData(self, vehicleID):
        visionRadius = 0
        engagementRadius = 0
        yawLeftLimit = None
        yawRightLimit = None
        arenaDP = self.__sessionProvider.getArenaDP()
        vehicleInfoVO = arenaDP.getVehicleInfo(vehicleID)
        descriptor = VehicleDescr(compactDescr=vehicleInfoVO.vehicleType.strCompactDescr)
        if descriptor is not None:
            visionRadius = descriptor.turret.circularVisionRadius
            engagementRadius = descriptor.gun.shots[0].maxDistance
            if descriptor.gun.turretYawLimits is not None:
                yawLeftLimit, yawRightLimit = descriptor.gun.turretYawLimits
        return (visionRadius,
         engagementRadius,
         yawLeftLimit,
         yawRightLimit)

    def _getSpawnCtrl(self):
        return self.__sessionProvider.dynamic.spawn
