# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/fortifications.py
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.common import ToolTipBaseData
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache
__buildsDirectionMap = {'A': FORTIFICATIONS.STRONGHOLDBUILDS_DIRECTION_A,
 'B': FORTIFICATIONS.STRONGHOLDBUILDS_DIRECTION_B,
 'C': FORTIFICATIONS.STRONGHOLDBUILDS_DIRECTION_C,
 'D': FORTIFICATIONS.STRONGHOLDBUILDS_DIRECTION_D}
_MAX_VEHICLES_COUNT = 23

def getBuildsDirection(direction):
    return _ms(__buildsDirectionMap[direction])


class ToolTipRefSysDirects(ToolTipBaseData):

    def __init__(self, context):
        super(ToolTipRefSysDirects, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    @staticmethod
    def __getTitle(index):
        infoMap = (FORTIFICATIONS.STRONGHOLDBUILDS_POINT1,
         FORTIFICATIONS.STRONGHOLDBUILDS_POINT2,
         FORTIFICATIONS.STRONGHOLDBUILDS_POINT3,
         FORTIFICATIONS.STRONGHOLDBUILDS_POINT4,
         FORTIFICATIONS.STRONGHOLDBUILDS_POINT5,
         FORTIFICATIONS.STRONGHOLDBUILDS_POINT6)
        return _ms(infoMap[index])

    @staticmethod
    def __getPointReward(index):
        infoMap = (FORTIFICATIONS.STRONGHOLDBUILDS_REWARDPOINT1,
         FORTIFICATIONS.STRONGHOLDBUILDS_REWARDPOINT2,
         FORTIFICATIONS.STRONGHOLDBUILDS_REWARDPOINT3,
         FORTIFICATIONS.STRONGHOLDBUILDS_REWARDPOINT4,
         FORTIFICATIONS.STRONGHOLDBUILDS_REWARDPOINT5,
         FORTIFICATIONS.STRONGHOLDBUILDS_REWARDPOINT6)
        return _ms(infoMap[index])

    def buildMapPoints(self, size, teamBasePositions, playerTeam, isCurrentBattle):
        minimapSize = 300
        bottomLeft, upperRight = size
        mapWidth, mapHeight = (upperRight - bottomLeft) / minimapSize
        viewpoint = (upperRight + bottomLeft) * 0.5
        pointsData = []
        for team, points in enumerate(teamBasePositions, 1):
            for baseNumber, basePoint in enumerate(points.values(), 2):
                pos = (basePoint[0], 0, basePoint[1])
                if isCurrentBattle:
                    pointType = 'base'
                    color = 'blue' if team == playerTeam else 'red'
                else:
                    pointType = 'control'
                    color = 'empty'
                pointsData.append({'x': pos[0] / mapWidth - viewpoint.x * 0.5,
                 'y': pos[2] / mapHeight - viewpoint.y * 0.5,
                 'pointType': pointType,
                 'color': color,
                 'id': baseNumber if len(points) > 1 else 1})

        return pointsData

    def getDisplayableData(self, *args, **kwargs):
        import ArenaType
        from gui.prb_control.items.stronghold_items import isEnemyBattleIndex
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            entity = dispatcher.getEntity()
            if not entity.isStrongholdSettingsValid():
                return
            data = entity.getStrongholdSettings().getData()
            header = data.getHeader()
            reserves = data.getReserve()
            battleIndex = args[0]
            battleSeriesStatus = header.getBattleSeriesStatus()
            battle = battleSeriesStatus[battleIndex]
            isCurrentBattle = battle.getCurrentBattle()
            mapVisible = battle.getMapId() is not None
            arenaType = ArenaType.g_cache[battle.getMapId()] if mapVisible else None
            clan = header.getClan()
            if arenaType:
                mapName = _ms(FORTIFICATIONS.STRONGHOLDBUILDS_MAPNAME, mapName=arenaType.name)
            else:
                mapName = _ms(FORTIFICATIONS.STRONGHOLDBUILDS_MAPUNKNOWN)
            isEnemyBuilding = isEnemyBattleIndex(battleIndex)
            direction = getBuildsDirection(header.getDirection())
            if isEnemyBuilding:
                infoDirection = _ms(FORTIFICATIONS.STRONGHOLDBUILDS_DIRECTIONENEMY, direction=direction)
            else:
                infoDirection = _ms(FORTIFICATIONS.STRONGHOLDBUILDS_DIRECTION, direction=direction)
            toolTipData = {}
            toolTipData['infoTitle'] = self.__getTitle(battleIndex)
            resourceMultiplier = header.getIndustrialResourceMultiplier()
            rewardOnePoint = battle.getBattleReward()
            rewardTotal = rewardOnePoint
            rewardRequisition = int(rewardTotal * reserves.getRequisitionBonusPercent() / 100)
            if isEnemyBuilding:
                rewardResourceMultiplier = rewardOnePoint * (resourceMultiplier - 1)
                rewardTotal += rewardResourceMultiplier
            rewardTotal += rewardRequisition
            toolTipData['infoMapName'] = mapName
            toolTipData['infoDirection'] = infoDirection
            toolTipData['infoTotalValue'] = str(rewardTotal)
            toolTipData['infoDescription1'] = self.__getPointReward(battleIndex)
            toolTipData['infoValue1'] = str(rewardOnePoint)
            if isEnemyBuilding and rewardResourceMultiplier:
                toolTipData['infoDescription2'] = _ms(FORTIFICATIONS.STRONGHOLDBUILDS_REWARDFIRSTTIME, reward=str(resourceMultiplier))
                toolTipData['infoValue2'] = str(rewardResourceMultiplier)
            if rewardRequisition:
                toolTipData['infoDescription3'] = _ms(FORTIFICATIONS.STRONGHOLDBUILDS_REWARDREQUISITION)
                toolTipData['infoValue3'] = str(rewardRequisition)
            toolTipData['infoTotalDescription'] = _ms(FORTIFICATIONS.STRONGHOLDBUILDS_TOTALDESCRIPTION)
            toolTipData['isMapEnabled'] = mapVisible
            if mapVisible:
                toolTipData['mapTexture'] = RES_ICONS.getMapPath(arenaType.geometryName)
                toolTipData['mapPoints'] = arenaType.controlPoints or []
                playerTeam = 1 if clan.getId() == battle.getFirstClanId() else 2
                toolTipData['mapPoints'] = self.buildMapPoints(arenaType.boundingBox, arenaType.teamBasePositions, playerTeam, isCurrentBattle)
            return toolTipData


class FortToolTipData(ToolTipBaseData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(FortToolTipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)


class FortificationsSlotToolTipData(FortToolTipData):
    itemsCache = dependency.descriptor(IItemsCache)

    def getDisplayableData(self, index, unitMgrID=None):
        if unitMgrID is not None:
            unitMgrID = int(unitMgrID)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            entity = dispatcher.getEntity()
            vehicleGetter = self.itemsCache.items.getItemByCD
            slotFilters = entity.getSlotFilters()
            vehicleCDs = slotFilters.get(index, {}).get('vehicle_cds', [])
            conditions = []
            leftCount = len(vehicleCDs) - _MAX_VEHICLES_COUNT
            for vehicleCD in vehicleCDs[:_MAX_VEHICLES_COUNT]:
                conditions.append({'vehicle': vo_converters.makeVehicleVO(vehicleGetter(vehicleCD))})

            return {'conditions': conditions,
             'isCreator': True,
             'toolTipType': TOOLTIPS_CONSTANTS.FORT_SORTIE_SLOT,
             'leftCount': leftCount if leftCount > 0 else 0}
        else:
            super(FortificationsSlotToolTipData, self).getDisplayableData(index, unitMgrID)
            return
