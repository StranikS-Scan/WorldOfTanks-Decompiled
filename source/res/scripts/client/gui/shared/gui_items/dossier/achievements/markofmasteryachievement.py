# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MarkOfMasteryAchievement.py
from helpers import i18n
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from gui.shared.utils import CONST_CONTAINER

class MarkOfMasteryAchievement(ClassProgressAchievement):

    class MARK_OF_MASTERY(CONST_CONTAINER):
        MASTER = 4
        STEP_1 = 3
        STEP_2 = 2
        STEP_3 = 1

    def __init__(self, dossier, value = None):
        super(MarkOfMasteryAchievement, self).__init__('markOfMastery', _AB.TOTAL, dossier, value)

    def getUserName(self):
        i18nRank = i18n.makeString('#achievements:achievement/master%d' % (self._value or self.MIN_LVL))
        return super(ClassProgressAchievement, self).getUserName() % {'name': i18nRank}
