# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IntroPageMeta.py
from gui.Scaleform.framework.entities.View import View

class IntroPageMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def stopVideo(self):
        """
        :return :
        """
        self._printOverrideError('stopVideo')

    def handleError(self, data):
        """
        :param data:
        :return :
        """
        self._printOverrideError('handleError')

    def as_playVideoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_playVideo(data) if self._isDAAPIInited() else None
