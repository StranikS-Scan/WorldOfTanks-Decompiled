# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/sub_systems/pbh_sequence_handler.py
from __future__ import absolute_import
from future.utils import iteritems
import CGF
import logging
import typing
from collections import OrderedDict
from GenericComponents import Sequence
from cgf_modules.sequence_events import sequenceSubscribe
from constants import PREBATTLE_SEQUENCE_EVENT_NAMES
from gui.battle_control.avatar_getter import getSpaceID
from gui.battle_control.controllers.prebattle_highlights.pbh_helpers import getPbhPrefabGo, timeUntilEndOfPeriod
from gui.battle_control.controllers.prebattle_highlights.sub_systems.base_sub_system import BasePbhSubSystem
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import PrebattleEvent, PetSystemEvent
from pet_system_common.pet_constants import PetTrigger
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import Optional, Callable, Tuple
    from Event import Event
_logger = logging.getLogger(__name__)
EXCLUDED_LAYERS = (Sequence.TRANSITION_LAYER_NAME, 'default')
EMPTY_SEQUENCE_LAYER_VALUE = ('', 0)

class PbhSequenceHandler(BasePbhSubSystem):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, readyCallback, stopCallback, onStartPbhStageEvent):
        self.__stopCallback = stopCallback
        self.__onStartPbhStageEvent = onStartPbhStageEvent
        self.__sequenceLayer = None
        super(PbhSequenceHandler, self).__init__(readyCallback)
        return

    def subscribe(self):
        pass

    def unsubscribe(self):
        pass

    def isReady(self):
        _, sequenceCMP = self.getSequenceData()
        layerInfo = self.getSequenceLayerInfo()
        return sequenceCMP is not None and layerInfo is not None

    def prepareSequences(self, go, layer):
        sequences = CGF.findInHierarchyWithComponent(go, Sequence, includingRoot=True)
        for sequence in sequences:
            sequence.requestLayerChangeByName(layer, 0.0)

    def startFlow(self):
        if not self.isReady():
            return
        spaceID = getSpaceID()
        sequenceSubscribe(spaceID, PREBATTLE_SEQUENCE_EVENT_NAMES.ON_ANIMATION, self.__handleAnimationEvent)
        sequenceSubscribe(spaceID, PREBATTLE_SEQUENCE_EVENT_NAMES.ON_START_PBH_STAGE, self.__handleStartPbhStageEvent)
        sequenceSubscribe(spaceID, PREBATTLE_SEQUENCE_EVENT_NAMES.ON_PBH_ENDS, self.__handlePbhEndsEvent)
        sequenceSubscribe(spaceID, PREBATTLE_SEQUENCE_EVENT_NAMES.ON_PET_HIGHLIGHT_ANIM, self.__handlePbhPetHighlightAnim)
        layer, _ = self.__sequenceLayer
        go, sequenceCMP = self.getSequenceData()
        self.prepareSequences(go, layer)
        sequenceCMP.start()

    def stopFlow(self):
        pass

    def clear(self):
        self.__stopCallback = None
        self.__onStartPbhStageEvent = None
        self.__sequenceLayer = None
        super(PbhSequenceHandler, self).clear()
        return

    def getSequenceData(self):
        pbhPrefabGameObject = getPbhPrefabGo()
        if pbhPrefabGameObject is None:
            return (None, None)
        else:
            sequence = pbhPrefabGameObject.findWrite(Sequence)
            if sequence is None:
                _logger.error('[PBH] No Sequence component on PBH prefab')
                return (None, None)
            return (pbhPrefabGameObject, sequence)

    def getSequenceLayerInfo(self):
        sequenceLayers = {}
        _, sequenceCMP = self.getSequenceData()
        if sequenceCMP is None:
            return
        else:
            for layerName in sequenceCMP.layerNames:
                if layerName not in EXCLUDED_LAYERS:
                    sequenceLayers[layerName] = sequenceCMP.getDurationByLayerName(layerName)

            sortedSequenceLayers = OrderedDict(sorted(iteritems(sequenceLayers), key=lambda item: item[1], reverse=True))
            _logger.info('[PBH] Prefab sequence layers: %s', sortedSequenceLayers)
            currentTimeLeft = timeUntilEndOfPeriod()
            _logger.info('[PBH] Time left before current period ends: %f seconds', currentTimeLeft)
            minPrebattleTime = self.__lobbyContext.getServerSettings().pbhConfig.timeBeforeBattleMin
            _logger.info('[PBH] Minimum time for prebattle highlights showing: %f seconds', minPrebattleTime)
            if currentTimeLeft < minPrebattleTime:
                return EMPTY_SEQUENCE_LAYER_VALUE
            for layerName, layerDuration in iteritems(sortedSequenceLayers):
                if layerDuration is not None and currentTimeLeft >= layerDuration + minPrebattleTime:
                    self.__sequenceLayer = (layerName, layerDuration)
                    _logger.info('[PBH] Sequence name: %s, duration: %f seconds', layerName, layerDuration)
                    return (layerName, layerDuration)

            _logger.info('[PBH] Could not find suitable sequence layer')
            return EMPTY_SEQUENCE_LAYER_VALUE

    @staticmethod
    def __handleAnimationEvent():
        _logger.info('[PBH] PrebattleHighlightsController.PbhSequenceHandler __handleAnimationEvent')
        g_eventBus.handleEvent(PrebattleEvent(PrebattleEvent.ANIMATION_STARTED, ctx={}), scope=EVENT_BUS_SCOPE.BATTLE)

    def __handleStartPbhStageEvent(self):
        _logger.info('[PBH] PrebattleHighlightsController.PbhSequenceHandler __handleStartPbhStageEvent')
        if self.__onStartPbhStageEvent is not None:
            self.__onStartPbhStageEvent()
        return

    def __handlePbhEndsEvent(self):
        _logger.info('[PBH] PrebattleHighlightsController.PbhSequenceHandler __handlePbhEndsEvent')
        if self.__stopCallback is not None:
            self.__stopCallback()
        g_eventBus.handleEvent(PrebattleEvent(PrebattleEvent.ANIMATION_ENDED, ctx={}), scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def __handlePbhPetHighlightAnim(self):
        _logger.info('[PBH] PrebattleHighlightsController.PbhSequenceHandler __handlePbhPetHighlightAnim')
        g_eventBus.handleEvent(PetSystemEvent(PetSystemEvent.PET_SEQUENCE, ctx={'trigger': PetTrigger.PBH_HIGHLIGHT}), scope=EVENT_BUS_SCOPE.BATTLE)
