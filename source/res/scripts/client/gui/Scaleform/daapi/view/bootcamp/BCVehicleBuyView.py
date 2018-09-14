# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCVehicleBuyView.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.BCVehicleBuyViewMeta import BCVehicleBuyViewMeta
from Event import Event

class BCVehicleBuyView(BCVehicleBuyViewMeta):

    def __init__(self):
        super(BCVehicleBuyView, self).__init__()
        self.__academySelected = False
        self.onAcademyClicked = Event()

    def onAcademyClick(self):
        if not self.__academySelected:
            self.__academySelected = True
            self.onAcademyClicked()

    def _dispose(self):
        self.onAcademyClicked.clear()
        super(BCVehicleBuyView, self)._dispose()
