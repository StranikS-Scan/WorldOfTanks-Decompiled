# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechnique.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui import GUI_NATIONS_ORDER_INDEX
from gui.shared.fortifications import isFortificationEnabled
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils, DetailedStatisticsUtils
from gui.Scaleform.daapi.view.meta.ProfileTechniqueMeta import ProfileTechniqueMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared import g_itemsCache
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES
from nations import NAMES
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD

class ProfileTechnique(ProfileSection, ProfileTechniqueMeta):

    def __init__(self, *args):
        ProfileSection.__init__(self, *args)
        ProfileTechniqueMeta.__init__(self)

    def _populate(self):
        super(ProfileTechnique, self)._populate()
        self.as_setInitDataS(self._getInitData())

    def _getInitData(self):
        dropDownProvider = [PROFILE.PROFILE_DROPDOWN_LABELS_ALL, PROFILE.PROFILE_DROPDOWN_LABELS_HISTORICAL, PROFILE.PROFILE_DROPDOWN_LABELS_TEAM]
        if isFortificationEnabled():
            dropDownProvider.append(PROFILE.PROFILE_DROPDOWN_LABELS_FORTIFICATIONS_SORTIES)
        return {'dropDownProvider': dropDownProvider}

    def _sendAccountData(self, targetData, accountDossier):
        self.as_responseDossierS(self._battlesType, self._getTechniqueListVehicles(targetData))

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
        if self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_ALL:
            return markOfMastery
        return ProfileUtils.UNAVAILABLE_VALUE

    def _receiveVehicleDossier(self, vehicleIntCD, databaseId):
        vehDossier = g_itemsCache.items.getVehicleDossier(vehicleIntCD, databaseId)
        achievementsList = None
        specialMarksStats = []
        if self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_ALL:
            stats = vehDossier.getRandomStats()
            achievementsList = self.__getAchievementsList(stats, vehDossier)
            if g_itemsCache.items.getItemByCD(int(vehicleIntCD)).level > 4:
                specialMarksStats.append(ProfileUtils.packAchievement(stats.getAchievement(MARK_ON_GUN_RECORD), vehDossier, self._userID is None))
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_TEAM:
            stats = vehDossier.getTeam7x7Stats()
            achievementsList = self.__getAchievementsList(stats, vehDossier)
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_HISTORICAL:
            stats = vehDossier.getHistoricalStats()
            achievementsList = self.__getAchievementsList(stats, vehDossier)
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_FORTIFICATIONS_SORTIES:
            stats = vehDossier.getFortSortiesStats()
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_FORTIFICATIONS_BATTLES:
            stats = vehDossier.getFortBattlesStats()
        else:
            raise ValueError('Profile Technique: Unknown battle type: ' + self._battlesType)
        if achievementsList is not None:
            achievementsList.insert(0, specialMarksStats)
        self.as_responseVehicleDossierS({'detailedData': DetailedStatisticsUtils.getStatistics(stats),
         'achievements': achievementsList})
        return

    def __getAchievementsList(self, targetData, vehDossier):
        packedList = []
        achievements = targetData.getAchievements(True)
        for achievementBlockList in achievements:
            packedList.append(ProfileUtils.packAchievementList(achievementBlockList, vehDossier, self._userID is None))

        return packedList
