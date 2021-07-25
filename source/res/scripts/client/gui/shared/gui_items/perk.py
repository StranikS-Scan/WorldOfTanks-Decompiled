# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/perk.py
import typing
from functools import partial
from constants import BASE_DAMAGE_MONITORING_DELAY
from gui import g_htmlTemplates
from items.components.component_constants import DEFAULT_DAMAGE_RANDOMIZATION, DEFAULT_PIERCING_POWER_RANDOMIZATION
from gui.impl import backport
from gui.impl.gen import R
from items import perks
from items.components.perks_constants import PerksValueType, PERK_BONUS_VALUE_PRECISION, PERKS_TYPE
from debug_utils import LOG_ERROR
if typing.TYPE_CHECKING:
    from items.components.perks_components import Perk

class PerkGUI(object):

    def _dmgMonitoringDelayBaseValue(self, *args):
        return BASE_DAMAGE_MONITORING_DELAY + args[0]

    def _dmgPenDispersionCombinedBase(self, *args):
        if DEFAULT_DAMAGE_RANDOMIZATION != DEFAULT_PIERCING_POWER_RANDOMIZATION:
            LOG_ERROR('Default damage randomization does not equal default piercing power randomization!')
        return DEFAULT_DAMAGE_RANDOMIZATION - args[0]

    def _equipmentCdTime(self, *args):
        value, uiSettings = args
        from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
        from gui.shared.items_parameters.functions import getEquipmentCdForPerkPercentToTimeConversion
        return value * getEquipmentCdForPerkPercentToTimeConversion(g_detachmentTankSetupVehicle.item, uiSettings.equipmentCooldown)

    _localeValueFormatters = {'dmgMonitoringDelayBaseValue': _dmgMonitoringDelayBaseValue,
     'dmgPenDispersionCombinedBase': _dmgPenDispersionCombinedBase,
     'equipmentCdTime': _equipmentCdTime}
    _ULTIMATE_BASE_LVL = 1

    def __init__(self, perkID, perkLevel=0):
        self._perk = perks.g_cache.perks().perks[perkID]
        self._perkLevel = perkLevel

    @property
    def id(self):
        return self._perk.id

    @property
    def perkType(self):
        return self._perk.perkType

    @property
    def isUltimate(self):
        return self._perk.perkType == PERKS_TYPE.ULTIMATE

    @property
    def situational(self):
        return self._perk.situational

    @property
    def isAutoperk(self):
        return self._perk.isAutoperk

    @property
    def name(self):
        return R.strings.item_types.abilities.perk_name.num(self.id)()

    @property
    def title(self):
        return R.strings.detachment.learnedSkills.perk_name.num(self.id)()

    @property
    def description(self):
        return R.strings.item_types.abilities.perk_desc.num(self.id)()

    @property
    def descriptionZeroLvl(self):
        return R.strings.item_types.abilities.perk_desc_zero_lvl.num(self.id)()

    @property
    def icon(self):
        return 'perk_{}'.format(self.id)

    @property
    def vehParamsIcon(self):
        return R.images.gui.maps.icons.perks.normal.c_24x24.dyn(self.icon)()

    @property
    def video(self):
        return 'perks/perk_{}'.format(self.id)

    @property
    def paramID(self):
        return '{}_{}'.format(self.id, self._perkLevel)

    @property
    def perkLevel(self):
        return self._perkLevel

    @property
    def formattedDescription(self):
        return self._formatDescription(self.description, self._perkLevel)

    @property
    def formattedDescriptionZeroLvl(self):
        return self._formatDescription(self.descriptionZeroLvl, self._perkLevel)

    @property
    def formattedDescriptionForUltimates(self):
        return self._formatDescription(self.description, self._ULTIMATE_BASE_LVL)

    @property
    def flashFormattedDescription(self):
        description = self.getFormattedDescriptionBasedOnLvl()
        description = description.replace('&zwnbsp;', '')
        return description.format(**g_htmlTemplates['html_templates:lobby/detachment']['tooltip'].source)

    @property
    def course(self):
        if self.isUltimate:
            if self.situational:
                return R.strings.detachment.learnedSkills.course_4()
            return R.strings.detachment.learnedSkills.course_3()
        return R.strings.detachment.learnedSkills.course_2() if self.situational else R.strings.detachment.learnedSkills.course_1()

    def hasParam(self, paramName):
        return paramName in self._perk.defaultBlockSettings

    def isSituationalForParam(self, paramName):
        perkArgument = self._perk.defaultBlockSettings.get(paramName, None)
        return False if not perkArgument else perkArgument.UISettings.situationalArg

    def getBonusFromBoost(self, levelBefore, bonusPoints):
        bonuses = []
        for bonusName, perkArgument in self._perk.defaultBlockSettings.iteritems():
            bonusValueBefore = self._perk.getArgBonusByLevel(bonusName, levelBefore)
            bonusValueAfter = self._perk.getArgBonusByLevel(bonusName, levelBefore + bonusPoints)
            formattedValue = self._formatValue(bonusValueAfter - bonusValueBefore, uiType=perkArgument.UISettings.type)
            isSituational = perkArgument.UISettings.situationalArg
            bonuses.append((bonusName, formattedValue, isSituational))

        return bonuses

    def getFormattedDescriptionBasedOnLvl(self):
        if self.perkLevel:
            description = self.formattedDescription
        elif self.isUltimate:
            description = self.formattedDescriptionForUltimates
        else:
            description = self.formattedDescriptionZeroLvl
        return description

    def getSpecialFormattedValue(self, uiSettings, value):
        if uiSettings.localeFormatting:
            specialFormatter = self._localeValueFormatters[uiSettings.localeFormatting]
            value = specialFormatter(self, value, uiSettings)
        return value

    def _formatDescription(self, description, level):
        bonuses = {}
        for bonusName, perkArgument in self._perk.defaultBlockSettings.iteritems():
            bonusValue = self._perk.getArgBonusByLevel(bonusName, level)
            bonusValue = self.getSpecialFormattedValue(perkArgument.UISettings, bonusValue)
            formatValue = partial(self._formatValue, uiType=perkArgument.UISettings.type)
            bonuses[bonusName] = formatValue(bonusValue)
            bonuses['{}.value'.format(bonusName)] = formatValue(perkArgument.value)
            bonuses['{}.maxStacks'.format(bonusName)] = perkArgument.maxStacks
            bonuses['{}.maxValue'.format(bonusName)] = formatValue(perkArgument.value * perkArgument.maxStacks)

        return backport.text(description, **bonuses)

    @staticmethod
    def _formatValue(value, uiType):
        numValue = round(abs(value), PERK_BONUS_VALUE_PRECISION) if value else 0
        formatStr = '{}'
        if uiType == PerksValueType.PERCENTS:
            numValue *= 100
            formatStr = '{}%'
        return formatStr.format(backport.getNiceNumberFormat(numValue))
