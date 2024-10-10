# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ability.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SHOW_ABILITY_ADVANCE_ANIM
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import ToolTipBaseData
from items.vehicles import g_cache
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.tank_setup.tooltips.abilities.ability_tooltip_model import AbilityTooltipModel
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel

class AbilitySkillTooltip(ViewImpl):
    __slots__ = ('_ability', '_vehicleIntCD')

    def __init__(self, abilityID, vehicleIntCD, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.tanksetup.tooltips.AbilitySkillTooltip(), args=args, kwargs=kwargs)
        settings.model = AbilityTooltipModel()
        self._ability = g_cache.getEquipmentByID(abilityID)
        self._vehicleIntCD = vehicleIntCD
        super(AbilitySkillTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AbilitySkillTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(AbilitySkillTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setVehicleIntCD(self._vehicleIntCD)
            vm.setUserString(self._ability.userString)
            vm.setDescription(self._ability.description)
            vm.setIconName(self._ability.iconName)
            vm.setReuseCount(self._ability.reuseCount)
            vm.setDuration(self._ability.duration)
            vm.setCooldown(self._ability.cooldownSeconds)
            vm.setLightAdditional(AccountSettings.getSettings(SHOW_ABILITY_ADVANCE_ANIM))
            bonusesArray = vm.bonuses.getItems()
            bonusesArray.clear()
            for kpi in self._ability.kpi:
                value = BonusValueModel()
                value.setValue(kpi.value)
                value.setValueKey(kpi.name)
                value.setValueType(kpi.type)
                value.setIsDebuff(kpi.isDebuff)
                if kpi.specValue:
                    value.setSpecValue(kpi.specValue)
                bonusModel = BonusModel()
                bonusModel.setLocaleName(kpi.name)
                bonusModel.getValues().addViewModel(value)
                bonusesArray.addViewModel(bonusModel)

            bonusesArray.invalidate()


class AbilitySkillTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(AbilitySkillTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.ABILITY_LOBBY_TOOLTIP)

    def getDisplayableData(self, abilityID, vehicleIntCD, parent=None, *args, **kwargs):
        return DecoratedTooltipWindow(AbilitySkillTooltip(abilityID, vehicleIntCD), parent, False)

    def buildToolTip(self, *args, **kwargs):
        return {'type': self.getType(),
         'component': self.context.getComponent()}

    def setSupportAdvanced(self, supportAdvanced):
        pass


class AbilitySkillAdditionalTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.tanksetup.tooltips.AbilitySkillAdditionalTooltip())
        settings.model = ViewModel()
        super(AbilitySkillAdditionalTooltip, self).__init__(settings)


class AbilitySkillTooltipDataAdditional(AbilitySkillTooltipData):

    def getDisplayableData(self, ability, vehicleIntCD, parent=None, *args, **kwargs):
        AccountSettings.setSettings(SHOW_ABILITY_ADVANCE_ANIM, False)
        return DecoratedTooltipWindow(AbilitySkillAdditionalTooltip(), parent, False)
