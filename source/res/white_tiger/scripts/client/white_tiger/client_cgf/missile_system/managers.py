# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/missile_system/managers.py
import typing
import logging
import CGF
from Math import Vector3
from collections import deque
from functools import partial
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from GenericComponents import DynamicModelComponent
from Sound import Sound3DComponent
from Triggers import TimeTriggerComponent
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery
from events_core_client.events_core_cgf.missile_system.components import ClientMissileComponent, MissileReplicationDoneComponent
from events_core_common.events_core_cgf.missile_system.components import MissileDeploymentComponent
from events_core_common.events_core_cgf.missile_system.helpers import MISSILE_COMPONENTS, registerMissileManager
from white_tiger_common.wt_constants import WT_COMPONENT_CONSTANTS
from white_tiger.client_cgf.missile_system.components import WTMissileFlyEffectComponent
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_VIEW_ALIASES import WHITE_TIGER_BATTLE_VIEW_ALIASES
if typing.TYPE_CHECKING:
    from white_tiger.gui.battle_control.controllers.wt_ability_ctrl import WTAbilityController
_logger = logging.getLogger(__name__)

@registerMissileManager(CGF.DomainOption.DomainClient)
class WTMissileUIHelperManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _MAX_HEIGHT_COUNT = 6
    _ALTITUDE_OFFSET = 50
    _MAX_ALTITUDE = WT_COMPONENT_CONSTANTS.MISSILE_WIDGET_MAX_ALTITUDE
    _TRIGGER_TIMEOUT_COUNT = 1

    def __init__(self):
        super(WTMissileUIHelperManager, self).__init__()
        self.__abilityCtrl = self.__sessionProvider.dynamic.wtAbilityCtrl
        self._timeTriggerReactions = {}
        self.__heights = deque(maxlen=self._MAX_HEIGHT_COUNT)

    @onAddedQuery(*(MISSILE_COMPONENTS + (MissileReplicationDoneComponent, MissileDeploymentComponent)))
    def onDeploy(self, go, missile, transform, clientMissile, deployment):
        timeTriggerComponent = go.createComponent(TimeTriggerComponent, deployment.deployTime, self._TRIGGER_TIMEOUT_COUNT)
        wrappedCb = partial(self.__timeout, go)
        reactionID = timeTriggerComponent.addFireReaction(wrappedCb)
        self._timeTriggerReactions[go.id] = reactionID

    @onAddedQuery(*(MISSILE_COMPONENTS + (ClientMissileComponent, MissileDeploymentComponent)))
    def onStartedMissileUI(self, go, missile, transform, clientMissile, deployment):
        if self.__heights:
            self.__heights.clear()

    @onProcessQuery(period=0.05, *(MISSILE_COMPONENTS + (ClientMissileComponent,)))
    def onProcessUIDistance(self, go, missile, transform, clientMissileComponent):
        self.__abilityCtrl.update(WHITE_TIGER_BATTLE_VIEW_ALIASES.WT_MISSILE_WIDGET, distance=clientMissileComponent.distanceToTarget)

    @onProcessQuery(period=0.2, *(MISSILE_COMPONENTS + (ClientMissileComponent,) + (CGF.No(MissileDeploymentComponent),)))
    def onProcessUIAltitude(self, go, missile, transform, clientMissileComponent):
        self.__heights.append(transform.position.y + self._ALTITUDE_OFFSET)
        averageHeight = sum(self.__heights) / self._MAX_HEIGHT_COUNT
        if averageHeight > self._MAX_ALTITUDE:
            averageHeight = self._MAX_ALTITUDE
        self.__abilityCtrl.update(WHITE_TIGER_BATTLE_VIEW_ALIASES.WT_MISSILE_WIDGET, altitude=averageHeight)

    def __timeout(self, go, _):
        go.removeComponentByType(MissileDeploymentComponent)
        trigger = go.findComponentByType(TimeTriggerComponent)
        if not trigger:
            _logger.error('[Missile] Timeout after missile go is not valid')
            return
        trigger.removeFireReaction(self._timeTriggerReactions[go.id])
        go.removeComponent(trigger)
        self._timeTriggerReactions.pop(go.id)


@registerMissileManager(CGF.DomainOption.DomainClient)
class WTMissileEffectManager(CGF.ComponentManager):
    _MISSILE_NUMBER = 3
    _MISSILE_TRACER = 'ev_wt_ability_missile_tracer_0'

    def __init__(self):
        super(WTMissileEffectManager, self).__init__()
        self.__idx = 0

    @onAddedQuery(*(MISSILE_COMPONENTS + (WTMissileFlyEffectComponent,) + (CGF.No(MissileDeploymentComponent),)))
    def addProjection(self, go, missileComponent, __, flyEffectComponent):
        if not flyEffectComponent.effectPrefab:
            _logger.error('[Missile] flyEffectComponent has not a prefab path for effects')
            return
        CGF.loadGameObjectIntoHierarchy(flyEffectComponent.effectPrefab, go, Vector3(0, 0, 0))

    @onAddedQuery(*(MISSILE_COMPONENTS + (DynamicModelComponent,) + (CGF.No(MissileDeploymentComponent),)))
    def startFlight(self, go, missileComponent, __, model):
        model.setPartVisibleByName('projectile', True)
        go.createComponent(Sound3DComponent, go.name, self._MISSILE_TRACER + str(self.__idx % self._MISSILE_NUMBER + 1), True)
        self.__idx += 1
