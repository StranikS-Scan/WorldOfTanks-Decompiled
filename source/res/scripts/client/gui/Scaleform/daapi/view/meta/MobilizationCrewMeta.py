# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MobilizationCrewMeta.py
from gui.Scaleform.daapi.view.lobby.hangar.recruit_panel_base import RecruitPanelBase

class MobilizationCrewMeta(RecruitPanelBase):

    def as_setConvertAvailableS(self, isAvailable):
        return self.flashObject.as_setConvertAvailable(isAvailable) if self._isDAAPIInited() else None
