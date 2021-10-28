# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/tooltips/nitro_tooltip.py
from gui.impl.gen import R
from helpers import dependency
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from gui.impl.gen.view_models.views.lobby.halloween.tooltips.nitro_tooltip_model import NitroTooltipModel
RECHARGE_TIME = 90

class NitroTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.halloween.tooltips.NitroTooltip())
        settings.model = NitroTooltipModel()
        super(NitroTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NitroTooltip, self).getViewModel()

    def _onLoading(self):
        super(NitroTooltip, self)._onLoading()
        self.viewModel.setTimeRecharge(RECHARGE_TIME)
