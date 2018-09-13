# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/DialogsManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class DialogsManagerMeta(DAAPIModule):

    def showSimpleI18nDialog(self, i18nKey, handlers):
        self._printOverrideError('showSimpleI18nDialog')
