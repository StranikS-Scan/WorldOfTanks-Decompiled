# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechnique.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui.Scaleform.genConsts.ACHIEVEMENTS_ALIASES import ACHIEVEMENTS_ALIASES
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.fortifications import isFortificationEnabled, isFortificationBattlesEnabled
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils, DetailedStatisticsUtils
from gui.Scaleform.daapi.view.meta.ProfileTechniqueMeta import ProfileTechniqueMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared import g_itemsCache
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES
from nations import NAMES
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.shared.gui_items.dossier import dumpDossier
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from helpers import i18n

class ProfileTechnique(ProfileTechniqueMeta):

    def __init__(self, *args):
        super(ProfileTechnique, self).__init__(*args)

    def _populate(self):
        super(ProfileTechnique, self)._populate()
        self.as_setInitDataS(self._getInitData())

    def _getInitData(self):
        dropDownProvider = [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.ALL),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.HISTORICAL),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.TEAM),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.STATICTEAM),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.CLAN)]
        if isFortificationEnabled():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES))
        if isFortificationBattlesEnabled():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES))
        return {'dropDownProvider': dropDownProvider,
         'tableHeader': self._getTableHeader()}

    def _getTableHeader(self):
        return [self._createTableBtnInfo('nationIndex', 36, 0, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_NATION, 'ascending', iconSource=RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL, inverted=True),
         self._createTableBtnInfo('typeIndex', 34, 1, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_TECHNIQUE, 'ascending', iconSource=RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL, inverted=True),
         self._createTableBtnInfo('level', 32, 2, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_LVL, 'descending', iconSource=RES_ICONS.MAPS_ICONS_BUTTONS_TAB_SORT_BUTTON_LEVEL),
         self._createTableBtnInfo('shortUserName', 154, 7, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_NAME, 'ascending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_VEHICLENAME, sortType='string'),
         self._createTableBtnInfo('battlesCount', 74, 3, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_BATTLESCOUNT, 'descending', label=PROFILE.SECTION_SUMMARY_SCORES_TOTALBATTLES),
         self._createTableBtnInfo('winsEfficiency', 74, 4, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_WINS, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_TOTALWINS),
         self._createTableBtnInfo('avgExperience', 90, 5, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_AVGEXP, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_AVGEXPERIENCE),
         self._createTableBtnInfo('markOfMastery', 83, 6, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_MARKSOFMASTERY, 'descending', label=PROFILE.SECTION_TECHNIQUE_BUTTONBAR_CLASSINESS, showSeparator=False)]

    def _createTableBtnInfo(self, iconId, buttonWidth, sortOrder, toolTip, defaultSortDirection, label = '', iconSource = '', inverted = False, sortType = 'numeric', showSeparator = True):
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
         'buttonHeight': 40}

    def getEmptyScreenLabel(self):
        emptyScreenLabelsDictionary = {PROFILE_DROPDOWN_KEYS.ALL: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_ALL,
         PROFILE_DROPDOWN_KEYS.TEAM: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_TEAM,
         PROFILE_DROPDOWN_KEYS.STATICTEAM: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_STATICTEAM,
         PROFILE_DROPDOWN_KEYS.HISTORICAL: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_HISTORICAL,
         PROFILE_DROPDOWN_KEYS.CLAN: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_GLOBALMAP,
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_FORTBATTLES,
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES: PROFILE.SECTION_TECHNIQUE_EMPTYSCREENLABEL_BATTLETYPE_FORTSORTIES}
        return i18n.makeString(emptyScreenLabelsDictionary[self._battlesType])

    def _sendAccountData(self, targetData, accountDossier):
        self.as_responseDossierS(self._battlesType, self._getTechniqueListVehicles(targetData), '', self.getEmptyScreenLabel())

    def _getTechniqueListVehicles(self, targetData, addVehiclesThatInHangarOnly = False):
        result = []
        for intCD, (battlesCount, wins, markOfMastery, xp) in targetData.getVehicles().iteritems():
            avgXP = xp / battlesCount if battlesCount else 0
            vehicle = g_itemsCache.items.getItemByCD(intCD)
            if vehicle is not None:
                isInHangar = vehicle.invID > 0
                if addVehiclesThatInHangarOnly and not isInHangar:
                    continue
                result.append({'id': intCD,
                 'inventoryID': vehicle.invID,
                 'shortUserName': vehicle.shortUserName,
                 'battlesCount': battlesCount,
                 'winsEfficiency': 100.0 * wins / battlesCount if battlesCount else 0,
                 'avgExperience': avgXP,
                 'userName': vehicle.userName,
                 'typeIndex': VEHICLE_TABLE_TYPES_ORDER_INDICES[vehicle.type],
                 'nationIndex': GUI_NATIONS_ORDER_INDEX[NAMES[vehicle.nationID]],
                 'nationID': vehicle.nationID,
                 'level': vehicle.level,
                 'markOfMastery': self.__getMarkOfMasteryVal(markOfMastery),
                 'markOfMasteryBlock': ACHIEVEMENT_BLOCK.TOTAL,
                 'tankIconPath': vehicle.iconSmall,
                 'typeIconPath': '../maps/icons/filters/tanks/%s.png' % vehicle.type,
                 'isInHangar': isInHangar})

        return result

    def requestData(self, data):
        pass

    def __getMarkOfMasteryVal(self, markOfMastery):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.ALL:
            return markOfMastery
        return ProfileUtils.UNAVAILABLE_VALUE

    def _receiveVehicleDossier(self, vehicleIntCD, databaseId):
        vehDossier = g_itemsCache.items.getVehicleDossier(vehicleIntCD, databaseId)
        achievementsList = None
        specialMarksStats = []
        if self._battlesType == PROFILE_DROPDOWN_KEYS.ALL:
            stats = vehDossier.getRandomStats()
            achievementsList = self.__getAchievementsList(stats, vehDossier)
            if g_itemsCache.items.getItemByCD(int(vehicleIntCD)).level > 4:
                specialMarksStats.append(AchievementsUtils.packAchievement(stats.getAchievement(MARK_ON_GUN_RECORD), vehDossier.getDossierType(), dumpDossier(vehDossier), self._userID is None))
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
        else:
            raise ValueError('Profile Technique: Unknown battle type: ' + self._battlesType)
        if achievementsList is not None:
            achievementsList.insert(0, specialMarksStats)
        preparedStatistics = DetailedStatisticsUtils.getStatistics(stats, self._userID is None)
        if self._battlesType == PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES:
            preparedStatistics[0]['data'][0]['tooltip'] = PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FORT_BATTLESCOUNT
        self.as_responseVehicleDossierS({'detailedData': preparedStatistics,
         'achievements': achievementsList})
        return

    def __getAchievementsList(self, targetData, vehDossier):
        packedList = []
        achievements = targetData.getAchievements(True)
        for achievementBlockList in achievements:
            packedList.append(AchievementsUtils.packAchievementList(achievementBlockList, vehDossier.getDossierType(), dumpDossier(vehDossier), self._userID is None, True, ACHIEVEMENTS_ALIASES.GREY_COUNTER))

        return packedList
