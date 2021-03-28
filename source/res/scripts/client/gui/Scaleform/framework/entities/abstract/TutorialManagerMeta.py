# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/TutorialManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TutorialManagerMeta(BaseDAAPIComponent):

    def onComponentFound(self, componentId, viewTutorialId):
        self._printOverrideError('onComponentFound')

    def onComponentDisposed(self, componentId):
        self._printOverrideError('onComponentDisposed')

    def onTriggerActivated(self, componentId, triggerId, state):
        self._printOverrideError('onTriggerActivated')

    def onEffectCompleted(self, componentId, effectType):
        self._printOverrideError('onEffectCompleted')

    def onUbTrackedVarChanged(self, viewTutorialId, botNetID, varName, value):
        self._printOverrideError('onUbTrackedVarChanged')

    def as_setSystemEnabledS(self, value):
        return self.flashObject.as_setSystemEnabled(value) if self._isDAAPIInited() else None

    def as_setDescriptionsS(self, descriptions):
        return self.flashObject.as_setDescriptions(descriptions) if self._isDAAPIInited() else None

    def as_setCriteriaS(self, criteriaName, criteriaValue):
        return self.flashObject.as_setCriteria(criteriaName, criteriaValue) if self._isDAAPIInited() else None

    def as_setTriggersS(self, componentId, triggers):
        return self.flashObject.as_setTriggers(componentId, triggers) if self._isDAAPIInited() else None

    def as_showEffectS(self, viewTutorialId, componentId, effType, builderData):
        return self.flashObject.as_showEffect(viewTutorialId, componentId, effType, builderData) if self._isDAAPIInited() else None

    def as_hideEffectS(self, viewTutorialId, componentId, effType, builder):
        return self.flashObject.as_hideEffect(viewTutorialId, componentId, effType, builder) if self._isDAAPIInited() else None

    def as_setComponentViewCriteriaS(self, componentId, viewTutorialId):
        return self.flashObject.as_setComponentViewCriteria(componentId, viewTutorialId) if self._isDAAPIInited() else None

    def as_getComponentGlobalBoundsS(self, viewTutorialId, componentID):
        return self.flashObject.as_getComponentGlobalBounds(viewTutorialId, componentID) if self._isDAAPIInited() else None

    def as_getComponentPathS(self, viewTutorialId, botNetID):
        return self.flashObject.as_getComponentPath(viewTutorialId, botNetID) if self._isDAAPIInited() else None

    def as_setConditionsS(self, conditions):
        return self.flashObject.as_setConditions(conditions) if self._isDAAPIInited() else None

    def as_externalComponentFoundS(self, componentID, viewTutorialId, data):
        return self.flashObject.as_externalComponentFound(componentID, viewTutorialId, data) if self._isDAAPIInited() else None

    def as_updateExternalComponentS(self, componentID, viewTutorialId, data):
        return self.flashObject.as_updateExternalComponent(componentID, viewTutorialId, data) if self._isDAAPIInited() else None

    def as_disposeExternalComponentS(self, componentID, viewTutorialId):
        return self.flashObject.as_disposeExternalComponent(componentID, viewTutorialId) if self._isDAAPIInited() else None
