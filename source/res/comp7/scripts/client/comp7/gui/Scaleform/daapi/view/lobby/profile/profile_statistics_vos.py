# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/profile/profile_statistics_vos.py
from comp7.gui.Scaleform.daapi.view.lobby.profile.profile_utils import COMP7_STATISTICS_LAYOUT
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils as PUtils
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import ProfileDictStatisticsVO, packAvgDmgLditItemData, getDetailedStatisticsData, formatChartsData, getVehStatsByTypes, getVehStatsByNation
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.impl import backport
from gui.impl.gen import R

class ProfileComp7StatisticsVO(ProfileDictStatisticsVO):

    def __init__(self, targetData, accountDossier, isCurrentUser):
        self.__headerKey = PROFILE_DROPDOWN_KEYS.COMP7
        super(ProfileComp7StatisticsVO, self).__init__(targetData, accountDossier, isCurrentUser)

    def _getHeaderText(self, data):
        return backport.text(R.strings.profile.section.statistics.headerText.dyn(self.__headerKey)())

    def _getHeaderData(self, data):
        targetData, _ = data
        avgPrestigePoints = PUtils.getValueOrUnavailable(targetData.getAvgPrestigePoints())
        return (PUtils.getTotalBattlesHeaderParam(targetData, PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
         PUtils.packLditItemData(self._formattedWinsEfficiency, PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS, 'wins40x32.png'),
         packAvgDmgLditItemData(self._avgDmg),
         PUtils.packLditItemData(backport.getIntegralFormat(avgPrestigePoints), PROFILE.SECTION_STATISTICS_SCORES_AVGPRESTIGEPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGPRESTIGEPOINTS, 'avgPrestigePoints40x32.png'))

    def _getDetailedData(self, data):
        targetData, _ = data
        stats = targetData.getBattlesStats()
        return (getDetailedStatisticsData(PROFILE.SECTION_STATISTICS_BODYBAR_LABEL_DETAILED, targetData, self._isCurrentUser, COMP7_STATISTICS_LAYOUT), formatChartsData((getVehStatsByTypes(stats),
          getVehStatsByNation(stats),
          tuple(),
          tuple(),
          tuple())))


def getComp7StatisticsVO(battlesType, targetData, accountDossier, isCurrentUser):
    return ProfileComp7StatisticsVO(targetData, accountDossier, isCurrentUser) if battlesType == PROFILE_DROPDOWN_KEYS.COMP7 else None
