# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/DialogsManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class DialogsManagerMeta(BaseDAAPIModule):

    def showSimpleI18nDialog(self, i18nKey, handlers):
        self._printOverrideError('showSimpleI18nDialog')
