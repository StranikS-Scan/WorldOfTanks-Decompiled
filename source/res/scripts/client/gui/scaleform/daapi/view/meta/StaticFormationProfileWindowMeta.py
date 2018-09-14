# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationProfileWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class StaticFormationProfileWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def actionBtnClickHandler(self, action):
        """
        :param action:
        :return :
        """
        self._printOverrideError('actionBtnClickHandler')

    def onClickHyperLink(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('onClickHyperLink')

    def as_setWindowSizeS(self, width, height):
        """
        :param width:
        :param height:
        :return :
        """
        return self.flashObject.as_setWindowSize(width, height) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setFormationEmblemS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setFormationEmblem(value) if self._isDAAPIInited() else None

    def as_updateFormationInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateFormationInfo(data) if self._isDAAPIInited() else None

    def as_updateActionButtonS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateActionButton(data) if self._isDAAPIInited() else None

    def as_showViewS(self, idx):
        """
        :param idx:
        :return :
        """
        return self.flashObject.as_showView(idx) if self._isDAAPIInited() else None
