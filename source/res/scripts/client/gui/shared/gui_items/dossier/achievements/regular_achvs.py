# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/regular_achvs.py
from abstract import RegularAchievement
from abstract.mixins import NoProgressBar
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from gui.shared.gui_items.dossier.achievements import validators

class Achieved(RegularAchievement):
    __slots__ = ()

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.alreadyAchieved(cls, name, block, dossier)


class HonoredRankAchievement(RegularAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(HonoredRankAchievement, self).__init__('honoredRank', _AB.CLIENT, dossier, value)

    def getIcons(self):
        iconName = self.getIconName()
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


class MoonSphereAchievement(RegularAchievement, NoProgressBar):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MoonSphereAchievement, self).__init__('moonSphere', _AB.SINGLE, dossier, value)

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.alreadyAchieved(cls, name, block, dossier)


class ReferralProgramSingleAchievement(RegularAchievement):
    __slots__ = ()

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.requiresReferralProgram() or validators.alreadyAchieved(cls, name, block, dossier)
