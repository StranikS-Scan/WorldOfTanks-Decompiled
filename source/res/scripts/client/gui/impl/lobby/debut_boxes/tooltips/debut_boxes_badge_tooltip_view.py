# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/debut_boxes/tooltips/debut_boxes_badge_tooltip_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel
from gui.impl.pub import ViewImpl
from gui.shared.missions.packers.debut_boxes import getDebutBoxesBonusPacker
from gui.shared.missions.packers.events import BattleQuestUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IDebutBoxesController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class DebutBoxesBadgeTooltipView(ViewImpl):
    __debutBoxesCtl = dependency.descriptor(IDebutBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.debutBoxes.DebutBoxesBadgeTooltipView())
        settings.model = QuestModel()
        settings.args = args
        settings.kwargs = kwargs
        super(DebutBoxesBadgeTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DebutBoxesBadgeTooltipView, self).getViewModel()

    def _onLoading(self, intCD, *args, **kwargs):
        with self.viewModel.transaction() as model:
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            quest = self.__debutBoxesCtl.getQuestForVehicle(vehicle)
            if quest is None:
                _logger.error('There is no available quests for vehicle %s', intCD)
            questUIPacker = BattleQuestUIDataPacker(quest, bonusPackerGetter=getDebutBoxesBonusPacker)
            questUIPacker.pack(model)
        return
