# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/AbstractWindowView.py
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta

class AbstractWindowView(WindowViewMeta):

    def __init__(self, ctx = None):
        super(AbstractWindowView, self).__init__()

    def _populate(self):
        super(AbstractWindowView, self)._populate()

    def onTryClosing(self):
        return True
