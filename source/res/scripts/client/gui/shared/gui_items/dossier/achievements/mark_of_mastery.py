# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/mark_of_mastery.py
from helpers import i18n
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from shared_utils import CONST_CONTAINER
MASTERY_IS_NOT_ACHIEVED = 0

def isMarkOfMasteryAchieved(markOfMasterVal):
    return markOfMasterVal > MASTERY_IS_NOT_ACHIEVED


class MarkOfMasteryAchievement(ClassProgressAchievement):
    __slots__ = ('__prevMarkOfMastery', '__compDescr')

    class MARK_OF_MASTERY(CONST_CONTAINER):
        MASTER = 4
        STEP_1 = 3
        STEP_2 = 2
        STEP_3 = 1

    def __init__(self, dossier, value=None):
        super(MarkOfMasteryAchievement, self).__init__('markOfMastery', _AB.TOTAL, dossier, value)
        self.__prevMarkOfMastery = self.MIN_LVL
        self.__compDescr = None
        return

    def getMarkOfMastery(self):
        return self._value

    def getPrevMarkOfMastery(self):
        return self.__prevMarkOfMastery

    def setPrevMarkOfMastery(self, prevMarkOfMastery):
        self.__prevMarkOfMastery = prevMarkOfMastery

    def getCompDescr(self):
        return self.__compDescr

    def setCompDescr(self, compDescr):
        self.__compDescr = compDescr

    def _getUserNameCtx(self):
        return {'name': i18n.makeString('#achievements:achievement/master%d' % (self._value or self.MIN_LVL))}

    def _getIconName(self):
        return 'markOfMastery%drecord' % (self._value or self.MIN_LVL) if self.__prevMarkOfMastery < self._value else 'markOfMastery%d' % (self._value or self.MIN_LVL)
