# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/GuiItemsManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class GuiItemsManagerMeta(BaseDAAPIModule):

    def _getItemAttribute(self, itemTypeIdx, id, attrName):
        self._printOverrideError('_getItemAttribute')

    def _callItemMethod(self, itemTypeIdx, id, methodName, kargs):
        self._printOverrideError('_callItemMethod')
