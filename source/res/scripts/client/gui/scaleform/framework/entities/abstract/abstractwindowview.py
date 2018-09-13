# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/AbstractWindowView.py
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class AbstractWindowView(WrapperViewMeta, WindowViewMeta):

    def __init__(self):
        super(AbstractWindowView, self).__init__()

    def onTryClosing(self):
        return True
