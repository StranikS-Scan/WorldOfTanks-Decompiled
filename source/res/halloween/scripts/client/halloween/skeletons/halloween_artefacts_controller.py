# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/halloween_artefacts_controller.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from halloween.gui.game_control.halloween_artefacts_controller import Artefact

class IHalloweenArtefactsController(IGameController):
    onArtefactStatusUpdated = None
    onArtefactKeyUpdated = None
    onArtefactSettingsUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    @property
    def selectedArtefactID(self):
        raise NotImplementedError

    @selectedArtefactID.setter
    def selectedArtefactID(self, artefactID):
        raise NotImplementedError

    @property
    def needSelectNextSlide(self):
        raise NotImplementedError

    @needSelectNextSlide.setter
    def needSelectNextSlide(self, value):
        raise NotImplementedError

    def artefactsSorted(self):
        raise NotImplementedError

    def regularArtefacts(self):
        raise NotImplementedError

    def getFinalArtefact(self):
        raise NotImplementedError

    def getArtefact(self, artefactID):
        raise NotImplementedError

    def isArtefactOpened(self, artefactID):
        raise NotImplementedError

    def isArtefactReceived(self, artefactID):
        raise NotImplementedError

    def getArtefactKeyQuantity(self):
        raise NotImplementedError

    def getCurrentArtefactProgress(self):
        raise NotImplementedError

    def getAvailableArtefactProgress(self):
        raise NotImplementedError

    def getMaxArtefactsProgress(self):
        raise NotImplementedError

    def getArtefactsCount(self):
        raise NotImplementedError

    def getRareAttachmentsFromArtefact(self, artefactID):
        raise NotImplementedError

    def isArtefactHasTwitchConCertificate(self, artefactID):
        raise NotImplementedError

    def isExistUnreceivedTwitchConCertificate(self):
        raise NotImplementedError

    def getArtefactIDForAccessToVehicle(self, vehTypeCD):
        raise NotImplementedError

    def getLackOfKeysForArtefact(self, artefactID):
        raise NotImplementedError

    def getLackOfKeysForArtefacts(self):
        raise NotImplementedError

    def getQuest(self, questID):
        raise NotImplementedError

    def openArtefact(self, artefactID, isSkipQuest):
        raise NotImplementedError

    def getMainGiftVehicle(self):
        raise NotImplementedError

    def getMainGiftStyle(self):
        raise NotImplementedError

    def getOpenedArtefactToken(self, artefactID):
        raise NotImplementedError

    def geArtefactIDFromOpenToken(self, token):
        raise NotImplementedError

    def isFinalArtefact(self, artefect):
        raise NotImplementedError

    def getIndex(self, artefactID):
        raise NotImplementedError

    def isProgressCompleted(self):
        raise NotImplementedError

    def resetSelectedArtefactID(self):
        raise NotImplementedError

    def getArtefactIDByIndex(self, index):
        raise NotImplementedError
