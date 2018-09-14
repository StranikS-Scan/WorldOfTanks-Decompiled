# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReferralReferrerIntroWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ReferralReferrerIntroWindowMeta(AbstractWindowView):

    def onClickApplyButton(self):
        self._printOverrideError('onClickApplyButton')

    def onClickHrefLink(self):
        self._printOverrideError('onClickHrefLink')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
