# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileAwards.py
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import StatisticTypes
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

    def setFilter(self, data):
        self.__achievementsFilter = data
        self.invokeUpdate()

    @staticmethod
    def _getTotalStatsBlock(dossier):
        return dossier.getTotalStats()

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileAwards, self)._sendAccountData(targetData, accountDossier)
        achievements = targetData.getAchievements(showHidden=False)
        totalItemsList = []
        for block in achievements:
            totalItemsList.append(len(block))

        if self.__achievementsFilter == PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_INPROCESS:
            achievements = targetData.getAchievements(isInDossier=True, showHidden=False)
        elif self.__achievementsFilter == PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_NONE:
            achievements = targetData.getAchievements(isInDossier=False, showHidden=False)
        packedList = []
        for achievementBlockList in achievements:
            packedList.append(AchievementsUtils.packAchievementList(achievementBlockList, accountDossier.getDossierType(), dumpDossier(accountDossier), self._userID is None))

        self.as_responseDossierS(self._battlesType, {'achievementsList': packedList,
         'totalItemsList': totalItemsList,
         'battlesCount': targetData.getBattlesCount(),
         'available': False if self._statisticType == StatisticTypes.SEASON else True,
         'unavailableMsg': makeHtmlString('html_templates:lobby/season_stats', 'unavailable', {'header': backport.text(R.strings.profile.profile.seasonRating.title()),
                            'textFirst': backport.text(R.strings.profile.profile.seasonRating.desc.firstBlock(), seasonStatText=text_styles.highlightText(backport.text(R.strings.profile.profile.seasonRating.desc.seasonStatText()))),
                            'textSecond': backport.text(R.strings.profile.profile.seasonRating.desc.secondBlock(), commonStatText=text_styles.highlightText(backport.text(R.strings.profile.profile.seasonRating.desc.commonStatText())))})}, '', '')
        return

    def _populate(self):
        super(ProfileAwards, self)._populate()
        initData = {'achievementFilter': {'dataProvider': [self.__packProviderItem(PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_ALL), self.__packProviderItem(PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_INPROCESS), self.__packProviderItem(PROFILE.SECTION_AWARDS_DROPDOWN_LABELS_NONE)],
                               'selectedItem': self.__achievementsFilter}}
        self.as_setInitDataS(initData)
        self.as_setTabsDataS([{'id': 'all',
          'label': backport.text(R.strings.profile.profile.tabs.title.allTime()),
          'linkage': 'RegularItemsTabViewUI',
          'selected': True,
          'enabled': True,
          'tooltip': backport.text(R.strings.profile.profile.tabs.tooltip.forAllTime())}, {'id': 'season',
          'label': backport.text(R.strings.profile.profile.tabs.title.season()),
          'linkage': 'RegularItemsTabViewUI',
          'selected': False,
          'enabled': True,
          'tooltip': backport.text(R.strings.profile.profile.tabs.tooltip.forTime(), time='--')}])

    def setSeasonStatisticsFilter(self, value):
        self._statisticType = StatisticTypes.ALL_TIME
        if value == StatisticTypes.SEASON:
            self._statisticType = StatisticTypes.SEASON
        self.invokeUpdate()

    def _onRareImageReceived(self, imgType, rareID, imageData):
        if imgType == IMAGE_TYPE.IT_67X71:
            stats = self._getNecessaryStats()
            achievement = stats.getAchievement(('rareAchievements', rareID))
            if achievement is not None:
                image_id = achievement.getSmallIcon()[6:]
                self.as_setRareAchievementDataS(rareID, image_id)
        return

    def _dispose(self):
        self._disposeRequester()
        super(ProfileAwards, self)._dispose()

    @staticmethod
    def __packProviderItem(key):
        return {'label': i18n.makeString(key),
         'key': key}
