# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicDamagePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicDamagePanelMeta(BaseDAAPIComponent):

    def as_setGeneralBonusS(self, value):
        return self.flashObject.as_setGeneralBonus(value) if self._isDAAPIInited() else None
