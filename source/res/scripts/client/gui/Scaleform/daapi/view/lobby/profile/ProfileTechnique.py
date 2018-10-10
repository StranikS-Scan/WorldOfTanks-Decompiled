# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechnique.py
import BigWorld
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PROFILE_TECHNIQUE_MEMBER
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, MARK_ON_GUN_RECORD, HONORED_RANK_RECORD
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getHofRatingUrlForVehicle, getHofDisabledKeys, onServerSettingsChange, isHofButtonNew, setHofButtonOld
from gui.Scaleform.daapi.view.lobby.hof.web_handlers import createHofWebHandlers
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils, DetailedStatisticsUtils, STATISTICS_LAYOUT, FALLOUT_STATISTICS_LAYOUT
from gui.Scaleform.daapi.view.meta.ProfileTechniqueMeta import ProfileTechniqueMeta
from gui.Scaleform.genConsts.ACHIEVEMENTS_ALIASES import ACHIEVEMENTS_ALIASES
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.dossier.achievements.MarkOfMasteryAchievement import isMarkOfMasteryAchieved
from gui.shared.gui_items.dossier.stats import UNAVAILABLE_MARKS_OF_MASTERY
from helpers import i18n, dependency
from nations import NAMES
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from soft_exception import SoftException
_MARK_ON_GUN_MIN_LVL = 5

