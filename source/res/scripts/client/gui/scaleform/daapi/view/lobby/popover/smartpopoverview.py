# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/popover/SmartPopOverView.py
from gui.Scaleform.daapi.view.meta.SmartPopOverViewMeta import SmartPopOverViewMeta
from gui.Scaleform.framework.entities.abstract.AbstractPopOverView import AbstractPopOverView

class SmartPopOverView(SmartPopOverViewMeta, AbstractPopOverView):

    def __init__(self):
        super(SmartPopOverView, self).__init__()
        self.__keyPointX = None
        self.__keyPointY = None
        return

    def _setKeyPoint(self, inX, inY):
        self.__keyPointX = inX
        self.__keyPointY = inY

    def _populate(self):
        super(SmartPopOverView, self)._populate()
        if self.__keyPointX is not None and self.__keyPointY is not None:
            self.as_setPositionKeyPointS(self.__keyPointX, self.__keyPointY)
        return
