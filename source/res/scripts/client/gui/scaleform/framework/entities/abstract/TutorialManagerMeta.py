# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/TutorialManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class TutorialManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def onComponentFound(self, componentId):
        """
        :param componentId:
        :return Array:
        """
        self._printOverrideError('onComponentFound')

    def onComponentDisposed(self, componentId):
        """
        :param componentId:
        :return :
        """
        self._printOverrideError('onComponentDisposed')

    def onTriggerActivated(self, componentId, triggerId):
        """
        :param componentId:
        :param triggerId:
        :return :
        """
        self._printOverrideError('onTriggerActivated')

    def requestCriteriaValue(self, criteriaName):
        """
        :param criteriaName:
        :return :
        """
        self._printOverrideError('requestCriteriaValue')

    def as_setSystemEnabledS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setSystemEnabled(value) if self._isDAAPIInited() else None

    def as_setDescriptionsS(self, descriptions):
        """
        :param descriptions:
        :return :
        """
        return self.flashObject.as_setDescriptions(descriptions) if self._isDAAPIInited() else None

    def as_setCriteriaS(self, criteriaName, criteriaValue, requestedCriteria):
        """
        :param criteriaName:
        :param criteriaValue:
        :param requestedCriteria:
        :return :
        """
        return self.flashObject.as_setCriteria(criteriaName, criteriaValue, requestedCriteria) if self._isDAAPIInited() else None

    def as_setTriggersS(self, componentId, triggers):
        """
        :param componentId:
        :param triggers:
        :return :
        """
        return self.flashObject.as_setTriggers(componentId, triggers) if self._isDAAPIInited() else None

    def as_showHintS(self, viewTutorialId, componentId, data, isCustomCmp):
        """
        :param viewTutorialId:
        :param componentId:
        :param data:
        :param isCustomCmp:
        :return :
        """
        return self.flashObject.as_showHint(viewTutorialId, componentId, data, isCustomCmp) if self._isDAAPIInited() else None

    def as_hideHintS(self, viewTutorialId, componentId):
        """
        :param viewTutorialId:
        :param componentId:
        :return :
        """
        return self.flashObject.as_hideHint(viewTutorialId, componentId) if self._isDAAPIInited() else None
