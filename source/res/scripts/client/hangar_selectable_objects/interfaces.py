# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_selectable_objects/interfaces.py


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

    def onMouseDown(self):
        pass

    def onMouseUp(self):
        pass

    def onMouseClick(self):
        pass


class ISelectableLogic(object):
    __slots__ = ()

    def init(self, callback=None):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def _onMouseEnter(self, entity):
        raise NotImplementedError

    def _onMouseExit(self, entity):
        raise NotImplementedError

    def _onMouseDown(self):
        raise NotImplementedError

    def _onMouseUp(self):
        raise NotImplementedError

    def _onNotifyCursorOver3dScene(self, isCursorOver3dScene):
        raise NotImplementedError

    def _filterEntity(self, entity):
        raise NotImplementedError


class ISelectableLogicCallback(object):

    def onHighlight3DEntity(self, entity):
        raise NotImplementedError

    def onFade3DEntity(self, entity):
        raise NotImplementedError
