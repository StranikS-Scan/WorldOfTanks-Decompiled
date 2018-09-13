# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileAchievementSection.py
from gui.shared import g_itemsCache
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection
from gui.Scaleform.daapi.view.meta.ProfileAchievementSectionMeta import ProfileAchievementSectionMeta
from gui.shared.utils.RareAchievementsCache import g_rareAchievesCache, IMAGE_TYPE

class ProfileAchievementSection(ProfileSection, ProfileAchievementSectionMeta):

    def __init__(self, *args):
        ProfileAchievementSectionMeta.__init__(self)
        ProfileSection.__init__(self, *args)
        g_rareAchievesCache.onTextReceived += self._onRareTextReceived
        g_rareAchievesCache.onImageReceived += self._onRareImageReceived

    def request(self, data):
        dossier = g_itemsCache.items.getAccountDossier(data)
        if dossier is not None:
            g_rareAchievesCache.request(dossier.getBlock('rareAchievements'))
        return

    def _onRareTextReceived(self, *args):
        self.invokeUpdate()

    def _onRareImageReceived(self, imgType, rareID, imageData):
        if imgType == IMAGE_TYPE.IT_67X71:
            self.invokeUpdate()

    def _disposeRequester(self):
        g_rareAchievesCache.onImageReceived -= self._onRareImageReceived
        g_rareAchievesCache.onTextReceived -= self._onRareTextReceived
