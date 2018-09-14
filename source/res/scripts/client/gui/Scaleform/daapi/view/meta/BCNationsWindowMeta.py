# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCNationsWindowMeta.py
from gui.Scaleform.framework.entities.View import View

class BCNationsWindowMeta(View):

    def onNationSelected(self, nationId):
        self._printOverrideError('onNationSelected')

    def onNationShow(self, nationId):
        self._printOverrideError('onNationShow')

    def as_selectNationS(self, nationId, nationsList):
        """
        :param nationsList: Represented by Vector.<int> (AS)
        """
        return self.flashObject.as_selectNation(nationId, nationsList) if self._isDAAPIInited() else None
