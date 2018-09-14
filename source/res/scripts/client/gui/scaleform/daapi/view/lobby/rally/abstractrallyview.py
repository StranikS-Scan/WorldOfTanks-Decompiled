# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/AbstractRallyView.py
from gui.Scaleform.daapi.view.meta.AbstractRallyViewMeta import AbstractRallyViewMeta

class AbstractRallyView(AbstractRallyViewMeta):

    def __init__(self):
        super(AbstractRallyView, self).__init__()
        self.isMinimising = False

    def setData(self, itemID):
        pass
