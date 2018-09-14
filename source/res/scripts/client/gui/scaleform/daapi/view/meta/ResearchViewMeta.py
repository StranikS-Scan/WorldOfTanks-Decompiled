# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ResearchViewMeta.py
from gui.Scaleform.framework.entities.View import View

class ResearchViewMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def request4Unlock(self, itemCD, parentID, unlockIdx, xpCost):
        """
        :param itemCD:
        :param parentID:
        :param unlockIdx:
        :param xpCost:
        :return :
        """
        self._printOverrideError('request4Unlock')

    def request4Buy(self, itemCD):
        """
        :param itemCD:
        :return :
        """
        self._printOverrideError('request4Buy')

    def request4Info(self, itemCD, rootCD):
        """
        :param itemCD:
        :param rootCD:
        :return :
        """
        self._printOverrideError('request4Info')

    def showSystemMessage(self, typeString, message):
        """
        :param typeString:
        :param message:
        :return :
        """
        self._printOverrideError('showSystemMessage')

    def as_setNodesStatesS(self, primary, data):
        """
        :param primary:
        :param data:
        :return :
        """
        return self.flashObject.as_setNodesStates(primary, data) if self._isDAAPIInited() else None

    def as_setNext2UnlockS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setNext2Unlock(data) if self._isDAAPIInited() else None

    def as_setVehicleTypeXPS(self, xps):
        """
        :param xps:
        :return :
        """
        return self.flashObject.as_setVehicleTypeXP(xps) if self._isDAAPIInited() else None

    def as_setInventoryItemsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInventoryItems(data) if self._isDAAPIInited() else None

    def as_useXMLDumpingS(self):
        """
        :return :
        """
        return self.flashObject.as_useXMLDumping() if self._isDAAPIInited() else None
