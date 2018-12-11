# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/selectable_object.py


class ISelectableObject(object):

    def __init__(self):
        super(ISelectableObject, self).__init__()
        if not hasattr(self, 'selectionId'):
            self.selectionId = ''
        if not hasattr(self, 'mouseOverSoundName'):
            self.mouseOverSoundName = ''

    @property
    def enabled(self):
        raise NotImplementedError

    def setEnable(self, enabled):
        raise NotImplementedError

    def setHighlight(self, show):
        raise NotImplementedError

    def onMouseDown(self):
        pass

    def onMouseUp(self):
        pass

    def onMouseClick(self):
        pass
