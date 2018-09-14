# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MoonSphereAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import RegularAchievement
from abstract.mixins import NoProgressBar
from gui.shared.gui_items.dossier.achievements import validators

class MoonSphereAchievement(RegularAchievement, NoProgressBar):

    def __init__(self, dossier, value=None):
        super(MoonSphereAchievement, self).__init__('moonSphere', _AB.SINGLE, dossier, value)

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return validators.alreadyAchieved(cls, name, block, dossier)
