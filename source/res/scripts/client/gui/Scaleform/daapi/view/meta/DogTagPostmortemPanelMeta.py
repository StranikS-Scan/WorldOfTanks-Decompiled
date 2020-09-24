# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DogTagPostmortemPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel

class DogTagPostmortemPanelMeta(PostmortemPanel):

    def onDogTagKillerInPlaySound(self):
        self._printOverrideError('onDogTagKillerInPlaySound')

    def onDogTagKillerSlidePlaySound(self):
        self._printOverrideError('onDogTagKillerSlidePlaySound')

    def onDogTagKillerZoomOutPlaySound(self):
        self._printOverrideError('onDogTagKillerZoomOutPlaySound')

    def onVictimDogTagInPlaySound(self):
        self._printOverrideError('onVictimDogTagInPlaySound')

    def onVictimDogTagOutPlaySound(self):
        self._printOverrideError('onVictimDogTagOutPlaySound')

    def as_showKillerDogTagS(self, data):
        return self.flashObject.as_showKillerDogTag(data) if self._isDAAPIInited() else None

    def as_showVictimDogTagS(self, data):
        return self.flashObject.as_showVictimDogTag(data) if self._isDAAPIInited() else None
