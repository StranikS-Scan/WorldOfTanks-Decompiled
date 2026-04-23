# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/skeletons/ls_artefacts_controller.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_artefacts_controller import Artefact

class ILSArtefactsController(IGameController):
    onArtefactStatusUpdated = None
    onProgressPointsUpdated = None
    onArtefactSettingsUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    @property
    def selectedArtefactID(self):
        raise NotImplementedError

    @selectedArtefactID.setter
    def selectedArtefactID(self, artefactID):
        raise NotImplementedError

    def resetSelectedArtefactID(self):
        raise NotImplementedError

    def artefactsSorted(self):
        raise NotImplementedError

    def regularArtefacts(self):
        raise NotImplementedError

    def getFinalArtefact(self):
        raise NotImplementedError

    def getKingRewardArtefact(self):
        raise NotImplementedError

    def getRareAttachmentsFromArtefact(self, artefactID):
        raise NotImplementedError

    def getArtefact(self, artefactID):
        raise NotImplementedError

    def isArtefactOpened(self, artefactID):
        raise NotImplementedError

    def remainNotOpened(self, artefactID):
        raise NotImplementedError

    def isArtefactReceived(self, artefactID):
        raise NotImplementedError

    def getProgressPointsQuantity(self):
        raise NotImplementedError

    def getCurrentArtefactProgress(self):
        raise NotImplementedError

    def getAvailableArtefactProgress(self):
        raise NotImplementedError

    def getMaxArtefactsProgress(self):
        raise NotImplementedError

    def getArtefactsCount(self):
        raise NotImplementedError

    def getLackOfPointsForArtefact(self, artefactID):
        raise NotImplementedError

    def getLackOfPointsForArtefacts(self):
        raise NotImplementedError

    def getArtefactProgressPointsCost(self, artefactID):
        raise NotImplementedError

    def openArtefact(self, artefactID, isSkipQuest):
        raise NotImplementedError

    def isArtefactHasLootBoxGift(self, artefactID):
        raise NotImplementedError

    def isAnyArtefactsHasLootBoxGift(self):
        raise NotImplementedError

    def getMainGift(self):
        raise NotImplementedError

    def geArtefactIDFromOpenToken(self, token):
        raise NotImplementedError

    def isFinalArtefact(self, artefect):
        raise NotImplementedError

    def isKingRewardArtefact(self, artefect):
        raise NotImplementedError

    def getIndex(self, artefactID):
        raise NotImplementedError

    def isProgressCompleted(self):
        raise NotImplementedError

    def getArtefactIDByIndex(self, index):
        raise NotImplementedError

    def getLastUnopenedArtefactId(self):
        raise NotImplementedError
