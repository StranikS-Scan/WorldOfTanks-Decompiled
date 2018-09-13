# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportBaseView.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.CyberSportBaseViewMeta import CyberSportBaseViewMeta
__author__ = 'd_dichkovsky'

class CyberSportBaseView(CyberSportBaseViewMeta):

    def __init__(self):
        super(CyberSportBaseView, self).__init__()

    def canBeClosed(self, callback):
        callback(True)

    def setData(self, initialData):
        LOG_DEBUG('CyberSportBaseView.setItemId stub implementation. Passed id is:', initialData)
