# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/profile/comp7_profile_statistics.py
from comp7.gui.Scaleform.daapi.view.lobby.profile.comp7_profile_helper import getBattleHandlers
from comp7.gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import getComp7StatisticsVO
from comp7.gui.Scaleform.daapi.view.lobby.profile.seasons_manager import getComp7SeasonManagers
from gui.Scaleform.daapi.view.lobby.profile.ProfileStatistics import ProfileStatistics
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS

class Comp7ProfileStatistics(ProfileStatistics):

    def __init__(self, *args):
        super(Comp7ProfileStatistics, self).__init__(*args)
        self._battleTypeHandlers.update(getBattleHandlers())
        self._seasonsManagers.update(getComp7SeasonManagers())

    @classmethod
    def _makeBattleTypesDropDown(cls, accountDossier, forVehiclesPage=False):
        result = super(Comp7ProfileStatistics, cls)._makeBattleTypesDropDown(accountDossier, forVehiclesPage)
        result.addByKey(PROFILE_DROPDOWN_KEYS.COMP7)
        return result

    def _setStatisticsVO(self, targetData, accountDossier):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7:
            vo = getComp7StatisticsVO(self._battlesType, targetData, accountDossier, self._userID is None)
            self._seasonsManagers.addSeasonsDropdown(vo)
            self.as_responseDossierS(self._battlesType, vo, 'comp7', '')
        else:
            super(Comp7ProfileStatistics, self)._setStatisticsVO(targetData, accountDossier)
        return
