# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/crew_perks_additional_tooltip.py
import logging
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_additional_tooltip_model import CrewPerksAdditionalTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import getTankmanSkill
from gui.shared.tooltips.advanced import SKILL_MOVIES
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Tankman import TankmanSkill
_logger = logging.getLogger(__name__)

class CrewPerksAdditionalTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_skill',)

    def __init__(self, skillName=None, tankmanId=None):
        settings = ViewSettings(R.views.lobby.crew.tooltips.CrewPerksAdditionalTooltip())
        settings.model = CrewPerksAdditionalTooltipModel()
        self._skill = getTankmanSkill(skillName, tankman=self._itemsCache.items.getTankman(int(tankmanId)) if tankmanId else None)
        super(CrewPerksAdditionalTooltip, self).__init__(settings)
        return

    def onError(self, args):
        errorFilePath = str(args.get('errorFilePath', ''))
        _logger.error('Reward video error: %s', errorFilePath)
        self.destroyWindow()

    @property
    def viewModel(self):
        return super(CrewPerksAdditionalTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrewPerksAdditionalTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _getEvents(self):
        return ((self.viewModel.onError, self.onError),)

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setIcon(self._skill.bigIconPath)
            vm.setSkillType(self._skill.typeName)
            vm.setTitle(self._skill.userName)
            vm.setDescription(self._skill.altDescription)
            vm.setInfo(self._skill.altInfo)
            movieName = SKILL_MOVIES.get(self._skill.name, None)
            if movieName:
                vm.setAnimationName(movieName)
        return
