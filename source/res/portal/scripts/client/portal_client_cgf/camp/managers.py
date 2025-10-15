# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/camp/managers.py
import logging
from functools import partial
import BigWorld
import CGF
from GenericComponents import AnimatorComponent
from cgf_script.managers_registrator import onAddedQuery
from constants import IS_EDITOR
from portal_common_cgf.portal_helpers import registerPortalManager
if IS_EDITOR:
    from portal_common_cgf.camp.components import CampReplicableComponent
else:
    from CampReplicableComponent import CampReplicableComponent
_logger = logging.getLogger(__name__)

@registerPortalManager(CGF.DomainOption.DomainClient)
class CampManager(CGF.ComponentManager):
    __MODEL_GO_NAME = 'model'
    __EXPLOSION_ANIMATION = 'explosion'
    __LEVITATION_ANIMATION = 'levitation'

    def __init__(self):
        super(CampManager, self).__init__()
        self.__callbacks = {}
        CampReplicableComponent.onCaptured += self.__onCampCaptured

    def destroy(self):
        CampReplicableComponent.onCaptured -= self.__onCampCaptured
        for callback in self.__callbacks:
            BigWorld.cancelCallback(callback)

        self.__callbacks.clear()

    @onAddedQuery(CGF.GameObject, CampReplicableComponent)
    def onCampAdded(self, campGO, campComponent):
        if campComponent.isCaptured:
            self.__onCampCaptured(campGO, skipExplosion=True)

    def __onCampCaptured(self, campGO, skipExplosion=False):
        hm = CGF.HierarchyManager(self.spaceID)
        modelGO = None
        for child in hm.getChildren(campGO):
            if child.name == self.__MODEL_GO_NAME:
                modelGO = child
                break

        if not modelGO:
            _logger.error('Could not find a model for camp %s', campGO.name)
            return
        else:
            animator = modelGO.findComponentByType(AnimatorComponent)
            if animator:
                if skipExplosion:
                    animator.startLayerByName(self.__LEVITATION_ANIMATION)
                    return
                explosionDuration = animator.getDurationByName(self.__EXPLOSION_ANIMATION)
                animator.startLayerByName(self.__EXPLOSION_ANIMATION)
                wrapper = partial(self.__playLevitation, modelGO)
                callback = BigWorld.callback(explosionDuration, wrapper)
                self.__callbacks[modelGO.id] = callback
            return

    def __playLevitation(self, modelGO):
        self.__callbacks.pop(modelGO.id)
        if not modelGO.isValid():
            return
        animator = modelGO.findComponentByType(AnimatorComponent)
        if animator:
            animator.stop()
            animator.startLayerByName(self.__LEVITATION_ANIMATION)
