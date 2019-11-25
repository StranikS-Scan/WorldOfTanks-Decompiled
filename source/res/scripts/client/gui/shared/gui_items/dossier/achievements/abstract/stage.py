# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/stage.py
from gui.shared.gui_items.dossier.achievements.abstract.regular import RegularAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE

class StageAchievement(RegularAchievement):
    __slots__ = ()

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return cls.checkIsInDossier(block, name, dossier)

    def getType(self):
        return ACHIEVEMENT_TYPE.SINGLE

    def _getActualName(self):
        return '%s%d' % (self._name, self._value)
