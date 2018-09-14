# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDeclarationOfWarWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortDeclarationOfWarWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onDirectonChosen(self, directionUID):
        """
        :param directionUID:
        :return :
        """
        self._printOverrideError('onDirectonChosen')

    def onDirectionSelected(self):
        """
        :return :
        """
        self._printOverrideError('onDirectionSelected')

    def as_setupHeaderS(self, title, description):
        """
        :param title:
        :param description:
        :return :
        """
        return self.flashObject.as_setupHeader(title, description) if self._isDAAPIInited() else None

    def as_setupClansS(self, myClan, enemyClan):
        """
        :param myClan:
        :param enemyClan:
        :return :
        """
        return self.flashObject.as_setupClans(myClan, enemyClan) if self._isDAAPIInited() else None

    def as_setDirectionsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setDirections(data) if self._isDAAPIInited() else None

    def as_selectDirectionS(self, uid):
        """
        :param uid:
        :return :
        """
        return self.flashObject.as_selectDirection(uid) if self._isDAAPIInited() else None
