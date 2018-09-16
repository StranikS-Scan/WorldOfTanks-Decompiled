# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileFormationsPageMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import ProfileSection

class ProfileFormationsPageMeta(ProfileSection):

    def showFort(self):
        self._printOverrideError('showFort')

    def createFort(self):
        self._printOverrideError('createFort')

    def onClanLinkNavigate(self, code):
        self._printOverrideError('onClanLinkNavigate')

    def as_setClanInfoS(self, clanInfo):
        return self.flashObject.as_setClanInfo(clanInfo) if self._isDAAPIInited() else None

    def as_setFortInfoS(self, fortInfo):
        return self.flashObject.as_setFortInfo(fortInfo) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, clanIcon):
        return self.flashObject.as_setClanEmblem(clanIcon) if self._isDAAPIInited() else None
