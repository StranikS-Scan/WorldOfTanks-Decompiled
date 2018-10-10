# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/HonoredRankAchievement.py
from gui.shared.gui_items.dossier.achievements.abstract.RegularAchievement import RegularAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class HonoredRankAchievement(RegularAchievement):

    def __init__(self, dossier, value=None):
        super(HonoredRankAchievement, self).__init__('honoredRank', _AB.CLIENT, dossier, value)

    def getIcons(self):
        iconName = self._getIconName()
        return {self.ICON_TYPE.IT_180X180: '%s/%s.png' % (self.ICON_PATH_180X180, iconName),
         self.ICON_TYPE.IT_67X71: '%s/%s.png' % (self.ICON_PATH_67X71, iconName)}

    @classmethod
    def checkIsInDossier(cls, block, name, dossier):
        return bool(cls.__getCount(dossier)) if dossier is not None else False

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return True

    def _readValue(self, dossier):
        return self.__getCount(dossier)

    @classmethod
    def __getCount(cls, dossier):
        return dossier.getRankedStats().getTotalRanksCount()
