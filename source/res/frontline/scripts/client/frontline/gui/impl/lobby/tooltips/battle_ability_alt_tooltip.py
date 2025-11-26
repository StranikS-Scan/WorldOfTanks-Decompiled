# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tooltips/battle_ability_alt_tooltip.py
from frameworks.wulf import ViewSettings
from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.tooltips.advanced import MODULE_MOVIES
from helpers import dependency
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.battle_ability_alt_tooltip_model import BattleAbilityAltTooltipModel
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache

class BattleAbilityAltTooltipView(ViewImpl):
    _slots__ = ('intCD',)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, intCD, *args, **kwargs):
        self.intCD = int(intCD)
        self.__epicSkills = self.__epicController.getEpicSkills()
        settings = ViewSettings(R.views.frontline.mono.lobby.tooltips.battle_ability_alt_tooltip())
        settings.model = BattleAbilityAltTooltipModel()
        super(BattleAbilityAltTooltipView, self).__init__(settings, *args, **kwargs)

    @property
    def viewModel(self):
        return super(BattleAbilityAltTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleAbilityAltTooltipView, self)._onLoading(*args, **kwargs)
        item = self.__itemsCache.items.getItemByCD(self.intCD)
        if not item:
            return
        else:
            with self.getViewModel().transaction() as model:
                skill = self.__epicSkills[item.innationID]
                info = skill.getSkillInfo()
                model.setName(info.name)
                model.setDescription(info.longDescr)
                movieKey = item.getGUIEmblemID()
                movieName = None
                if movieKey in MODULE_MOVIES:
                    movieName = MODULE_MOVIES[movieKey]
                model.setVideoName(movieName)
            return
