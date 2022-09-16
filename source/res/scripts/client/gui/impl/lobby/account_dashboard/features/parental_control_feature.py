# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/parental_control_feature.py
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.lobby.premacc.dashboard.parent_control_info_popover import ParentControlInfoPopoverContent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.shared import IItemsCache

class ParentalControlFeature(FeatureItem):
    __gameSession = dependency.descriptor(IGameSessionController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def initialize(self, *args, **kwargs):
        super(ParentalControlFeature, self).initialize(*args, **kwargs)
        self.__gameSession.onParentControlNotify += self.__onParentControlNotify

    def finalize(self):
        self.__gameSession.onParentControlNotify -= self.__onParentControlNotify
        super(ParentalControlFeature, self).finalize()

    def createPopOverContent(self, event):
        return ParentControlInfoPopoverContent()

    def _fillModel(self, model):
        self.__update(model=model)

    @replaceNoneKwargsModel
    def __update(self, model=None):
        limitsEnabled = self.__itemsCache.items.gameRestrictions.hasSessionLimit
        model.setIsParentalControlEnabled(limitsEnabled)

    def __onParentControlNotify(self):
        self.__update()
