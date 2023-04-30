# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/scenario/timed_activation.py
import CGF
import logging
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerReplicableComponent, registerComponent
_logger = logging.getLogger(__name__)

@registerComponent
class TimedActivation(object):
    category = 'Scenarios'
    editorTitle = 'TimedActivation'
    domain = CGF.DomainOption.DomainAll
    activationTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='ActivationTime', value=0.0)
    activationDuration = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='ActivationDuration', value=-1.0)
    autoRemove = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='AutoRemove', value=False)
    detach = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Detach', value=False)
    activateAnimations = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='SyncAnimations', value=False)
    activateMovers = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='SyncMovers', value=False)

    def __init__(self):
        self.__readyToActivate = False
        self.__startTime = 0
        self.__endTime = 0
        self.__duration = 0
        self.__removed = False

    @property
    def startTime(self):
        return self.__startTime

    @property
    def endTime(self):
        return self.__endTime

    @property
    def duration(self):
        return self.__duration

    @property
    def ready(self):
        return self.__readyToActivate

    @property
    def removed(self):
        return self.__removed

    def onRemove(self):
        self.__removed = True

    def setupTime(self, start, end):
        self.__startTime = start
        self.__endTime = end
        self.__duration = end - start
        self.__readyToActivate = True


@registerReplicableComponent
class ActivationController(object):
    category = 'Scenarios'
    editorTitle = 'ActivationController'
    eventStartTimeRange = ComponentProperty(type=CGFMetaTypes.VECTOR2, editorName='ActivationStartRange', value=(0.0, 5.0))

    @staticmethod
    def getTimedActivators(go):
        hr = CGF.HierarchyManager(go.spaceID)
        return hr.findComponentsInHierarchy(go, TimedActivation) if hr else []
