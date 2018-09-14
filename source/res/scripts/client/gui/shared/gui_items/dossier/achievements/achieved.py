# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/Achieved.py
from abstract import RegularAchievement
from gui.shared.gui_items.dossier.achievements import validators

class Achieved(RegularAchievement):

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.alreadyAchieved(cls, name, block, dossier)
