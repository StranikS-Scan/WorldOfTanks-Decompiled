# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/FreeXPInfoWindow.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FreeXPInfoWindowMeta import FreeXPInfoWindowMeta
from gui.Scaleform.framework import AppRef
__author__ = 'd_savitski'

class FreeXPInfoWindow(View, FreeXPInfoWindowMeta, AppRef, AbstractWindowView):

    def __init__(self, meta, handler):
        super(FreeXPInfoWindow, self).__init__()
        self.meta = meta
        self.handler = handler

    def _populate(self):
        super(FreeXPInfoWindow, self)._populate()
        self.as_setTitleS(self.meta.getTitle())
        self.as_setSubmitLabelS(self.meta.getSubmitLbl())
        self.as_setTextS(self.meta.getTextInfo())

    def onWindowClose(self):
        self.handler(True)
        self.destroy()

    def onSubmitButton(self):
        self.onWindowClose()

    def onCancelButton(self):
        self.onWindowClose()

    def _dispose(self):
        super(FreeXPInfoWindow, self)._dispose()
        self.handler = None
        return
