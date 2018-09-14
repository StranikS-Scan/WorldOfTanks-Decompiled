# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileStatistics.py
from debug_utils import LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import getStatisticsVO
from gui.Scaleform.daapi.view.meta.ProfileStatisticsMeta import ProfileStatisticsMeta
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared.formatters import text_styles
from helpers import i18n
_FRAME_LABELS = {PROFILE_DROPDOWN_KEYS.ALL: 'random',
 PROFILE_DROPDOWN_KEYS.FALLOUT: 'fallout',
 PROFILE_DROPDOWN_KEYS.HISTORICAL: 'historical',
 PROFILE_DROPDOWN_KEYS.TEAM: 'team7x7',
 PROFILE_DROPDOWN_KEYS.STATICTEAM: 'team7x7',
 PROFILE_DROPDOWN_KEYS.CLAN: 'clan',
 PROFILE_DROPDOWN_KEYS.FORTIFICATIONS: 'fortifications',
 PROFILE_DROPDOWN_KEYS.STATICTEAM_SEASON: 'team7x7'}

def _packProviderType(mainType, addValue=None):
    return '%s/%s' % (mainType, str(addValue)) if addValue is not None else mainType


def _parseProviderType(value):
    return value.split('/')


class ProfileStatistics(ProfileStatisticsMeta):

    def __init__(self, *args):
        try:
            _, _, _, self.__ctx = args
        except Exception:
            LOG_ERROR('There is error while parsing profile stats page arguments', args)
            self.__ctx = {}

        super(ProfileStatistics, self).__init__(*args)

    def _populate(self):
        super(ProfileStatistics, self)._populate()
        self._setInitData()

    def _setInitData(self, accountDossier=None):
        dropDownProvider = [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.ALL), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FALLOUT)]
        if accountDossier is not None and accountDossier.getHistoricalStats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.HISTORICAL))
        dropDownProvider.extend((self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.TEAM), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.STATICTEAM), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.CLAN)))
        if g_lobbyContext.getServerSettings().isStrongholdsEnabled():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS))
        seasonItems = [self._dataProviderEntry(PROFILE_DROPDOWN_KEYS.STATICTEAM, PROFILE.PROFILE_SEASONSDROPDOWN_ALL)]
        seasonIndex = 0
        for idx, season in enumerate(seasonItems):
            if season['key'] == _packProviderType(self._battlesType, self._seasonID):
                seasonIndex = idx

        self.as_setInitDataS({'dropDownProvider': dropDownProvider,
         'seasonItems': seasonItems,
         'seasonIndex': seasonIndex,
         'seasonEnabled': False})
        return

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileStatistics, self)._sendAccountData(targetData, accountDossier)
        self._setInitData(accountDossier)
        vo = getStatisticsVO(battlesType=self._battlesType, targetData=targetData, accountDossier=accountDossier, isCurrentUser=self._userID is None)
        if self._battlesType in (PROFILE_DROPDOWN_KEYS.TEAM, PROFILE_DROPDOWN_KEYS.STATICTEAM, PROFILE_DROPDOWN_KEYS.STATICTEAM_SEASON):
            if self._battlesType in (PROFILE_DROPDOWN_KEYS.STATICTEAM, PROFILE_DROPDOWN_KEYS.STATICTEAM_SEASON):
                self._battlesType = PROFILE_DROPDOWN_KEYS.STATICTEAM
                vo['headerText'] = i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_STATICTEAM)
                vo['dropdownSeasonLabel'] = text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_SEASONFILTER)
                vo['showSeasonDropdown'] = True
            else:
                vo['showSeasonDropdown'] = False
        self.as_responseDossierS(self._battlesType, vo, _FRAME_LABELS[self._battlesType], '')
        return

    def _receiveFortDossier(self, accountDossier):
        return accountDossier.getFortSortiesStats()

    def setSeason(self, seasonId):
        self.setSeasonID(*_parseProviderType(seasonId))

    def _dispose(self):
        super(ProfileStatistics, self)._dispose()

    def onCompletedSeasonsInfoChanged(self):
        self._setInitData()
