# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TrainingFormMeta.py
from gui.Scaleform.framework.entities.View import View

class TrainingFormMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def joinTrainingRequest(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('joinTrainingRequest')

    def createTrainingRequest(self):
        """
        :return :
        """
        self._printOverrideError('createTrainingRequest')

    def onEscape(self):
        """
        :return :
        """
        self._printOverrideError('onEscape')

    def onLeave(self):
        """
        :return :
        """
        self._printOverrideError('onLeave')

    def as_setListS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setList(data) if self._isDAAPIInited() else None
