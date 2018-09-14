# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileAwards.py
from gui.Scaleform.daapi.view.meta.ProfileAwardsMeta import ProfileAwardsMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from web_stubs import i18n
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.shared.utils.RareAchievementsCache import IMAGE_TYPE
from gui.shared.gui_items.dossier import dumpDossier

class ProfileAwards(ProfileAwardsMeta):

    def __init__(self, *args):
        super(ProfileAwards, self).__init__(*args)
        self.__achievementsFilter = PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_ALL

    @classmethod
    def _getTotalStatsBlock(cls, dossier):
        return dossier.getTotalStats()

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileAwards, self)._sendAccountData(targetData, accountDossier)
        achievements = targetData.getAchievements()
        totalItemsList = []
        for block in achievements:
            totalItemsList.append(len(block))

        if self.__achievementsFilter == PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_INPROCESS:
            achievements = targetData.getAchievements(isInDossier=True)
        elif self.__achievementsFilter == PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_NONE:
            achievements = targetData.getAchievements(isInDossier=False)
        packedList = []
        for achievementBlockList in achievements:
            packedList.append(AchievementsUtils.packAchievementList(achievementBlockList, accountDossier.getDossierType(), dumpDossier(accountDossier), self._userID is None))

        self.as_responseDossierS(self._battlesType, {'achievementsList': packedList,
         'totalItemsList': totalItemsList,
         'battlesCount': targetData.getBattlesCount()}, '', '')
        return

    def _populate(self):
        super(ProfileAwards, self)._populate()
        initData = {'achievementFilter': {'dataProvider': [self.__packProviderItem(PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_ALL), self.__packProviderItem(PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_INPROCESS), self.__packProviderItem(PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_NONE)],
                               'selectedItem': self.__achievementsFilter}}
        self.as_setInitDataS(initData)

    def _onRareImageReceived(self, imgType, rareID, imageData):
        if imgType == IMAGE_TYPE.IT_67X71:
            stats = self._getNecessaryStats()
            achievement = stats.getAchievement(('rareAchievements', rareID))
            if achievement is not None:
                image_id = achievement.getSmallIcon()[6:]
                self.as_setRareAchievementDataS({'rareID': rareID,
                 'rareIconId': image_id})
        return

    def __packProviderItem(self, key):
        return {'label': i18n.makeString(key),
         'key': key}

    def setFilter(self, data):
        self.__achievementsFilter = data
        self.invokeUpdate()

    def _dispose(self):
        self._disposeRequester()
        super(ProfileAwards, self)._dispose()