class ProfileTechnique(ProfileTechniqueMeta):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, *args):
        super(ProfileTechnique, self).__init__(*args)
        selectedData = self._selectedData
        self._selectedVehicleIntCD = selectedData.get('itemCD') if selectedData else None
        return

    def showVehiclesRating(self):
        setHofButtonOld(PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON)
        self.eventsCache.onProfileVisited()
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BROWSER_VIEW, ctx={'url': getHofRatingUrlForVehicle(self._selectedVehicleIntCD),
         'returnAlias': VIEW_ALIAS.LOBBY_PROFILE,
         'allowRightClick': True,
         'webHandlers': createHofWebHandlers(),
         'itemCD': self._selectedVehicleIntCD,
         'disabledKeys': getHofDisabledKeys(),
         'onServerSettingsChange': onServerSettingsChange}), EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(ProfileTechnique, self)._populate()
        self._setRatingButton()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _dispose(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(ProfileTechnique, self)._dispose()

    def _getInitData(self, accountDossier=None, isFallout=False):
        dropDownProvider = [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.ALL), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.EPIC_RANDOM), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED)]
        self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FALLOUT)
        if accountDossier is not None and accountDossier.getHistoricalStats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.HISTORICAL))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.TEAM))
        if accountDossier is not None and accountDossier.getRated7x7Stats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.STATICTEAM))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.CLAN))
        if self.lobbyContext.getServerSettings().isStrongholdsEnabled():
            dropDownProvider.extend((self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES)))
        storedData = self._getStorageData()
        return {'dropDownProvider': dropDownProvider,
         'tableHeader': self._getTableHeader(isFallout),
         'selectedColumn': storedData['selectedColumn'],
         'selectedColumnSorting': storedData['selectedColumnSorting']}

    def _setRatingButton(self):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.ALL and self.lobbyContext.getServerSettings().isHofEnabled():
            self.as_setRatingButtonS({'enabled': True,
             'visible': True})
            if isHofButtonNew(PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON):
                self.as_setBtnCountersS([{'componentId': PROFILE_CONSTANTS.HOF_VIEW_RATING_BUTTON,
                  'count': '1'}])
            else:
                self.as_setBtnCountersS([])
        else:
            self.as_setRatingButtonS({'enabled': False,
             'visible': False})

    def setSelectedTableColumn(self, index, sortDirection):
        storedDataId = self._getStorageId()
        storedData = AccountSettings.getFilter(storedDataId)
        storedData['selectedColumn'] = index
        storedData['selectedColumnSorting'] = sortDirection
        AccountSettings.setFilter(storedDataId, storedData)

    def invokeUpdate(self):
        super(ProfileTechnique, self).invokeUpdate()
        self._setRatingButton()

    def _getStorageId(self):
        return PROFILE_TECHNIQUE_MEMBER

    def _getStorageData(self):
        return AccountSettings.getFilter(self._getStorageId())

    def _getTableHeader(self, isFallout=False):
        markOfMasteryEnabled = self._battlesType == PROFILE_DROPDOWN_KEYS.ALL or self._battlesType == PROFILE_DROPDOWN_KEYS.EPIC_RANDOM or self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED
        return (self._createTableBtnInfo('nationIndex', 36, 0, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_NATION, 'ascending', iconSource=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, inverted=True),
         self._createTableBtnInfo('typeIndex', 34, 1, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_TECHNIQUE, 'descending', iconSource=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL),
         self._createTableBtnInfo('level', 32, 2, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_LVL, 'descending', iconSource=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL),
         self._createTableBtnInfo('shortUserName', 154, 7, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_NAME, 'ascending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_VEHICLENAME, inverted=True, sortType='string'),
         self._createTableBtnInfo('battlesCount', 74, 3, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_BATTLESCOUNT, 'descending', label=PROFILE.SECTION_SUMMARY_SCORES_TOTALBATTLES),
         self._createTableBtnInfo('winsEfficiency', 74, 4, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_WINS if isFallout else PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_WINRATE, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_TOTALWINS),
         self._createTableBtnInfo('avgExperience', 90, 5, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_AVGEXP, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_AVGEXPERIENCE),
         self._createTableBtnInfo('markOfMastery', 83, 6, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_MARKSOFMASTERY, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_CLASSINESS, enabled=markOfMasteryEnabled))

    def _createTableBtnInfo(self, iconId, buttonWidth, sortOrder, toolTip, defaultSortDirection, label='', iconSource='', inverted=False, sortType='numeric', showSeparator=True, enabled=True):
        return {'id': iconId,
         'buttonWidth': buttonWidth,
         'sortOrder': sortOrder,
         'toolTip': toolTip,
         'defaultSortDirection': defaultSortDirection,
         'label': label,
         'iconSource': iconSource,
         'inverted': inverted,
         'sortType': sortType,
         'showSeparator': showSeparator,
         'ascendingIconSource': RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_ASCPROFILESORTARROW,
         'descendingIconSource': RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_DESCPROFILESORTARROW,
         'buttonHeight': 40,
         'enabled': enabled}

    def getEmptyScreenLabel(self):
        emptyScreenLabelsDictionary = {PROFILE_DROPDOWN_KEYS.ALL: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_ALL,
         PROFILE_DROPDOWN_KEYS.FALLOUT: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_FALLOUT,
         PROFILE_DROPDOWN_KEYS.TEAM: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_TEAM,
         PROFILE_DROPDOWN_KEYS.STATICTEAM: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_STATICTEAM,
         PROFILE_DROPDOWN_KEYS.HISTORICAL: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_HISTORICAL,
         PROFILE_DROPDOWN_KEYS.CLAN: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_GLOBALMAP,
         PROFILE_DROPDOWN_KEYS.RANKED: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_RANKED,
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_FORTBATTLES,
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_FORTSORTIES,
         PROFILE_DROPDOWN_KEYS.EPIC_RANDOM: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_EPICRANDOM}
        return i18n.makeString(emptyScreenLabelsDictionary[self._battlesType])

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileTechnique, self)._sendAccountData(targetData, accountDossier)
        self.as_setInitDataS(self._getInitData(accountDossier, self._battlesType == PROFILE_DROPDOWN_KEYS.FALLOUT))
        self.as_responseDossierS(self._battlesType, self._getTechniqueListVehicles(targetData), '', self.getEmptyScreenLabel())

    def _getTechniqueListVehicles(self, targetData, addVehiclesThatInHangarOnly=False):
        result = []
        if self.lobbyContext.getServerSettings().isEpicRandomMarkOfMasteryEnabled():
            __markOfMasteryBattles = (PROFILE_DROPDOWN_KEYS.ALL, PROFILE_DROPDOWN_KEYS.EPIC_RANDOM, PROFILE_DROPDOWN_KEYS.RANKED)
        else:
            __markOfMasteryBattles = (PROFILE_DROPDOWN_KEYS.ALL, PROFILE_DROPDOWN_KEYS.RANKED)
        showMarkOfMastery = self._battlesType in __markOfMasteryBattles and targetData.getMarksOfMastery() != UNAVAILABLE_MARKS_OF_MASTERY
        for intCD, (battlesCount, wins, xp) in targetData.getVehicles().iteritems():
            avgXP = xp / battlesCount if battlesCount else 0
            vehicle = self.itemsCache.items.getItemByCD(intCD)
            if vehicle is not None:
                isInHangar = vehicle.invID > 0
                if addVehiclesThatInHangarOnly and not isInHangar:
                    continue
                if self._battlesType == PROFILE_DROPDOWN_KEYS.FALLOUT:
                    winsEfficiency = wins
                    winsEfficiencyStr = BigWorld.wg_getIntegralFormat(winsEfficiency)
                else:
                    winsEfficiency = 100.0 * wins / battlesCount if battlesCount else 0
                    winsEfficiencyStr = BigWorld.wg_getIntegralFormat(round(winsEfficiency)) + '%'
                if showMarkOfMastery:
                    markOfMastery = targetData.getMarkOfMasteryForVehicle(intCD)
                    if not isMarkOfMasteryAchieved(markOfMastery):
                        markOfMastery = ProfileUtils.UNAVAILABLE_VALUE
                else:
                    markOfMastery = ProfileUtils.UNAVAILABLE_VALUE
                result.append({'id': intCD,
                 'inventoryID': vehicle.invID,
                 'shortUserName': vehicle.shortUserName,
                 'battlesCount': battlesCount,
                 'winsEfficiency': winsEfficiency,
                 'winsEfficiencyStr': winsEfficiencyStr,
                 'avgExperience': avgXP,
                 'userName': vehicle.userName,
                 'typeIndex': VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[vehicle.type],
                 'nationIndex': GUI_NATIONS_ORDER_INDEX[NAMES[vehicle.nationID]],
                 'nationID': vehicle.nationID,
                 'level': vehicle.level,
                 'markOfMastery': markOfMastery,
                 'markOfMasteryBlock': ACHIEVEMENT_BLOCK.TOTAL,
                 'tankIconPath': vehicle.iconSmall,
                 'typeIconPath': '../maps/icons/filters/tanks/%s.png' % vehicle.type,
                 'isInHangar': isInHangar,
                 'compareModeAvailable': self.comparisonBasket.isEnabled()})

        return result

    def requestData(self, data):
        pass

    def _receiveVehicleDossier(self, vehicleIntCD, databaseId):
        vehDossier = self.itemsCache.items.getVehicleDossier(vehicleIntCD, databaseId)
        achievementsList = None
        specialMarksStats = []
        specialRankedStats = []
        if self._battlesType in (PROFILE_DROPDOWN_KEYS.ALL, PROFILE_DROPDOWN_KEYS.EPIC_RANDOM):
            achievementsEnabled = True
            if self._battlesType == PROFILE_DROPDOWN_KEYS.ALL:
                stats = vehDossier.getRandomStats()
            elif self._battlesType == PROFILE_DROPDOWN_KEYS.EPIC_RANDOM:
                stats = vehDossier.getEpicRandomStats()
                achievementsEnabled = self.lobbyContext.getServerSettings().isEpicRandomAchievementsEnabled()
            if achievementsEnabled:
                achievementsList = self.__getAchievementsList(stats, vehDossier)
            if self.__showMarksOnGun(vehicleIntCD):
                if self._battlesType != PROFILE_DROPDOWN_KEYS.EPIC_RANDOM or self.lobbyContext.getServerSettings().isEpicRandomMarksOnGunEnabled():
                    specialMarksStats.append(self.__packAchievement(stats, vehDossier, MARK_ON_GUN_RECORD))
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.TEAM:
            stats = vehDossier.getTeam7x7Stats()
            achievementsList = self.__getAchievementsList(stats, vehDossier)
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.STATICTEAM:
            stats = vehDossier.getRated7x7Stats()
            achievementsList = self.__getAchievementsList(stats, vehDossier)
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.HISTORICAL:
            stats = vehDossier.getHistoricalStats()
            achievementsList = self.__getAchievementsList(stats, vehDossier)
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES:
            stats = vehDossier.getFortSortiesStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES:
            stats = vehDossier.getFortBattlesStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.CLAN:
            stats = vehDossier.getGlobalMapStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.FALLOUT:
            stats = vehDossier.getFalloutStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
            stats = vehDossier.getRankedStats()
            achievementsList = self.__getAchievementsList(stats, vehDossier)
            specialRankedStats.append(self.__packAchievement(stats, vehDossier, HONORED_RANK_RECORD))
        else:
            raise SoftException('Profile Technique: Unknown battle type: ' + self._battlesType)
        if achievementsList is not None:
            achievementsList.insert(0, specialRankedStats)
            achievementsList.insert(1, specialMarksStats)
        if self._battlesType == PROFILE_DROPDOWN_KEYS.FALLOUT:
            layout = FALLOUT_STATISTICS_LAYOUT
        else:
            layout = STATISTICS_LAYOUT
        preparedStatistics = DetailedStatisticsUtils.getStatistics(stats, self._userID is None, layout)
        self._selectedVehicleIntCD = vehicleIntCD
        self.as_responseVehicleDossierS({'detailedData': preparedStatistics,
         'achievements': achievementsList})
        return

    def __getAchievementsList(self, targetData, vehDossier):
        packedList = []
        achievements = targetData.getAchievements(True)
        for achievementBlockList in achievements:
            packedList.append(AchievementsUtils.packAchievementList(achievementBlockList, vehDossier.getDossierType(), dumpDossier(vehDossier), self._userID is None, True, ACHIEVEMENTS_ALIASES.GREY_COUNTER))

        return packedList

    def __onServerSettingChanged(self, diff):
        if 'hallOfFame' in diff:
            self._setRatingButton()

    def __packAchievement(self, stats, vehDossier, record):
        return AchievementsUtils.packAchievement(stats.getAchievement(record), vehDossier.getDossierType(), dumpDossier(vehDossier), self._userID is None)

    def __showMarksOnGun(self, vehicleIntCD):
        return self.itemsCache.items.getItemByCD(int(vehicleIntCD)).level >= _MARK_ON_GUN_MIN_LVL
