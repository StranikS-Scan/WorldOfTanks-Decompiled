# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/fort_data_receivers.py
from ConnectionManager import connectionManager
from adisp import process, async
from constants import FORT_BUILDING_TYPE, DOSSIER_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.Scaleform.locale.CLANS import CLANS
from gui.clans.items import BuildingStats, Building
from helpers import time_utils
from helpers.i18n import makeString as _ms
from predefined_hosts import g_preDefinedHosts
from FortifiedRegionBase import NOT_ACTIVATED
from gui.shared.fortifications import formatters as fort_fmts, isStartingScriptDone
from gui.shared.fortifications.events_dispatcher import loadFortView
from gui.shared.fortifications.FortBuilding import FortBuilding
from gui.shared.gui_items.dossier import _Dossier
from gui.shared.gui_items.dossier.stats import FortRegionSortiesStats, FortRegionBattlesStats
from gui.Scaleform.daapi.view.lobby.clans.profile.clan_statistics_vos import FortSortiesStatisticsVO, FortBattlesStatisticsVO
from gui.Scaleform.daapi.view.lobby.fortifications import FortClanStatisticsData
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortTransportationViewHelper import FortTransportationViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from shared_utils import makeTupleByDict

def _getFortBuildingsVO(sortiesStats, battlesStats, buildingList, texts):
    return {'sortiesStats': sortiesStats,
     'battlesStats': battlesStats,
     'fortSortiesSchema': {'canAddBuilding': False,
                           'buildingData': buildingList,
                           'texts': texts}}


def _getNoFortBuildingsVO():
    return {}


def _getFortSortiesSchemaTexts(activatedDefModeParams, peripheryID, buildingsCount, dirsCount):
    if activatedDefModeParams:
        dayOff, defHour, vacation = activatedDefModeParams
        if dayOff == NOT_ACTIVATED:
            dayOffString = _ms(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_NODAYOFF)
        else:
            dayOffString = fort_fmts.getDayOffString(dayOff)
        defHourStart, _ = defHour or (None, None)
        if defHourStart is not None:
            defHour = fort_fmts.getDefencePeriodString(defHourStart)
        else:
            defHour = ''
        vacStart, vacEnd = vacation
        if vacStart is not None:
            vacationString = fort_fmts.getVacationPeriodString(vacStart, vacEnd)
        else:
            vacationString = _ms(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_NOVACATION)
    else:
        defHour = CLANS.SECTION_FORT_DEFENCE_NOTACTIVATED
        vacationString = dayOffString = None
    periphery = g_preDefinedHosts.periphery(peripheryID)
    if periphery is not None:
        serverName = periphery.name
    else:
        serverName = connectionManager.serverUserName
    return {'totalBuildingsCount': str(buildingsCount),
     'totalDirectionsCount': str(dirsCount),
     'defenceHour': defHour,
     'server': serverName,
     'vacation': vacationString,
     'dayOff': dayOffString}


class _UserDossierAdapter(_Dossier):

    def __init__(self, info):
        dossier = {'fortSorties': {'battlesCount': info.getSortieBattlesCount(),
                         'wins': info.getSortieWinsCount(),
                         'losses': info.getSortieLossesCount(),
                         'middleBattlesCount': info.getSortieMiddleBattlesCount(),
                         'championBattlesCount': info.getSortieChampionBattlesCount(),
                         'absoluteBattlesCount': info.getSortieAbsoluteBattlesCount(),
                         'fortResourceInMiddle': info.getSortieMiddleResourcesCount(),
                         'fortResourceInChampion': info.getSortieChampionResourcesCount(),
                         'fortResourceInAbsolute': info.getSortieAbsoluteResourcesCount()},
         'fortBattles': {'battlesCount': info.getDefenceBattlesCount(),
                         'wins': info.getDefenceCombatsCount(),
                         'resourceCaptureCount': info.getDefenceCapturedResourcesCount(),
                         'resourceLossCount': info.getDefenceLostResourcesCount(),
                         'enemyBaseCaptureCount': info.getDefenceEnemyBaseCapturesPointsCount(),
                         'captureEnemyBuildingTotalCount': info.getDefenceCapturedEnemyBuildingsCount(),
                         'lossOwnBuildingTotalCount': info.getDefenceLostOwnBuildingsCount(),
                         'attackCount': info.getAttacksCount(),
                         'successAttackCount': info.getSuccessAttacksCount(),
                         'defenceCount': info.getDefencesCount(),
                         'successDefenceCount': info.getSuccessDefencesCount()}}
        super(_UserDossierAdapter, self).__init__(dossier, DOSSIER_TYPE.ACCOUNT)


class _BaseDataReceiver(object):

    @async
    def requestFort(self, clanDossier, callback):
        raise NotImplementedError

    @async
    def hasFort(self, clanDossier, callback):
        raise NotImplementedError

    def createFort(self):
        raise NotImplementedError


