# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MarkI100Years.py
from abstract import ClassProgressAchievement, mixins
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class MarkI100Years(mixins.Quest, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        super(MarkI100Years, self).__init__('markI100Years', _AB.TOTAL, dossier, value)
