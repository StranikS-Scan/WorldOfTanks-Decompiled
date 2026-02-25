# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/minor_short_tooltip.py
from __future__ import absolute_import
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.minor_short_tooltip_model import MinorShortTooltipModel
from gui.impl.pub import ViewImpl

class MinorShortTooltip(ViewImpl):
    __slots__ = ('_icon', '_header', '_description')

    def __init__(self, icon, header, description):
        settings = ViewSettings(R.views.mono.vehicle_hub.tooltips.minor_short_tooltip(), model=MinorShortTooltipModel())
        self._icon = icon
        self._header = header
        self._description = description
        super(MinorShortTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MinorShortTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MinorShortTooltip, self)._onLoading(*args, **kwargs)
        if self._icon:
            self.viewModel.setIcon(self._icon)
        self.viewModel.setHeader(self._header)
        self.viewModel.setDescription(self._description)
