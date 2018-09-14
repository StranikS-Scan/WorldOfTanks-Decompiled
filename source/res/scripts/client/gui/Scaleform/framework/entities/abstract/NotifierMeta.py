# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/NotifierMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class NotifierMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def showDialog(self, kind, title, text, buttons, handlers):
        """
        :param kind:
        :param title:
        :param text:
        :param buttons:
        :param handlers:
        :return :
        """
        self._printOverrideError('showDialog')

    def showI18nDialog(self, kind, i18nKey, handlers):
        """
        :param kind:
        :param i18nKey:
        :param handlers:
        :return :
        """
        self._printOverrideError('showI18nDialog')
