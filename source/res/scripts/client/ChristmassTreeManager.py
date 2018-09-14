# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ChristmassTreeManager.py
import Event
from ClientSelectableCameraObject import ClientSelectableCameraObject, CameraMovementStates
from AnimatedGiftBox import AnimatedGiftBox
from debug_utils import LOG_ERROR
TREE = 0
GIFT = 1
TANK = 2

class _ChristmassTreeManager(object):

    @property
    def tree(self):
        return self.__parts[TREE]

    @property
    def giftBox(self):
        return self.__parts[GIFT]

    @property
    def tank(self):
        return self.__parts[TANK]

    def __init__(self):
        super(_ChristmassTreeManager, self).__init__()
        self.__parts = 3 * [None]
        self.__onClickCallbacks = None
        self.onTreeLoaded = Event.Event()
        self.onChestLoaded = Event.Event()
        return

    def setOnclickCallback(self, callbacks):
        self.__onClickCallbacks = callbacks
        id = 0
        for part in self.__parts:
            if part is not None:
                part.setOnClickCallback(callbacks[id])
            id += 1

        return

    def clearOnclickCallback(self):
        for part in self.__parts:
            if part is not None:
                part.setOnClickCallback(None)

        self.__onClickCallbacks = None
        return

    def setPart(self, part, id):
        self.__parts[id] = part
        if self.__onClickCallbacks is not None:
            part.setOnClickCallback(self.__onClickCallbacks[id])
        if id == TREE:
            self.onTreeLoaded()
        elif id == GIFT:
            self.onChestLoaded()
        return

    def removePart(self, id):
        self.__parts[id] = None
        return


g_christMassManager = _ChristmassTreeManager()
_SLOT_IDS = range(1, 17)
_TANK_SLOT_ID = 13

def idToHardpoint(slotID):
    if slotID >= 1 and slotID < _TANK_SLOT_ID:
        return 'HP_mount_%02d' % slotID
    if slotID >= _TANK_SLOT_ID and slotID <= 17:
        return 'HP_module%d' % (slotID - _TANK_SLOT_ID)
    LOG_ERROR('Wrong slot ID', slotID)


def hangToy(modelName, HPname=None):
    if g_christMassManager.tree is not None:
        g_christMassManager.tree.hangToy(modelName, HPname)
    return


def hangToyByID(toyId, slotID=None, isLeft=False):
    if slotID is None:
        if g_christMassManager.tank is not None:
            g_christMassManager.tank.applyTexture(toyId)
    elif slotID < _TANK_SLOT_ID:
        if g_christMassManager.tree is not None:
            g_christMassManager.tree.hangToyByID(toyId, idToHardpoint(slotID), isLeft)
    elif g_christMassManager.tank is not None:
        g_christMassManager.tank.hangToyByID(toyId, idToHardpoint(slotID))
    return


def removeToy(slotID=None):
    if slotID is None:
        if g_christMassManager.tank is not None:
            g_christMassManager.tank.removeTexture()
    elif slotID < _TANK_SLOT_ID:
        if g_christMassManager.tree is not None:
            g_christMassManager.tree.removeToy(idToHardpoint(slotID))
    elif g_christMassManager.tank is not None:
        g_christMassManager.tank.removeToy(idToHardpoint(slotID))
    return


def hangToysDebug():
    if g_christMassManager.tree is not None:
        g_christMassManager.tree.defaultSetup()
    return


def switchCameraToTree(callback=None):
    ClientSelectableCameraObject.switchCamera(g_christMassManager.tree, callback)


def switchCameraToTank(callback=None):
    ClientSelectableCameraObject.switchCamera(g_christMassManager.tank.parent, callback)


def isChristmasView():
    for cameraObject in ClientSelectableCameraObject.allCameraObjects:
        if cameraObject.state == CameraMovementStates.ON_OBJECT:
            if cameraObject is g_christMassManager.tank.parent or cameraObject is g_christMassManager.tree:
                return True
            return False

    return False


def switchCameraToHangar(callback=None):
    ClientSelectableCameraObject.switchCamera(None, callback)
    return


def switchCameraToEntity(entity):
    if isTankEntity(entity) or isTreeEntity(entity):
        ClientSelectableCameraObject.switchCamera(entity)


def isTreeEntity(entity):
    return entity is g_christMassManager.tree


def isTankEntity(entity):
    return entity is g_christMassManager.tank.parent


def highlightEntity(entity, highlighted):
    if entity is g_christMassManager.tank.parent or entity is g_christMassManager.tree:
        entity.highlight(highlighted)


def switchCameraToChest(callback=None):
    if g_christMassManager.giftBox is not None:
        ClientSelectableCameraObject.switchCamera(g_christMassManager.giftBox, callback)
    return


def playReceiveChestAnimation(callback=None):
    if g_christMassManager.giftBox is not None:
        g_christMassManager.giftBox.setState(AnimatedGiftBox.BoxState.APPEARANCE, callback)
    return


def playChestWaitBonusAnimation():
    if g_christMassManager.giftBox is not None:
        g_christMassManager.giftBox.setState(AnimatedGiftBox.BoxState.WAITING_FOR_OPEN_RESPONSE)
    return


def playExploseChestAnimation(callback=None):
    if g_christMassManager.giftBox is not None:
        g_christMassManager.giftBox.setState(AnimatedGiftBox.BoxState.OPENING, callback)
    return


def addChestToScene():
    if g_christMassManager.giftBox is not None:
        g_christMassManager.giftBox.setState(AnimatedGiftBox.BoxState.ON_SCENE)
    return


def removeChestFromScene():
    if g_christMassManager.giftBox is not None:
        g_christMassManager.giftBox.setState(AnimatedGiftBox.BoxState.HIDDEN)
    return
