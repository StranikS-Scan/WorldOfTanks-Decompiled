# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/tooltips/charm_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.charm_model import CharmModel
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import updateCharmModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from lunar_ny.lunar_ny_charm import LunarNYCharm
from skeletons.gui.shared import IItemsCache

class CharmTooltip(ViewImpl[CharmModel]):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.lunar_ny.CharmTooltip())
        settings.model = CharmModel()
        settings.args = args
        settings.kwargs = kwargs
        super(CharmTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CharmTooltip, self)._onLoading(*args, **kwargs)
        charmId = kwargs.get('charmID')
        charms = self.__itemsCache.items.lunarNY.getCharms()
        charm = charms[charmId] if charmId in charms else LunarNYCharm(charmId, 0, 0, 0)
        with self.viewModel.transaction() as tx:
            updateCharmModel(charm, tx)
