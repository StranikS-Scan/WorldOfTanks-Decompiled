# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/kamikaze_effect.py
from functools import partial
import logging
import BigWorld
import Svarog
import AnimationSequence
from helpers import dependency
from battleground import getKamikazeEquipmentDescr
from battleground.components import SequenceComponent, AvatarRelatedComponent
from helpers.CallbackDelayer import CallbackDelayer
from items.battle_royale import isSpawnedBot
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
_logger = logging.getLogger(__name__)

class KamikazeActivationEffect(AvatarRelatedComponent, CallbackDelayer):

    def __init__(self, componentSystem):
        super(KamikazeActivationEffect, self).__init__(componentSystem)
        CallbackDelayer.__init__(self)

    def deactivate(self):
        super(KamikazeActivationEffect, self).deactivate()
        playerAvatar = BigWorld.player()
        if hasattr(playerAvatar, 'onVehicleEnterWorld'):
            playerAvatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        CallbackDelayer.destroy(self)

    def _initialize(self):
        super(KamikazeActivationEffect, self)._initialize()
        playerAvatar = BigWorld.player()
        playerAvatar.onVehicleEnterWorld += self.__onVehicleEnterWorld

    def __onVehicleEnterWorld(self, vehicle):
        if isSpawnedBot(vehicle.typeDescriptor.type.tags):
            highlightDelay = getKamikazeEquipmentDescr().clientVisuals.highlightDelay
            if highlightDelay >= 0.0:
                self.delayCallback(highlightDelay, self.__showEffect, vehicle.id)

    def __showEffect(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle:
            spaceID = BigWorld.player().spaceID
            effectCmp = Svarog.GameObject(spaceID)
            effectDescr = self.__getConfig()

            def onResourceLoaded(effectP, resourceRefs):
                if effectP in resourceRefs.failedIDs:
                    _logger.warning('Resource loading failed %s', effectP)
                    return
                sequenceComponent = effectCmp.createComponent(SequenceComponent, resourceRefs[effectP])
                sequenceComponent.bindToCompound(vehicle.model)
                sequenceComponent.start()
                _logger.info('Kamikaze Animation Started!')
                effectCmp.activate()
                vehicle.appearance.addTempGameObject(effectCmp, 'kamikaze')

            effectPath = effectDescr.path
            BigWorld.loadResourceListBG((AnimationSequence.Loader(effectPath, spaceID),), partial(onResourceLoaded, effectPath))

    def __getConfig(self):
        dynObjCache = dependency.instance(IBattleDynamicObjectsCache)
        config = dynObjCache.getConfig(BigWorld.player().arenaGuiType)
        return config.getKamikazeActivatedEffect().effectDescr
