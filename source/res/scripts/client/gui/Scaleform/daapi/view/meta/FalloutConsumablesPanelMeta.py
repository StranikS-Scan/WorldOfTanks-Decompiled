# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FalloutConsumablesPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel

class FalloutConsumablesPanelMeta(ConsumablesPanel):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ConsumablesPanel
    null
    """

    def as_initializeRageProgressS(self, show, barProps):
        """
        :param show:
        :param barProps:
        :return :
        """
        return self.flashObject.as_initializeRageProgress(show, barProps) if self._isDAAPIInited() else None

    def as_updateProgressBarValueByDeltaS(self, delta):
        """
        :param delta:
        :return :
        """
        return self.flashObject.as_updateProgressBarValueByDelta(delta) if self._isDAAPIInited() else None

    def as_updateProgressBarValueS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_updateProgressBarValue(value) if self._isDAAPIInited() else None
