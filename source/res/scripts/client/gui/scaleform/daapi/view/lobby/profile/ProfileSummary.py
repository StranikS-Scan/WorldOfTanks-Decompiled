# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSummary.py
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import StatisticTypes, ProfileUtils, getProfileCommonInfo
from gui.Scaleform.daapi.view.meta.ProfileSummaryMeta import ProfileSummaryMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from PlayerEvents import g_playerEvents
from helpers.i18n import makeString
from gui.Scaleform.locale.MENU import MENU

class ProfileSummary(ProfileSummaryMeta):

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileSummary, self)._sendAccountData(targetData, accountDossier)
        if self._statisticType == StatisticTypes.SEASON:
            data = self.statisticsController.getStatisticData(self._userID, self._battlesType)
            data['available'] = False if self._statisticType == StatisticTypes.SEASON else True
            data['unavailableMsg'] = makeHtmlString('html_templates:lobby/season_stats', 'unavailable', {'header': backport.text(R.strings.profile.profile.seasonRating.title()),
             'textFirst': backport.text(R.strings.profile.profile.seasonRating.desc.firstBlock(), seasonStatText=text_styles.highlightText(backport.text(R.strings.profile.profile.seasonRating.desc.seasonStatText()))),
             'textSecond': backport.text(R.strings.profile.profile.seasonRating.desc.secondBlock(), commonStatText=text_styles.highlightText(backport.text(R.strings.profile.profile.seasonRating.desc.commonStatText())))})
            data['seasonTime'] = ''
        else:
            data = ProfileUtils.packProfileDossierInfo(targetData, accountDossier, self._userID)
        self.as_responseDossierS(self._battlesType, data, '', '')

    def _populate(self):
        super(ProfileSummary, self)._populate()
        g_playerEvents.onDossiersResync += self.__dossierResyncHandler
        self.__updateUserInfo()
        self.as_setInitDataS(self._getInitData())
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

    def __dossierResyncHandler(self, *args):
        self.__updateUserInfo()

    def __updateUserInfo(self):
        dossier = self.itemsCache.items.getAccountDossier(self._userID)
        if dossier is not None:
            info = getProfileCommonInfo(self._userName, dossier.getDossierDescr())
            info['name'] = makeString(PROFILE.PROFILE_TITLE, info['name'])
            registrationDate = makeString(MENU.PROFILE_HEADER_REGISTRATIONDATETITLE) + ' ' + info['registrationDate']
            info['registrationDate'] = registrationDate
            if info['lastBattleDate'] is not None:
                info['lastBattleDate'] = makeString(MENU.PROFILE_HEADER_LASTBATTLEDATETITLE) + ' ' + info['lastBattleDate']
            else:
                info['lastBattleDate'] = ''
            self.as_setUserDataS(info)
        return

    def _getInitData(self):
        return {'commonScores': {'battles': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_TOTALBATTLES, ProfileUtils.getIconPath('battles40x32.png')),
                          'wins': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_TOTALWINS, ProfileUtils.getIconPath('wins40x32.png')),
                          'coolSigns': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_COOLSIGNS, ProfileUtils.getIconPath('markOfMastery40x32.png')),
                          'maxDestroyed': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_MAXDESTROYED, ProfileUtils.getIconPath('maxDestroyed40x32.png')),
                          'maxExperience': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_MAXEXPERIENCE, ProfileUtils.getIconPath('maxExp40x32.png')),
                          'avgExperience': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_AVGEXPERIENCE, ProfileUtils.getIconPath('avgExp40x32.png')),
                          'hits': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_HITS, ProfileUtils.getIconPath('hits40x32.png')),
                          'avgDamage': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_AVGDAMAGE, ProfileUtils.getIconPath('avgDamage40x32.png')),
                          'personalScore': self._formIconLabelInitObject(PROFILE.SECTION_SUMMARY_SCORES_PERSONALSCORE, ProfileUtils.getIconPath('battles40x32.png'))},
         'significantAwardsLabel': PROFILE.SECTION_SUMMARY_LABELS_SIGNIFICANTAWARDS,
         'significantAwardsErrorText': PROFILE.SECTION_SUMMARY_ERRORTEXT_SIGNIFICANTAWARDS}

    def _dispose(self):
        g_playerEvents.onDossiersResync -= self.__dossierResyncHandler
        self._disposeRequester()
        super(ProfileSummary, self)._dispose()

    def setSeasonStatisticsFilter(self, value):
        self._statisticType = StatisticTypes.ALL_TIME
        if value == StatisticTypes.SEASON:
            self._statisticType = StatisticTypes.SEASON
        self.invokeUpdate()
