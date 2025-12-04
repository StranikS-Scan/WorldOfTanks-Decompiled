# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/oldman_manager.py
import CGF
import logging
from GenericComponents import AnimatorComponent, RemoveGoDelayedComponent
from Sound import Sound3DComponent
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery
from helpers import dependency
from new_year.skeletons.new_year import IOldManController
_logger = logging.getLogger(__name__)

@registerComponent
class OldManActivationComponent(object):
    domain = CGF.DomainOption.DomainClient


@registerComponent
class OldManActivationZoneComponent(object):
    domain = CGF.DomainOption.DomainClient
    prefabPath = ComponentProperty(type=CGFMetaTypes.STRING, annotations={'path': '*.prefab'}, editorName='OldMan prefab path')


class OldManManager(CGF.ComponentManager):
    __oldManCtrl = dependency.descriptor(IOldManController)

    @onAddedQuery(OldManActivationZoneComponent)
    def handleOldManActivationZoneAdded(self, _):
        self.__oldManCtrl.tryShowOldMan()

    @onAddedQuery(CGF.GameObject, OldManActivationComponent)
    def handleOldManAdded(self, go, _):
        self.__createSound3DComponent(go)
        animator = go.findComponentByType(AnimatorComponent)
        go.createComponent(RemoveGoDelayedComponent, animator.getDuration())

    def __createSound3DComponent(self, go):
        if go.findComponentByType(Sound3DComponent) is not None:
            _logger.error('Sound3DComponent already exists in OldManGO!')
            return
        else:
            soundEvent = self.__oldManCtrl.getSoundEvent()
            if not soundEvent:
                _logger.error('Sound event was not found for OldManGO.')
                return
            go.createComponent(Sound3DComponent, '', soundEvent, True)
            return
