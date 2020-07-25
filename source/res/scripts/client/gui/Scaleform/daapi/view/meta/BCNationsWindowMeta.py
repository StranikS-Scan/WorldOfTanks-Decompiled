# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCNationsWindowMeta.py
from tutorial.gui.Scaleform.pop_ups import TutorialDialog

class BCNationsWindowMeta(TutorialDialog):

    def onNationSelected(self, nationId):
        self._printOverrideError('onNationSelected')

    def onNationShow(self, nationId):
        self._printOverrideError('onNationShow')

    def as_selectNationS(self, selectedIndex, nationsList):
        return self.flashObject.as_selectNation(selectedIndex, nationsList) if self._isDAAPIInited() else None
