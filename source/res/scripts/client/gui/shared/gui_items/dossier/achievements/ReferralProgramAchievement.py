# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReferralProgramAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import ClassProgressAchievement
from abstract import RegularAchievement
from gui.shared.gui_items.dossier.achievements import validators

class ReferralProgramSingleAchievement(RegularAchievement):

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.requiresReferralProgram() or validators.alreadyAchieved(cls, name, block, dossier)


class ReferralProgramClassAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        super(ReferralProgramClassAchievement, self).__init__('RP2018sergeant', _AB.TOTAL, dossier, value)

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.requiresReferralProgram() or validators.alreadyAchieved(cls, name, block, dossier)

    def getNextLevelInfo(self):
        return ('recruitsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'RP2018sergeant')
