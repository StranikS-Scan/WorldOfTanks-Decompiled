# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WrapperViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class WrapperViewMeta(DAAPIModule):

    def onWindowClose(self):
        self._printOverrideError('onWindowClose')
