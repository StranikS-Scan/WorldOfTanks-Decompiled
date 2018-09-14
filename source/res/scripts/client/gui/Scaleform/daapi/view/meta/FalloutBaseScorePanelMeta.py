# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FalloutBaseScorePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FalloutBaseScorePanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def as_initS(self, maxValue, warningValue):
        return self.flashObject.as_init(maxValue, warningValue) if self._isDAAPIInited() else None

    def as_playScoreHighlightAnimS(self):
        return self.flashObject.as_playScoreHighlightAnim() if self._isDAAPIInited() else None

    def as_stopScoreHighlightAnimS(self):
        return self.flashObject.as_stopScoreHighlightAnim() if self._isDAAPIInited() else None
