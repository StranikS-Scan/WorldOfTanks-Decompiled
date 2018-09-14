# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/FalloutAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import RegularAchievement
from gui.shared.gui_items.dossier.achievements import validators

class FalloutAchievement(RegularAchievement):

    def __init__(self, dossier, value = None):
        RegularAchievement.__init__(self, 'fallout', _AB.SINGLE, dossier, value)

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.alreadyAchieved(cls, name, block, dossier)
