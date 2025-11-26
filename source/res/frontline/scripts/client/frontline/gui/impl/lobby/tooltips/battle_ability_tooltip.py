# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tooltips/battle_ability_tooltip.py
from frameworks.wulf import ViewSettings
from frontline.gui.frontline_helpers import AbilitiesTemplates
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.battle_ability_tooltip_levels_model import BattleAbilityTooltipLevelsModel
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.battle_ability_tooltip_param_model import BattleAbilityTooltipParamModel
from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.battle_ability_tooltip_model import BattleAbilityTooltipModel
from frontline.gui.frontline_helpers import getSkillParams
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache
TEMPLATES = AbilitiesTemplates(R.strings.fl_battle_abilities_setup.infoPanel.param.valueTemplate)

class BattleAbilityTooltipView(ViewImpl):
    _slots__ = ('intCD',)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, intCD, *args, **kwargs):
        self.intCD = int(intCD)
        self.__epicSkills = self.__epicController.getEpicSkills()
        settings = ViewSettings(R.views.frontline.mono.lobby.tooltips.battle_ability_tooltip(), args=args, kwargs=kwargs)
        settings.model = BattleAbilityTooltipModel()
        super(BattleAbilityTooltipView, self).__init__(settings, *args, **kwargs)

    @property
    def viewModel(self):
        return super(BattleAbilityTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleAbilityTooltipView, self)._onLoading(*args, **kwargs)
        item = self.__itemsCache.items.getItemByCD(self.intCD)
        if not item:
            return
        with self.getViewModel().transaction() as model:
            skill = self.__epicSkills[item.innationID]
            realLevel = self.__epicController.getSkillLevels().get(skill.skillID)
            info = skill.getSkillInfo()
            model.setName(info.name)
            model.setIsPurchased(realLevel)
            model.setImageName(info.icon)
            model.setCategory(skill.category)
            levels = model.getLevelsInfo()
            levels.clear()
            characteristics = model.getCharacteristics()
            characteristics.clear()
            self.__fillDetailsSkillLevels(levels, characteristics, skill)

    @staticmethod
    def __fillDetailsSkillLevels(levels, characteristics, skillData):
        skillParams = getSkillParams(skillData)
        for lvl in skillData.levels.iterkeys():
            levelModel = BattleAbilityTooltipLevelsModel()
            levels.addViewModel(levelModel)
            levelModel.setLevel(lvl)
            paramslevel = levelModel.getParams()
            for paramList in skillParams[lvl].itervalues():
                for param in paramList:
                    skillParam = BattleAbilityTooltipParamModel()
                    skillParam.setId(param.get('id'))
                    skillParam.setName(param.get('name'))
                    skillParam.setValue(param.get('value'))
                    skillParam.setSign(param.get('sign'))
                    skillParam.setValueTemplate(param.get('valueTemplate'))
                    if param['isDynamic']:
                        paramslevel.addViewModel(skillParam)
                    if lvl == 1:
                        characteristics.addViewModel(skillParam)
