# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSummary.py
import WWISE
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils, getProfileCommonInfo
from gui.Scaleform.daapi.view.meta.ProfileSummaryMeta import ProfileSummaryMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from PlayerEvents import g_playerEvents
from helpers.i18n import makeString
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items.dossier import dumpDossier
from skeletons.gui.shared import IItemsCache
from gui.battle_control.dog_tag_composer import layoutComposer as dogTagComposer
from skeletons.gui.web import IWebController

class ProfileSummary(ProfileSummaryMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    _webCtrl = dependency.descriptor(IWebController)

    def __init__(self, *args):
        super(ProfileSummary, self).__init__(*args)
        self._isDTFlameEnabled = False

    def setActive(self, value):
        super(ProfileSummary, self).setActive(value)
        self._triggerDogTagFlameSound(value)

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileSummary, self)._sendAccountData(targetData, accountDossier)
        outcome = ProfileUtils.packProfileDossierInfo(targetData, accountDossier)
        outcome['avgDamage'] = ProfileUtils.getValueOrUnavailable(targetData.getAvgDamage())
        outcome['maxDestroyed'] = targetData.getMaxFrags()
        vehicle = self.itemsCache.items.getItemByCD(targetData.getMaxFragsVehicle())
        outcome['maxDestroyedByVehicle'] = vehicle.shortUserName if vehicle is not None else ''
        outcome['globalRating'] = self.getGlobalRating(self._databaseID)
        totalStats = accountDossier.getTotalStats()
        outcome['significantAchievements'] = AchievementsUtils.packAchievementList(totalStats.getSignificantAchievements(), accountDossier.getDossierType(), dumpDossier(accountDossier), self._userID is None, False)
        outcome['nearestAchievements'] = AchievementsUtils.packAchievementList(totalStats.getNearestAchievements(), accountDossier.getDossierType(), dumpDossier(accountDossier), self._userID is None, True)
        self.as_responseDossierS(self._battlesType, outcome, '', '')
        return

    def _populate(self):
        super(ProfileSummary, self)._populate()
        g_playerEvents.onDossiersResync += self.__dossierResyncHandler
        self.__updateUserInfo()
        self.as_setInitDataS(self._getInitData())

    def __dossierResyncHandler(self, *args):
        self.__updateUserInfo()

    def __updateUserInfo(self):
        dossier = self.itemsCache.items.getAccountDossier(self._userID)
        if dossier is not None:
            info = getProfileCommonInfo(self._userName, dossier.getDossierDescr())
            info['name'] = makeString(PROFILE.PROFILE_TITLE, info['name'])
            info['userID'] = str(self._userID)
            registrationDate = makeString(MENU.PROFILE_HEADER_REGISTRATIONDATETITLE) + ' ' + info['registrationDate']
            info['registrationDate'] = registrationDate
            if info['lastBattleDate'] is not None:
                info['lastBattleDate'] = makeString(MENU.PROFILE_HEADER_LASTBATTLEDATETITLE) + ' ' + info['lastBattleDate']
            else:
                info['lastBattleDate'] = ''
            dogTag = self.itemsCache.items.getDogTag(self._userID)
            clanProfile = self._webCtrl.getAccountProfile()
            self._addDogTagInfo(info, dogTag, self._userName, clanProfile)
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
        self._triggerDogTagFlameSound(False)
        self._disposeRequester()
        super(ProfileSummary, self)._dispose()

    def _addDogTagInfo(self, info, dogTag, playerName, clanProfile):
        if not dogTag:
            return
        dogTag['playerName'] = playerName
        dogTag['clanTag'] = clanProfile.getClanAbbrev()
        info['dogTag'] = dogTagComposer.getModelFromDict(dogTag)
        if info['dogTag']['isEngravingMaxLevel']:
            self._isDTFlameEnabled = True
            self._triggerDogTagFlameSound(True)

    def _triggerDogTagFlameSound(self, active):
        if not self._isDTFlameEnabled:
            return
        if active:
            WWISE.WW_eventGlobal(backport.sound(R.sounds.dt_flame_start()))
        else:
            WWISE.WW_eventGlobal(backport.sound(R.sounds.dt_flame_stop()))
