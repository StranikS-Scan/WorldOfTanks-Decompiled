# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/accuracy_stacks_manager.py
import CGF
import SoundGroups
from cgf_components.vehicle_mechanics_components import AccuracyStacksRTPCComponent
from cgf_script.managers_registrator import autoregister, onProcessQuery, onAddedQuery, onRemovedQuery
from cgf_common.cgf_helpers import getParentGameObjectByComponent
from AccuracyStacksController import AccuracyStacksController

@autoregister(presentInAllWorlds=True)
class AccuracyStacksMechanicManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, AccuracyStacksRTPCComponent)
    def onAccuracyStacksRTPCAdded(self, gameObject, accuracyStacksComponent):
        accuracyStacksComponent.controllerGO = getParentGameObjectByComponent(gameObject, AccuracyStacksController)
        self.__setAccuracyStacksRTPC(accuracyStacksComponent)

    @onProcessQuery(AccuracyStacksRTPCComponent, period=0.2)
    def onAccuracyStacksRTPCProcess(self, accuracyStacksComponent):
        self.__setAccuracyStacksRTPC(accuracyStacksComponent)

    @onRemovedQuery(AccuracyStacksRTPCComponent)
    def onAccuracyStacksRTPCRemoved(self, accuracyStacksComponent):
        accuracyStacksComponent.controllerGO = None
        self.__setAccuracyStacksRTPC(accuracyStacksComponent)
        return

    @classmethod
    def __setAccuracyStacksRTPC(cls, accuracyStacksComponent):
        if accuracyStacksComponent.controllerGO is not None:
            progress = cls.__getAccuracyStacksProgress(accuracyStacksComponent.controllerGO)
        else:
            progress = 0.0
        if accuracyStacksComponent.progress != progress:
            SoundGroups.g_instance.setGlobalRTPC(accuracyStacksComponent.RTPCName, progress)
            accuracyStacksComponent.progress = progress
        return

    @classmethod
    def __getAccuracyStacksProgress(cls, controllerGO):
        accuracyStacksController = controllerGO.findComponentByType(AccuracyStacksController)
        if not controllerGO:
            return 0.0
        state = accuracyStacksController.getMechanicState()
        return 100.0 * (state.level + state.progress) / state.maxLevel
