# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportBaseViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class CyberSportBaseViewMeta(DAAPIModule):

    def as_setPyAliasS(self, alias):
        if self._isDAAPIInited():
            return self.flashObject.as_setPyAlias(alias)

    def as_getPyAliasS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getPyAlias()
