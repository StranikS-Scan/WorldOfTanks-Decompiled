# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDeclarationOfWarWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortDeclarationOfWarWindowMeta(AbstractWindowView):

    def onDirectonChosen(self, directionUID):
        self._printOverrideError('onDirectonChosen')

    def onDirectionSelected(self):
        self._printOverrideError('onDirectionSelected')

    def as_setupHeaderS(self, title, description):
        return self.flashObject.as_setupHeader(title, description) if self._isDAAPIInited() else None

    def as_setupClansS(self, myClan, enemyClan):
        """
        :param myClan: Represented by ClanInfoVO (AS)
        :param enemyClan: Represented by ClanInfoVO (AS)
        """
        return self.flashObject.as_setupClans(myClan, enemyClan) if self._isDAAPIInited() else None

    def as_setDirectionsS(self, data):
        """
        :param data: Represented by Vector.<ConnectedDirectionsVO> (AS)
        """
        return self.flashObject.as_setDirections(data) if self._isDAAPIInited() else None

    def as_selectDirectionS(self, uid):
        return self.flashObject.as_selectDirection(uid) if self._isDAAPIInited() else None
