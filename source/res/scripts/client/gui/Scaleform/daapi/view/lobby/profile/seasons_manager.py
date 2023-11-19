# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/seasons_manager.py
import typing
from gui.Scaleform.daapi.view.lobby.comp7.comp7_profile_helper import getDropdownKeyBySeason, getSeasonName, COMP7_ARCHIVE_NAMES, getDropdownKeyByArchiveName, isComp7Archive, getArchiveName
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import BattleTypesDropDownItems
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import RankedDossierKeys
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController, IComp7Controller
if typing.TYPE_CHECKING:
    from skeletons.gui.game_control import ISeasonProvider

class ISeasonsManager(object):

    def setSeason(self, seasonId):
        raise NotImplementedError

    def getSeason(self):
        raise NotImplementedError

    def addSeasonsDropdown(self, vo):
        raise NotImplementedError

    def getStats(self, dossierStats):
        raise NotImplementedError

    def getPlayersStatsBtnEnabled(self):
        raise NotImplementedError


class _BaseSeasonManager(ISeasonsManager):

    def __init__(self):
        self._seasonKey = None
        return

    def setSeason(self, seasonId):
        if self._seasonKey == seasonId:
            return False
        self._seasonKey = seasonId
        return True

    def getSeason(self):
        return self._seasonKey

    def addSeasonsDropdown(self, targetVO):
        targetVO['showSeasonDropdown'] = showDropDown = self._showSeasonsDropDown()
        if showDropDown:
            seasonItems = targetVO['seasonItems'] = self._makeSeasonsDropDown()
            seasonIndex = 0
            for i, seasonItem in enumerate(seasonItems):
                if seasonItem['key'] == self._seasonKey:
                    seasonIndex = i

            targetVO['seasonIndex'] = seasonIndex
            targetVO['dropdownSeasonLabel'] = backport.text(R.strings.profile.seasons.dropdown_label())
            targetVO['seasonEnabled'] = True

    def getPlayersStatsBtnEnabled(self):
        return False

    def getStats(self, dossierStats):
        return None

    def _showSeasonsDropDown(self):
        return False

    def _getLastActiveSeason(self):
        if not self._getSeasonsProvider():
            return None
        currentSeason = self._getSeasonsProvider().getCurrentSeason()
        if currentSeason:
            return currentSeason
        seasons = self._getSeasonsProvider().getSeasonsPassed()
        if seasons:
            seasons.sort()
            return self._getSeasonsProvider().getSeason(seasons[-1][0])
        else:
            return None

    def _makeSeasonsDropDown(self):
        if self._getSeasonsProvider() is None:
            return []
        else:
            sortedSeasons = sorted(self._getSeasonsProvider().getSeasonsPassed(), key=lambda seasonData: seasonData[1])
            seasonIds = [ seasonID for seasonID, _ in sortedSeasons ]
            currentSeason = self._getSeasonsProvider().getCurrentSeason()
            if currentSeason:
                seasonIds.append(currentSeason.getSeasonID())
            result = BattleTypesDropDownItems()
            for seasonID in seasonIds:
                season = self._getSeasonsProvider().getSeason(seasonID)
                if season:
                    self._addSeasonToDropDown(result, seasonID, season)

            return result

    def _getSeasonsProvider(self):
        return None

    @staticmethod
    def _addSeasonToDropDown(itemsList, seasonID, season):
        return itemsList.addByKey(seasonID)


