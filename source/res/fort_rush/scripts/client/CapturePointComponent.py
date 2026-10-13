# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/CapturePointComponent.py
from __future__ import absolute_import, division
import logging
from functools import wraps
import BigWorld
import CGF
from Event import Event, EventManager
from FortRushCapturePointStateMachineComponent import FortRushCapturePointStateMachineComponent
from cgf_script.registration import registerReplicableComponent, registerComponent
from constants import ARENA_PERIOD
from fort_rush.gui.shared.events import CapturePointEvent
from fort_rush_common.cgf.capture_point import FortRushCapturePointComponentDescr
from fort_rush_common.fort_rush_constants import CaptureStates
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from math_common import decimal_round
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

def capturablePointEventWrapper(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.scheduleUiRefresh()
        return func(self, *args, **kwargs)

    return wrapper


@registerComponent
class CapturePointMarkerAnchor(object):
    category = 'FortRush'
    editorTitle = 'Capture Point Marker Anchor'
    domain = CGF.Domain.ClientEditor


@registerReplicableComponent
class CapturePointComponent(FortRushCapturePointStateMachineComponent, FortRushCapturePointComponentDescr):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CapturePointComponent, self).__init__()
        _logger.debug('[FORT_RUSH] CapturePointComponent_%s.__init__', self.capturablePointName)
        self._isUiRefreshPending = False
        self._eventManager = EventManager()
        self.onOwnerTeamChanged = Event(self._eventManager)
        self.onCaptureStateChanged = Event(self._eventManager)
        self._isBattleFinished = self.sessionProvider.arenaVisitor.getArenaPeriod() == ARENA_PERIOD.AFTERBATTLE
        self._arenaSubscription = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if self._arenaSubscription is not None:
            self._arenaSubscription.onPeriodChange += self._onArenaPeriodChange
        else:
            _logger.warning('[FORT_RUSH] CapturePointComponent_%s: no arena subscription, battle end will not stop UI refreshes', self.capturablePointName)
        return

    def onDestroy(self):
        if self._arenaSubscription is not None:
            self._arenaSubscription.onPeriodChange -= self._onArenaPeriodChange
            self._arenaSubscription = None
        self._isUiRefreshPending = False
        self._eventManager.clear()
        super(CapturePointComponent, self).onDestroy()
        return

    def _onArenaPeriodChange(self, period, _periodEndTime, _periodLength, _periodAdditionalInfo):
        if period != ARENA_PERIOD.AFTERBATTLE:
            return
        _logger.debug('[FORT_RUSH] CapturePointComponent_%s: battle finished, stop UI refreshes', self.capturablePointName)
        self._isBattleFinished = True
        self._isUiRefreshPending = False

    def scheduleUiRefresh(self):
        if self._isBattleFinished:
            return
        if not self._isUiRefreshPending:
            self._isUiRefreshPending = True
            BigWorld.callback(0.095, makeCallbackWeak(self._sendEvent))

    @property
    def isNeutralizing(self):
        return False if not self.capturablePointOwnerTeam else self.state == CaptureStates.CAPTURING and self.invadingTeam != self.capturablePointOwnerTeam

    @capturablePointEventWrapper
    def set_totalInvaders(self, _):
        _logger.debug('[FORT_RUSH] CapturePointComponent totalInvaders: %s', self.totalInvaders)

    @capturablePointEventWrapper
    def set_capturablePointOwnerTeam(self, _):
        _logger.debug('[FORT_RUSH] CapturePointComponent capturablePointOwnerTeam: %s', self.capturablePointOwnerTeam)
        self.onOwnerTeamChanged(self.entity.entityGameObject, self)

    @capturablePointEventWrapper
    def set_invadingTeam(self, _):
        _logger.debug('[FORT_RUSH] CapturePointComponent invadingTeam: %s', self.invadingTeam)

    @capturablePointEventWrapper
    def set_currentPoints(self, _):
        _logger.debug('[FORT_RUSH] CapturePointComponent currentPoints: %s', self.currentPoints)

    @capturablePointEventWrapper
    def set_isContested(self, _):
        _logger.debug('[FORT_RUSH] CapturePointComponent isContested: %s', self.isContested)

    @capturablePointEventWrapper
    def set_state(self, prevState):
        _logger.debug('[FORT_RUSH] CapturePointComponent from state %s to state %s', CaptureStates(prevState), CaptureStates(self.state))
        self.onCaptureStateChanged(self.entity.entityGameObject, self, prevState)

    def calculatePercentage(self):
        return decimal_round(self.currentPoints / self.maxPoints, 2) if self.maxPoints != 0 else 0.0

    def sendEventImmediately(self):
        self._sendEvent()

    def _sendEvent(self):
        self._isUiRefreshPending = False
        entity = self.entity
        gameObject = entity.entityGameObject if entity is not None else None
        if gameObject is None:
            return
        else:
            eventType = CapturePointEvent.CAPTURABLE_POINT_UPDATE
            capturablePointName = self.capturablePointName
            invadersTeam = self.invadingTeam
            totalInvaders = self.totalInvaders
            ownersTeam = self.capturablePointOwnerTeam
            isContested = self.isContested
            isNeutralizing = self.isNeutralizing
            captureProgressPercent = self.calculatePercentage()
            captureState = self.state
            numberOfAttackers = self.numberOfAttackers
            uid = gameObject.id
            _logger.debug('[FORT_RUSH] CapturePointComponent._sendEvent: eventType=%s capturablePointName=%s uid=%s totalInvaders=%s invadersTeam=%s ownersTeam=%s isContested=%s captureProgressPercent=%s state=%s numberOfAttackers=%s isNeutralizing=%s', eventType, capturablePointName, uid, totalInvaders, invadersTeam, ownersTeam, isContested, captureProgressPercent, captureState, numberOfAttackers, isNeutralizing)
            g_eventBus.handleEvent(CapturePointEvent(eventType=eventType, capturablePointName=capturablePointName, invadersTeam=invadersTeam, totalInvaders=totalInvaders, ownersTeam=ownersTeam, isContested=isContested, captureProgressPercent=captureProgressPercent, state=captureState, numberOfAttackers=numberOfAttackers, isNeutralizing=isNeutralizing, uid=uid), scope=EVENT_BUS_SCOPE.BATTLE)
            return