class ClanDataReceiver(_BaseDataReceiver, FortViewHelper):

    @async
    @process
    def requestFort(self, clanDossier, callback):
        sInfo = yield clanDossier.requestStrongholdInfo()
        if sInfo.hasFort():
            sStats = yield clanDossier.requestStrongholdStatistics()
            buildings = self._makeBuildingsList(sInfo.getBuildings(), sStats)
            dossierDescriptor = _UserDossierAdapter(sInfo)
            defModeParams = None
            if sInfo.isDefenceModeActivated():
                defence_hour = sInfo.getDefenceHour()
                dHours = None
                if defence_hour is not None:
                    hour = time_utils.getTimeTodayForUTC(defence_hour.hour)
                    dHours = (hour, hour + time_utils.ONE_HOUR)
                defModeParams = (sStats.getOffDay(), dHours, sStats.getVacationInfo())
            data = _getFortBuildingsVO(FortSortiesStatisticsVO(FortRegionSortiesStats(dossierDescriptor), sStats.getFsBattlesCount28d(), sStats.getFsWinsCount28d()), FortBattlesStatisticsVO(FortRegionBattlesStats(dossierDescriptor), sInfo.getFbBattlesCount8(), sInfo.getFbBattlesCount10()), buildings, _getFortSortiesSchemaTexts(defModeParams, sStats.getPeripheryID(), len(buildings), sStats.getDirectionsCount()))
        else:
            data = _getNoFortBuildingsVO()
        callback(data)
        return

    @async
    @process
    def hasFort(self, clanDossier, callback):
        sInfo = yield clanDossier.requestStrongholdInfo()
        callback(sInfo.hasFort())

    def createFort(self):
        LOG_ERROR('Cannot create fort from another player clan card')

    def _makeBuildingsList(self, buildings, sStats):
        MAX_BUILDINGS_PER_DIRECTION = 2
        directions = sStats.getDirectionsIDs()
        buildingsDict = dict(map(lambda dirId: (dirId, [None] * MAX_BUILDINGS_PER_DIRECTION), directions))
        buildingsDict[0] = [None]
        for building in buildings:
            stats = sStats.getBuildingStats(building.type)
            buildingsDict[building.direction][building.position] = self._makeBuildingVO(building, stats)

        result = []
        for dirID in buildingsDict:
            dirBuildings = buildingsDict[dirID]
            for i, building in enumerate(dirBuildings):
                result.append(building or self._makeFoundationBuilding(direction=dirID, position=i))

        return result

    def _makeBuildingVO(self, building, stats):
        typeID = building.type
        uid = self.UI_BUILDINGS_BIND[typeID]
        descr = FortBuilding(typeID=typeID)
        level = building.level
        return {'uid': uid,
         'defResVal': stats.storage,
         'maxDefResValue': descr.levelRef.storage,
         'hpVal': stats.hp,
         'maxHpValue': descr.levelRef.hp,
         'buildingLevel': level,
         'animationType': FORTIFICATION_ALIASES.WITHOUT_ANIMATION,
         'iconSource': self.getMapIconSource(uid, level, stats.hp, descr.levelRef.hp, False, False),
         'isAvailable': True,
         'direction': building.direction,
         'position': building.position,
         'progress': self._getProgress(typeID, level),
         'toolTipData': [uid, self.getCommonBuildTooltipData(descr)],
         'directionType': self._getUpgradeLevelByBuildingLevel(FORTIFICATION_ALIASES.FORT_BASE_BUILDING, level, isDefenceOn=False)}

    def _makeFoundationBuilding(self, direction, position):
        uid = self.FORT_UNKNOWN
        return {'uid': uid,
         'direction': direction,
         'position': position,
         'progress': FORTIFICATION_ALIASES.STATE_TROWEL,
         'directionType': self._getUpgradeLevelByBuildingLevel(FORTIFICATION_ALIASES.FORT_BASE_BUILDING, 0, isDefenceOn=False)}


class OwnClanDataReceiver(_BaseDataReceiver, FortTransportationViewHelper):

    @async
    def hasFort(self, clanDossier, callback):
        callback(isStartingScriptDone())

    @async
    @process
    def requestFort(self, clanDossier, callback):
        fortData = yield FortClanStatisticsData.getDataObject()
        sInfo = yield clanDossier.requestStrongholdInfo()
        sStats = yield clanDossier.requestStrongholdStatistics()
        if fortData is not None:
            fort = fortData.fortCtrl.getFort()
            dossier = fort.getFortDossier()
            mapObjects, buildingsCount = self._makeBuildingsList(fort)
            defModeParams = None
            if fort.isDefenceHourEnabled():
                defModeParams = (fort.getLocalOffDay(), fort.getDefencePeriod(), fort.getVacationDate())
            data = _getFortBuildingsVO(FortSortiesStatisticsVO(dossier.getSortiesStats(), sStats.getFsBattlesCount28d(), sStats.getFsWinsCount28d()), FortBattlesStatisticsVO(dossier.getBattlesStats(), sInfo.getFbBattlesCount8(), sInfo.getFbBattlesCount10()), mapObjects, _getFortSortiesSchemaTexts(defModeParams, fort.peripheryID, buildingsCount, len(fort.getOpenedDirections())))
            fortData.stopFortListening()
        else:
            data = _getNoFortBuildingsVO()
        callback(data)
        return

    def createFort(self):
        loadFortView()

    def isOnNextTransportingStep(self):
        return False

    def _makeBuildingsList(self, fort):
        """
        :param fort: data about fort
        :return: (mObjects, buildingsCount) - (map objects info, real count of buildings without building sites)
        """
        mObjects = []
        mObjects.append(self._makeBuilding(fort.getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE), 0, 0))
        buildingsCount = 1
        for dir, buildings in fort.getBuildingsByDirections().iteritems():
            for pos, bDescr in enumerate(buildings):
                mObjects.append(self._makeBuilding(bDescr, dir, pos))
                if bDescr and self._getProgress(bDescr.typeID, bDescr.level) == FORTIFICATION_ALIASES.STATE_BUILDING:
                    buildingsCount += 1

        return (mObjects, buildingsCount)

    def _makeBuilding(self, buildDescr, dir, pos):
        return self._makeBuildingData(buildDescr, dir, pos, False, FORTIFICATION_ALIASES.WITHOUT_ANIMATION)
