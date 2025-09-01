# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/presenters_map.py
from __future__ import absolute_import
import typing
import weakref
from functools import partial
from future.utils import itervalues
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.vehicle_hub_view_model import VehicleHubViewModel
SubModelInfo = typing.NamedTuple('_SubModelInfo', [('ID', str), ('presenter', SubPresenterBase)])

class PresentersMap(object):

    def __init__(self, mainView):
        self.__presentersCache = {}
        self.__mainView = weakref.proxy(mainView)
        self.__loadersMap = {VehicleHubViewModel.OVERVIEW: partial(self.__makeSubModel, VehicleHubViewModel.OVERVIEW, self.__loadOverview),
         VehicleHubViewModel.MODULES: partial(self.__makeSubModel, VehicleHubViewModel.MODULES, self.__loadModules),
         VehicleHubViewModel.VEH_SKILL_TREE: partial(self.__makeSubModel, VehicleHubViewModel.VEH_SKILL_TREE, self.__loadVehSkillTree),
         VehicleHubViewModel.STATS: partial(self.__makeSubModel, VehicleHubViewModel.STATS, self.__loadStats),
         VehicleHubViewModel.ARMOR: partial(self.__makeSubModel, VehicleHubViewModel.ARMOR, self.__loadArmor)}

    def itervalues(self):
        return itervalues(self.__presentersCache)

    def clear(self):
        self.__loadersMap = {}
        self.__presentersCache = {}
        self.__mainView = None
        return

    def __getitem__(self, item):
        if item not in self.__presentersCache:
            self.__tryToLoadPresenter(item)
        return self.__presentersCache.get(item, None)

    def __tryToLoadPresenter(self, key):
        if key in self.__loadersMap:
            self.__presentersCache[key] = self.__loadersMap[key]()

    def __loadOverview(self):
        from gui.impl.lobby.vehicle_hub.sub_presenters.overview_sub_presenter import OverviewSubPresenter
        return OverviewSubPresenter(self.__mainView.viewModel.overviewModel, self.__mainView)

    def __loadModules(self):
        from gui.impl.lobby.vehicle_hub.sub_presenters.modules_sub_presenter import ModulesSubPresenter
        return ModulesSubPresenter(self.__mainView.viewModel.modulesModel, self.__mainView)

    def __loadStats(self):
        from gui.impl.lobby.vehicle_hub.sub_presenters.stats_sub_presenter import StatsSubPresenter
        return StatsSubPresenter(self.__mainView.viewModel.statsModel, self.__mainView)

    def __loadVehSkillTree(self):
        from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree_sub_presenter import VehSkillTreeSubPresenter
        return VehSkillTreeSubPresenter(self.__mainView.viewModel.vehSkillTreeModel, self.__mainView)

    def __loadArmor(self):
        from gui.impl.lobby.vehicle_hub.sub_presenters.armor.armor_sub_presenter import ArmorSubPresenter
        return ArmorSubPresenter(self.__mainView.viewModel.armorModel, self.__mainView)

    @staticmethod
    def __makeSubModel(viewAlias, loader):
        return SubModelInfo(viewAlias, loader())
