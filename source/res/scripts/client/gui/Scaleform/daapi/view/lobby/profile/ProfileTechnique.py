# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechnique.py
from stats_params import BATTLE_ROYALE_STATS_ENABLED
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PROFILE_TECHNIQUE_MEMBER
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, MARK_ON_GUN_RECORD
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getHofRatingUrlForVehicle, getHofDisabledKeys, onServerSettingsChange, isHofButtonNew, setHofButtonOld
from gui.Scaleform.daapi.view.lobby.hof.web_handlers import createHofWebHandlers
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils, DetailedStatisticsUtils, STATISTICS_LAYOUT, FALLOUT_STATISTICS_LAYOUT, BATTLE_ROYALE_VEHICLE_STATISTICS_LAYOUT, COMP7_VEHICLE_STATISTICS_LAYOUT
from gui.Scaleform.daapi.view.meta.ProfileTechniqueMeta import ProfileTechniqueMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.ACHIEVEMENTS_ALIASES import ACHIEVEMENTS_ALIASES
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED, getIconResourceName
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.dossier.achievements import isMarkOfMasteryAchieved
from gui.shared.gui_items.dossier.stats import UNAVAILABLE_MARKS_OF_MASTERY
from helpers import i18n, dependency
from nations import NAMES
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from soft_exception import SoftException
from gui.shared.events import ProfileTechniqueEvent
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
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BROWSER_VIEW), ctx={'url': getHofRatingUrlForVehicle(self._selectedVehicleIntCD),
         'returnAlias': VIEW_ALIAS.LOBBY_PROFILE,
         'allowRightClick': True,
         'webHandlers': createHofWebHandlers(),
         'itemCD': self._selectedVehicleIntCD,
         'disabledKeys': getHofDisabledKeys(),
         'onServerSettingsChange': onServerSettingsChange}), EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        event = ProfileTechniqueEvent(ProfileTechniqueEvent.SELECT_BATTLE_TYPE)
        if self._selectedData and isinstance(self._selectedData, dict):
            event.ctx['eventOwner'] = self._selectedData.get('eventOwner')
        else:
            event.ctx['eventOwner'] = 'achievements'
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
        self._battlesType = event.ctx.get('battlesType', self._battlesType)
        super(ProfileTechnique, self)._populate()
        self._setRatingButton()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _dispose(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(ProfileTechnique, self)._dispose()
        g_eventBus.handleEvent(ProfileTechniqueEvent(ProfileTechniqueEvent.DISPOSE), scope=EVENT_BUS_SCOPE.LOBBY)

    def _getInitData(self, accountDossier=None, isFallout=False):
        dropDownProvider = [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.ALL), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.EPIC_RANDOM)]
        if BATTLE_ROYALE_STATS_ENABLED:
            dropDownProvider += [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD)]
        dropDownProvider += [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED_10X10)]
        self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FALLOUT)
        if accountDossier is not None and accountDossier.getHistoricalStats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.HISTORICAL))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.TEAM))
        if accountDossier is not None and accountDossier.getRated7x7Stats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.STATICTEAM))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.CLAN))
        if self.lobbyContext.getServerSettings().isStrongholdsEnabled():
            dropDownProvider.extend((self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES)))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.COMP7))
        storedData = self._getStorageData()
        return {'dropDownProvider': dropDownProvider,
         'tableHeader': self.__getTableHeader(isFallout),
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

    def _getDefaultTableHeader(self, isFallout=False):
        result = [self._createTableBtnInfo('nationIndex', 36, 0, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_NATION, 'ascending', iconSource=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, inverted=True),
         self._createTableBtnInfo('typeIndex', 34, 1, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_TECHNIQUE, 'descending', iconSource=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL),
         self._createTableBtnInfo('level', 32, 2, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_LVL, 'descending', iconSource=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL),
         self._createTableBtnInfo('shortUserName', 154, 7, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_NAME, 'ascending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_VEHICLENAME, inverted=True, sortType='string'),
         self._createTableBtnInfo('battlesCount', 74, 3, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_BATTLESCOUNT, 'descending', label=PROFILE.SECTION_SUMMARY_SCORES_TOTALBATTLES),
         self._createTableBtnInfo('winsEfficiency', 74, 4, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_WINS if isFallout else PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_WINRATE, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_TOTALWINS),
         self._createTableBtnInfo('avgExperience', 90, 5, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_AVGEXP, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_AVGEXPERIENCE)]
        if self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7:
            result.append(self._createTableBtnInfo('prestigePoints', 83, 6, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_PRESTIGEPOINTS, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_PRESTIGEPOINTS))
        else:
            markOfMasteryEnabled = self._battlesType in (PROFILE_DROPDOWN_KEYS.ALL, PROFILE_DROPDOWN_KEYS.EPIC_RANDOM)
            result.append(self._createTableBtnInfo('markOfMastery', 83, 6, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_MARKSOFMASTERY, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_CLASSINESS, enabled=markOfMasteryEnabled))
        return result

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
         PROFILE_DROPDOWN_KEYS.RANKED_10X10: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_RANKED,
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_FORTBATTLES,
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_FORTSORTIES,
         PROFILE_DROPDOWN_KEYS.EPIC_RANDOM: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_EPICRANDOM,
         PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_BATTLEROYALESOLO,
         PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_BATTLEROYALESQUAD,
         PROFILE_DROPDOWN_KEYS.COMP7: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_COMP7}
        return i18n.makeString(emptyScreenLabelsDictionary[self._battlesType])

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileTechnique, self)._sendAccountData(targetData, accountDossier)
        self.as_setInitDataS(self._getInitData(accountDossier, self._battlesType == PROFILE_DROPDOWN_KEYS.FALLOUT))
        self.as_responseDossierS(self._battlesType, self._getTechniqueListVehicles(targetData), '', self.getEmptyScreenLabel())

    def __getTableHeader(self, isFallout):
        return self.__getBattleRoyaleTableHeader() if self._battlesType in (PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO, PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD) else self._getDefaultTableHeader(isFallout)

    def __getBattleRoyaleTechniqueListVehicles(self, targetData):
        result = []
        vehicles = targetData.getVehicles()
        for vehicleCD, data in vehicles.items():
            battlesCount = data.getBattlesCount()
            winsCount = data.getWinsCount()
            avgXP = data.getAvgXP()
            avgDamage = data.getAvgDamage()
            avgFrags = data.getFragsCount() / battlesCount if battlesCount > 0 else 0
            vehicle = self.itemsCache.items.getItemByCD(vehicleCD)
            iconResId = R.images.gui.maps.icons.battleRoyale.vehicles.dyn(getIconResourceName(vehicle.name))()
            if vehicle is not None:
                result.append({'id': vehicleCD,
                 'inventoryID': vehicle.invID,
                 'shortUserName': vehicle.shortUserName,
                 'battlesCount': battlesCount,
                 'avgExperience': avgXP,
                 'userName': vehicle.userName,
                 'typeIndex': VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[vehicle.type],
                 'nationIndex': GUI_NATIONS_ORDER_INDEX[NAMES[vehicle.nationID]],
                 'nationID': vehicle.nationID,
                 'level': vehicle.level,
                 'tankIconPath': backport.image(iconResId),
                 'typeIconPath': '../maps/icons/filters/tanks/%s.png' % vehicle.type,
                 'winsCount': winsCount,
                 'avgDamage': avgDamage,
                 'avgFrags': avgFrags})

        return result

    def __getBattleRoyaleTableHeader(self):
        return (self._createTableBtnInfo('nationIndex', 36, 0, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_NATION, 'ascending', iconSource=backport.image(R.images.gui.maps.icons.filters.nations.all()), inverted=True),
         self._createTableBtnInfo('typeIndex', 34, 1, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_CLASS, 'descending', iconSource=backport.image(R.images.gui.maps.icons.filters.tanks.all())),
         self._createTableBtnInfo('shortUserName', 171, 7, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_NAME, 'ascending', label=backport.text(R.strings.profile.section.technique.buttonBar.vehicleName()), inverted=True, sortType='string'),
         self._createTableBtnInfo('battlesCount', 64, 2, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_BATTLESCOUNT, 'descending', iconSource=backport.image(R.images.gui.maps.icons.battleRoyale.achievements.battles())),
         self._createTableBtnInfo('winsCount', 64, 3, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_WINS, 'descending', iconSource=backport.image(R.images.gui.maps.icons.battleRoyale.achievements.wins())),
         self._createTableBtnInfo('avgExperience', 64, 4, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_AVGEXP, 'descending', iconSource=backport.image(R.images.gui.maps.icons.battleRoyale.achievements.avgExp())),
         self._createTableBtnInfo('avgDamage', 64, 5, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_AVGDAMAGE, 'descending', iconSource=backport.image(R.images.gui.maps.icons.battleRoyale.achievements.avgDamage())),
         self._createTableBtnInfo('avgFrags', 80, 6, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_AVGFRAGS, 'descending', iconSource=backport.image(R.images.gui.maps.icons.battleRoyale.achievements.avgFrags())))

    def _getTechniqueListVehicles(self, targetData, addVehiclesThatInHangarOnly=False):
        return self.__getBattleRoyaleTechniqueListVehicles(targetData) if self._battlesType in (PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO, PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD) else self.__getDefaultVehicleList(targetData, addVehiclesThatInHangarOnly)

    def __getDefaultVehicleList(self, targetData, addVehiclesThatInHangarOnly=False):
        result = []
        if self.lobbyContext.getServerSettings().isEpicRandomMarkOfMasteryEnabled():
            __markOfMasteryBattles = (PROFILE_DROPDOWN_KEYS.ALL, PROFILE_DROPDOWN_KEYS.EPIC_RANDOM)
        else:
            __markOfMasteryBattles = (PROFILE_DROPDOWN_KEYS.ALL,)
        showMarkOfMastery = self._battlesType in __markOfMasteryBattles and targetData.getMarksOfMastery() != UNAVAILABLE_MARKS_OF_MASTERY
        showPrestigePoints = self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7
        for intCD, vehParams in targetData.getVehicles().iteritems():
            if showPrestigePoints:
                battlesCount, wins, xp, prestigePoints = vehParams
                avgPrestigePoints = round(float(prestigePoints) / float(battlesCount))
            else:
                battlesCount, wins, xp = vehParams
                avgPrestigePoints = ProfileUtils.UNAVAILABLE_VALUE
            avgXP = xp / battlesCount if battlesCount else 0
            vehicle = self.itemsCache.items.getItemByCD(intCD)
            if vehicle is not None:
                isInHangar = vehicle.invID > 0
                if addVehiclesThatInHangarOnly and not isInHangar:
                    continue
                if self._battlesType == PROFILE_DROPDOWN_KEYS.FALLOUT:
                    winsEfficiency = wins
                    winsEfficiencyStr = backport.getIntegralFormat(winsEfficiency)
                else:
                    winsEfficiency = 100.0 * wins / battlesCount if battlesCount else 0
                    winsEfficiencyStr = backport.getIntegralFormat(round(winsEfficiency)) + '%'
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
                 'compareModeAvailable': self.comparisonBasket.isEnabled(),
                 'prestigePoints': avgPrestigePoints})

        return result

    def requestData(self, data):
        pass

    def _receiveVehicleDossier(self, vehicleIntCD, databaseId):
        vehDossier = self.itemsCache.items.getVehicleDossier(vehicleIntCD, databaseId)
        if not vehDossier:
            return
        else:
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
            elif self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED_10X10:
                stats = vehDossier.getRanked10x10Stats()
                achievementsList = self.__getAchievementsList(stats, vehDossier)
            elif self._battlesType == PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO:
                stats = vehDossier.getBattleRoyaleSoloStats(vehicleIntCD)
                if not stats:
                    return
            elif self._battlesType == PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD:
                stats = vehDossier.getBattleRoyaleSquadStats(vehicleIntCD)
                if not stats:
                    return
            elif self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7:
                stats = vehDossier.getComp7Stats()
            else:
                raise SoftException('Profile Technique: Unknown battle type: ' + self._battlesType)
            if achievementsList is not None:
                achievementsList.insert(0, specialRankedStats)
                achievementsList.insert(1, specialMarksStats)
            preparedStatistics = DetailedStatisticsUtils.getStatistics(stats, self._userID is None, self.__getLayout())
            self._selectedVehicleIntCD = vehicleIntCD
            self.as_responseVehicleDossierS({'detailedData': preparedStatistics,
             'achievements': achievementsList})
            return

    def __getLayout(self):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.FALLOUT:
            return FALLOUT_STATISTICS_LAYOUT
        if self._battlesType == PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO:
            return BATTLE_ROYALE_VEHICLE_STATISTICS_LAYOUT
        if self._battlesType == PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD:
            return BATTLE_ROYALE_VEHICLE_STATISTICS_LAYOUT
        return COMP7_VEHICLE_STATISTICS_LAYOUT if self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7 else STATISTICS_LAYOUT

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
