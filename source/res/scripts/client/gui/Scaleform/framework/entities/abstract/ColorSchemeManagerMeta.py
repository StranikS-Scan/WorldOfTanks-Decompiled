# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ColorSchemeManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ColorSchemeManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def getColorScheme(self, schemeName):
        """
        :param schemeName:
        :return Object:
        """
        self._printOverrideError('getColorScheme')

    def as_updateS(self):
        """
        :return :
        """
        return self.flashObject.as_update() if self._isDAAPIInited() else None
