# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileMeta.py
from gui.Scaleform.framework.entities.View import View

class ProfileMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def onCloseProfile(self):
        """
        :return :
        """
        self._printOverrideError('onCloseProfile')

    def as_updateS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None
