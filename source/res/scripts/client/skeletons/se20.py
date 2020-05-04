# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/se20.py


class ICustomizableObjectsManager(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def addCustomizableEntity(self, entity):
        raise NotImplementedError

    def removeCustomizableEntity(self, entity):
        raise NotImplementedError

    def getCustomizableEntity(self, anchorName):
        raise NotImplementedError

    def addCameraAnchor(self, anchorName, anchor):
        raise NotImplementedError

    def removeCameraAnchor(self, anchorName):
        raise NotImplementedError

    def getCameraAnchor(self, anchorName):
        raise NotImplementedError

    def switchByAnchorName(self, anchorName):
        raise NotImplementedError

    def showFade(self, show):
        raise NotImplementedError

    def isCamActive(self):
        raise NotImplementedError