class _RankedSeasonsManager(_BaseSeasonManager):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __RANKED_SEASONS_ARCHIVE = 'archive'
    __RANKED_SEASONS_ARCHIVE_10x10 = '_10x10'

    def __init__(self):
        super(_RankedSeasonsManager, self).__init__()
        self._seasonKey = self.__RANKED_SEASONS_ARCHIVE
        season = self._getLastActiveSeason()
        if season is not None and not self.__rankedController.hasSpecialSeason():
            self._seasonKey = str(season.getSeasonID())
        return

    def addSeasonsDropdown(self, targetVO):
        super(_RankedSeasonsManager, self).addSeasonsDropdown(targetVO)
        targetVO['playersStats'] = self.getPlayersStatsBtnEnabled()

    def getPlayersStatsBtnEnabled(self):
        if self.__rankedController.isEnabled():
            lastActiveSeason = self._getLastActiveSeason()
            if lastActiveSeason is not None:
                return str(lastActiveSeason.getSeasonID()) == self._seasonKey
        return False

    def getStats(self, dossierStats):
        if self._seasonKey == self.__RANKED_SEASONS_ARCHIVE:
            return dossierStats.getSeasonRankedStats(self.__RANKED_SEASONS_ARCHIVE_10x10, 0)
        season = self.__rankedController.getSeason(int(self._seasonKey))
        if season:
            seasonKey = RankedDossierKeys.SEASON % season.getNumber()
            seasonID = season.getSeasonID()
            return dossierStats.getSeasonRankedStats(seasonKey, seasonID)

    def _showSeasonsDropDown(self):
        return self.__hasRankedSeasonsHistory() and not self.__rankedController.hasSpecialSeason()

    def _makeSeasonsDropDown(self):
        itemsList = BattleTypesDropDownItems()
        itemsList.addWithKeyAndLabel(self.__RANKED_SEASONS_ARCHIVE, backport.text(R.strings.profile.profile.ranked.seasonsdropdown.archive()))
        itemsList.extend(super(_RankedSeasonsManager, self)._makeSeasonsDropDown())
        return itemsList

    def _getSeasonsProvider(self):
        return self.__rankedController

    @staticmethod
    def _addSeasonToDropDown(itemsList, seasonID, season):
        localeKey = R.strings.profile.profile.ranked.seasonsdropdown
        itemsList.addWithKeyAndLabel(str(seasonID), backport.text(localeKey.num(season.getNumber())()))

    def __hasRankedSeasonsHistory(self):
        passedSeasons = len(self.__rankedController.getSeasonsPassed())
        return passedSeasons >= 1 or self.__rankedController.getCurrentSeason() is not None


class _Comp7SeasonsManager(_BaseSeasonManager):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(_Comp7SeasonsManager, self).__init__()
        season = self._getLastActiveSeason()
        seasonNumber = season.getNumber() if season is not None else 1
        self._seasonKey = getDropdownKeyBySeason(seasonNumber)
        return

    def getStats(self, dossierStats):
        return dossierStats.getComp7Stats(archive=getArchiveName(self._seasonKey)) if isComp7Archive(self._seasonKey) else dossierStats.getComp7Stats(season=getSeasonName(self._seasonKey))

    def _makeSeasonsDropDown(self):
        itemsList = BattleTypesDropDownItems()
        for archive in COMP7_ARCHIVE_NAMES:
            itemsList.addByKey(getDropdownKeyByArchiveName(archive))

        itemsList.extend(super(_Comp7SeasonsManager, self)._makeSeasonsDropDown())
        return itemsList

    def _showSeasonsDropDown(self):
        return len(self._makeSeasonsDropDown()) > 1

    def _getSeasonsProvider(self):
        return self.__comp7Controller

    @staticmethod
    def _addSeasonToDropDown(itemsList, seasonID, season):
        return itemsList.addByKey(getDropdownKeyBySeason(season.getNumber()))


class _ManagersCollection(ISeasonsManager):
    DEFAULT_MANAGER_KEY = 'default'

    def __init__(self, managersMap):
        self.__managersMap = managersMap
        self.__activeManager = managersMap[self.DEFAULT_MANAGER_KEY]

    def clear(self):
        self.__activeManager = None
        self.__managersMap = {}
        return

    def onBattleTypeSwitched(self, battleType):
        if battleType in self.__managersMap:
            self.__activeManager = self.__managersMap[battleType]
        else:
            self.__activeManager = self.__managersMap[self.DEFAULT_MANAGER_KEY]

    def getStats(self, accountDossier):
        return self.__activeManager.getStats(accountDossier)

    def addSeasonsDropdown(self, vo):
        self.__activeManager.addSeasonsDropdown(vo)

    def setSeason(self, seasonId):
        return self.__activeManager.setSeason(seasonId)

    def getSeason(self):
        return self.__activeManager.getSeason()

    def getPlayersStatsBtnEnabled(self):
        return self.__activeManager.getPlayersStatsBtnEnabled()


def makeStatisticsSeasonManagers():
    return _ManagersCollection({_ManagersCollection.DEFAULT_MANAGER_KEY: _BaseSeasonManager(),
     PROFILE_DROPDOWN_KEYS.RANKED_10X10: _RankedSeasonsManager(),
     PROFILE_DROPDOWN_KEYS.COMP7: _Comp7SeasonsManager()})


def makeTechniqueSeasonManagers():
    return _ManagersCollection({_ManagersCollection.DEFAULT_MANAGER_KEY: _BaseSeasonManager(),
     PROFILE_DROPDOWN_KEYS.COMP7: _Comp7SeasonsManager()})
