# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/TutorialManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class TutorialManagerMeta(BaseDAAPIModule):

    def onComponentFound(self, componentId):
        self._printOverrideError('onComponentFound')

    def onComponentDisposed(self, componentId):
        self._printOverrideError('onComponentDisposed')

    def onTriggerActivated(self, componentId, triggerId):
        self._printOverrideError('onTriggerActivated')

    def requestCriteriaValue(self, criteriaName):
        self._printOverrideError('requestCriteriaValue')

    def as_setSystemEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setSystemEnabled(value)

    def as_setDescriptionsS(self, descriptions):
        if self._isDAAPIInited():
            return self.flashObject.as_setDescriptions(descriptions)

    def as_setCriteriaS(self, criteriaName, criteriaValue, requestedCriteria):
        if self._isDAAPIInited():
            return self.flashObject.as_setCriteria(criteriaName, criteriaValue, requestedCriteria)

    def as_setTriggersS(self, componentId, triggers):
        if self._isDAAPIInited():
            return self.flashObject.as_setTriggers(componentId, triggers)

    def as_showHintS(self, viewTutorialId, componentId, data, isCustomCmp):
        if self._isDAAPIInited():
            return self.flashObject.as_showHint(viewTutorialId, componentId, data, isCustomCmp)

    def as_hideHintS(self, viewTutorialId, componentId):
        if self._isDAAPIInited():
            return self.flashObject.as_hideHint(viewTutorialId, componentId)
