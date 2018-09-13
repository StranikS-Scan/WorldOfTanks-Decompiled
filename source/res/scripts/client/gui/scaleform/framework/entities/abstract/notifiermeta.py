# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/NotifierMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class NotifierMeta(DAAPIModule):

    def showDialog(self, kind, title, text, buttons, handlers):
        self._printOverrideError('showDialog')

    def showI18nDialog(self, kind, i18nKey, handlers):
        self._printOverrideError('showI18nDialog')
