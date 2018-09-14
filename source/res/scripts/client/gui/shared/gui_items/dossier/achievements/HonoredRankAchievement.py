# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/HonoredRankAchievement.py
from gui.shared.gui_items.dossier.achievements.abstract.RegularAchievement import RegularAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class HonoredRankAchievement(RegularAchievement):

    def __init__(self, dossier, value=None):
        super(HonoredRankAchievement, self).__init__('honoredRank', _AB.CLIENT, dossier, value)

    def getIcons(self):
        return {self.ICON_TYPE.IT_180X180: '../maps/icons/rankedBattles/ranks/114x160/rankVehMaster.png',
         self.ICON_TYPE.IT_67X71: '../maps/icons/rankedBattles/ranks/58x80/rankVehMaster.png'}

    @classmethod
    def checkIsInDossier(cls, block, name, dossier):
        return bool(cls.__getCount(dossier)) if dossier is not None else False

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return True

    def _readValue(self, dossier):
        return self.__getCount(dossier)

    @classmethod
    def __getCount(self, dossier):
        return dossier.getRankedStats().getTotalRanksCount()
