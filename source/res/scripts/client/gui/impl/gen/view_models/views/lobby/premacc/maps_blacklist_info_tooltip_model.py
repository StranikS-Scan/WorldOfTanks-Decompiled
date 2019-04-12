# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/maps_blacklist_info_tooltip_model.py
from frameworks.wulf import ViewModel

class MapsBlacklistInfoTooltipModel(ViewModel):
    __slots__ = ()

    def getMaxCooldownTime(self):
        return self._getNumber(0)

    def setMaxCooldownTime(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(MapsBlacklistInfoTooltipModel, self)._initialize()
        self._addNumberProperty('maxCooldownTime', 0)
