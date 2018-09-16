# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileAchievementSection.py
from gui.Scaleform.daapi.view.meta.ProfileAchievementSectionMeta import ProfileAchievementSectionMeta
from helpers import dependency
from skeletons.gui.shared.utils import IRaresCache

class ProfileAchievementSection(ProfileAchievementSectionMeta):
    rareAchievesCache = dependency.descriptor(IRaresCache)

    def __init__(self, *args):
        super(ProfileAchievementSection, self).__init__(*args)
        self.rareAchievesCache.onImageReceived += self._onRareImageReceived

    def _onRareImageReceived(self, imgType, rareID, imageData):
        pass

    def _disposeRequester(self):
        self.rareAchievesCache.onImageReceived -= self._onRareImageReceived
