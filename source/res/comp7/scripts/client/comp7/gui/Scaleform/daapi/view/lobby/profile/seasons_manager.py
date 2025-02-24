# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/profile/seasons_manager.py
from comp7.gui.Scaleform.daapi.view.lobby.profile.comp7_profile_helper import getDropdownKeyBySeason, getSeasonName, COMP7_ARCHIVE_NAMES, COMP7_SEASON_NUMBERS, getDropdownKeyByArchiveName, isComp7Archive, getArchiveName
from comp7.gui.shared.gui_items.dossier.stats import getComp7DossierStats
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import BattleTypesDropDownItems
from gui.Scaleform.daapi.view.lobby.profile.seasons_manager import BaseSeasonManager
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7SeasonsManager(BaseSeasonManager):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(Comp7SeasonsManager, self).__init__()
        season = self._getLastActiveSeason()
        seasonNumber = season.getNumber() if season is not None else 1
        self._seasonKey = getDropdownKeyBySeason(seasonNumber)
        return

    def getStats(self, dossierStats):
        return getComp7DossierStats(dossierStats, archive=getArchiveName(self._seasonKey)) if isComp7Archive(self._seasonKey) else getComp7DossierStats(dossierStats, season=getSeasonName(self._seasonKey))

    def addSeasonsDropdown(self, targetVO):
        super(Comp7SeasonsManager, self).addSeasonsDropdown(targetVO)
        targetVO['dropdownSeasonLabel'] = backport.text(R.strings.profile.seasons.comp7_dropdown_label())

    def _makeSeasonsDropDown(self):
        itemsList = BattleTypesDropDownItems()
        for archive in COMP7_ARCHIVE_NAMES:
            itemsList.addByKey(getDropdownKeyByArchiveName(archive))

        for season in COMP7_SEASON_NUMBERS:
            itemsList.addByKey(getDropdownKeyBySeason(season))

        return itemsList

    def _showSeasonsDropDown(self):
        return len(self._makeSeasonsDropDown()) > 1

    def _getSeasonsProvider(self):
        return self.__comp7Controller

    @staticmethod
    def _addSeasonToDropDown(itemsList, seasonID, season):
        return itemsList.addByKey(getDropdownKeyBySeason(season.getNumber()))


def getComp7SeasonManagers():
    return {PROFILE_DROPDOWN_KEYS.COMP7: Comp7SeasonsManager()}
