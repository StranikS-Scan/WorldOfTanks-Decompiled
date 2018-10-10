# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/lobby/BaseContactView.py
from debug_utils import LOG_ERROR
from messenger.gui.Scaleform.meta.BaseContactViewMeta import BaseContactViewMeta

class BaseContactView(BaseContactViewMeta):

    def onCancel(self):
        pass

    def _populate(self):
        super(BaseContactView, self)._populate()
        self.as_setInitDataS(self._getInitDataObject())

    def _getInitDataObject(self):
        LOG_ERROR('this method have to be overridden!')
        return self._getDefaultInitData('', '', '', '', '')

    def _getDefaultInitData(self, mainLbl, btOkLbl, btnCancelLbl, btOkTooltip, btnCancelTooltip):
        return {'btOkLbl': btOkLbl,
         'btnCancelLbl': btnCancelLbl,
         'mainLbl': mainLbl,
         'btOkTooltip': btOkTooltip,
         'btnCancelTooltip': btnCancelTooltip}
