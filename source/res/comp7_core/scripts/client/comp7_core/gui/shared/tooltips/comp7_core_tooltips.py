# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/shared/tooltips/comp7_core_tooltips.py
import logging
from copy import copy
import typing
from constants import ROLE_TYPE_TO_LABEL
from gui import g_htmlTemplates
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, getRoleText
from gui.shared.items_parameters import formatters as params_formatters
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from gui.shared.utils.functions import stripColorTagDescrTags
from helpers_common import castNumberToPrettyStr, getPercentFromFloat
from items import tankmen
if typing.TYPE_CHECKING:
    from typing import Optional
    from items.artefacts import Equipment, VisualScriptEquipment
_logger = logging.getLogger(__name__)

class RoleSkillBattleTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(RoleSkillBattleTooltipData, self).__init__(context, None)
        self._setContentMargin(top=20, left=20, bottom=10, right=20)
        self._setWidth(320)
        return

    @property
    def _modeController(self):
        raise NotImplementedError

    def _packBlocks(self, roleName):
        equipment = self.context.buildItem(roleName)
        if equipment is None:
            _logger.error('Missing Role Skill for role = %s', roleName)
            return []
        else:
            startLevel = self.context.getStartLevel(roleName)
            items = [self.__packTooltipBlock(roleName, equipment, startLevel, self._modeController)]
            return items

    @staticmethod
    def __packTooltipBlock(roleName, equipment, startLevel, modeController):
        blocks = []
        blocks.append(formatters.packTitleDescBlock(title=text_styles.main(getRoleText(roleName)), desc=text_styles.middleTitle(equipment.userString)))
        active, passive = getRoleSkillDescription(equipment, roleName, startLevel, modeController)
        if active:
            blocks.append(formatters.packTextBlockData(text=text_styles.standard(stripColorTagDescrTags(active)), padding=formatters.packPadding(bottom=15)))
        if passive:
            blocks.append(formatters.packTextBlockData(text=text_styles.standard(stripColorTagDescrTags(passive)), padding=formatters.packPadding(bottom=15)))
        if startLevel > 0:
            blocks.append(formatters.packTextBlockData(text=text_styles.standard(getStartLevelBattleTooltipText(startLevel)), padding=formatters.packPadding(bottom=15)))
        blocks.append(formatters.packTextBlockData(text=text_styles.standard(getCooldown(equipment))))
        return formatters.packBuildUpBlockData(blocks=blocks)


class RoleSkillLobbyTooltipData(BlocksTooltipData):
    _PARAMS_TEMPLATE = g_htmlTemplates['html_templates:comp7/tooltips/']['roleSkill']

    def __init__(self, context):
        super(RoleSkillLobbyTooltipData, self).__init__(context, None)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setWidth(width=400)
        return

    @property
    def _modeController(self):
        raise NotImplementedError

    def _packBlocks(self, equipmentName, roleName, startLevel):
        equipment = self.context.buildItem(equipmentName)
        if equipment is None:
            _logger.error('Missing Role Skill = %s', equipmentName)
            return []
        else:
            items = filter(None, [self.__packHeaderBlock(equipment, roleName, self._modeController), self.__packDescriptionBlock(equipment, roleName, startLevel, self._modeController), self.__packInfoBlock()])
            return items

    @classmethod
    def __packHeaderBlock(cls, equipment, roleName, modeController):
        blocks = [formatters.packTitleDescBlock(title=text_styles.highTitle(equipment.userString), desc=cls.__getCooldown(equipment, roleName, modeController), gap=-3), formatters.packItemTitleDescBlockData(img=backport.image(cls.__getRoleSkillIcon(equipment)), padding=formatters.packPadding(left=90))]
        return formatters.packBuildUpBlockData(blocks=blocks)

    @classmethod
    def __packDescriptionBlock(cls, equipment, roleName, startLevel, modeController):
        blocks = []
        active, passive = getRoleSkillDescription(equipment, roleName, startLevel, modeController)
        if active:
            blocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.roleSkill.description.active())), desc=text_styles.main(cls.__formatEquipmentParams(active))))
        if passive:
            blocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.roleSkill.description.passive())), desc=text_styles.main(cls.__formatEquipmentParams(passive))))
        if startLevel > 0:
            blocks.append(formatters.packImageTextBlockData(desc=text_styles.main(backport.text(R.strings.tooltips.roleSkill.startLevel.lobby(), startLevel=startLevel)).format(**cls._PARAMS_TEMPLATE.source), descPadding=formatters.packPadding(0, -15, -50), img=backport.image(R.images.comp7.gui.maps.icons.icons.dyn('abilityChargeLvl{}_130x124'.format(startLevel))()), imgPadding=formatters.packPadding(4, -35), padding=formatters.packPadding(-40, 0, -19)))
        return None if not blocks else formatters.packBuildUpBlockData(blocks=blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    @classmethod
    def __formatEquipmentParams(cls, description):
        formatted = description.format(**cls._PARAMS_TEMPLATE.source)
        return formatted

    @staticmethod
    def __packInfoBlock():
        text = text_styles.main(backport.text(R.strings.tooltips.roleSkill.info()))
        return formatters.packTextBlockData(text=text)

    @staticmethod
    def __getCooldown(equipment, roleName, modeController):
        overrides = modeController.getRoleEquipmentOverrides(roleName)
        cooldown = overrides.get('cooldownSeconds') or equipment.cooldownSeconds
        paramName = ModuleTooltipBlockConstructor.RELOAD_COOLDOWN_SECONDS
        paramValue = params_formatters.formatParameter(paramName, cooldown)
        cooldown = params_formatters.formatParamNameColonValueUnits(paramName=paramName, paramValue=paramValue)
        return cooldown

    @staticmethod
    def __getRoleSkillIcon(equipment):
        icon = R.images.gui.maps.icons.roleSkills.c_180x180.dyn(equipment.name)
        if not icon:
            _logger.error('Missing RoleSkill icon: R.images.gui.maps.icons.roleSkills.%s', equipment.name)
            return R.invalid()
        return icon()


def getCooldown(equipment, cooldownSecondsOverride=None):
    cooldown = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
    return backport.text(cooldown, cooldownSeconds=cooldownSecondsOverride or equipment.cooldownSeconds)


def getStartLevelBattleTooltipText(startLevel):
    return backport.text(R.strings.tooltips.roleSkill.startLevel.battle(), startLevel=startLevel)


def getRoleSkillDescription(equipment, roleName, startLevel, modeController):
    params = {}
    tooltipParams = equipment.tooltipParams
    tooltipParams.update(modeController.getRoleEquipmentOverrides(roleName))
    if roleName in ROLE_TOOLTIP_PREPROCESSORS:
        tooltipParams = ROLE_TOOLTIP_PREPROCESSORS[roleName].processParams(copy(tooltipParams))
    for k, v in tooltipParams.iteritems():
        if isinstance(v, tuple):
            for level, levelValue in enumerate(v):
                levelKey = '_'.join((k, str(level + 1)))
                params[levelKey] = castNumberToPrettyStr(levelValue)

        params[k] = castNumberToPrettyStr(v)

    if startLevel is not None:
        params['startLevel'] = startLevel
    description = R.strings.artefacts.dyn(equipment.name).dyn('descr')
    active = description.dyn('active')
    active = backport.text(active(), **params) if active.exists() else ''
    passive = description.dyn('passive')
    passive = backport.text(passive(), **params) if passive.exists() else ''
    return (active, passive)


def getPoIEquipmentDescription(equipment, modeController):
    description = R.strings.artefacts.dyn(equipment.name).dyn('descr')
    tooltipParams = equipment.tooltipParams
    tooltipParams.update(modeController.getPoiEquipmentOverrides(equipment.name).get('overrides', {}))
    return backport.text(description(), **tooltipParams)


def getRoleEquipmentTooltipParts(vehicle, modeController):
    roleName = ROLE_TYPE_TO_LABEL.get(vehicle.descriptor.role, '')
    roleSkill = modeController.getRoleEquipment(roleName)
    if not roleSkill:
        from gui.battle_control import avatar_getter
        if not avatar_getter.isObserver():
            _logger.error('No equipment found for vehicle %s', vehicle.descriptor.name)
        return (None, None)
    else:
        startLevel = modeController.getEquipmentStartLevel(roleName) or 0
        startLevelText = getStartLevelBattleTooltipText(startLevel) if startLevel > 0 else None
        active, passive = getRoleSkillDescription(roleSkill, roleName, startLevel, modeController)
        overrides = modeController.getRoleEquipmentOverrides(roleName)
        cooldown = getCooldown(roleSkill, overrides.get('cooldownSeconds'))
        body = stripColorTagDescrTags('\n\n'.join(filter(None, (active,
         passive,
         startLevelText,
         cooldown))))
        return (roleSkill, body)


class TooltipPreprocessor(object):

    @staticmethod
    def processParams(params):
        pass


class Comp7AoeHealTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['heal'] = tuple((h * params['tickInterval'] * params['duration'] for h in params['heal']))
        return params


class Comp7AllyHunterTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['heal'] = tuple((h * params['tickInterval'] * params['duration'] for h in params['heal']))
        return params


class Comp7ConcentrationTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['shotDispersionFactorsBuff'] = tuple((getPercentFromFloat(1.0 - b, 1) for b in params['shotDispersionFactors']))
        return params


class Comp7BerserkTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['gunReloadTimeBuff'] = tuple((getPercentFromFloat(1.0 - b, 1) for b in params['gunReloadTimeBuff']))
        params['shotDispersionFactorsBuff'] = tuple((getPercentFromFloat(1.0 - b, 1) for b in params['shotDispersionFactors']))
        return params


class Comp7FastRechargeTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['gunReloadTimeBuff'] = tuple((getPercentFromFloat(1.0 - b, 1) for b in params['gunReloadTimeBuff']))
        return params


class Comp7JuggernautTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['enginePowerBuff'] = getPercentFromFloat(params['enginePowerFactor'] - 1.0, 1)
        params['dmgAbsorbBuff'] = tuple((getPercentFromFloat(1.0 - b, 1) for b in params['dmgAbsorb']))
        params['rammingDamageBuff'] = getPercentFromFloat(params['rammingDamageBonus'] - 1.0, 1)
        return params


class Comp7SureShotTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['shotDispersionFactorsBuff'] = tuple((getPercentFromFloat(1.0 - b, 1) for b in params['shotDispersionFactors']))
        params['gunReloadBuffDamage'] = tuple((b * 100 for b in params['slvl']))
        params['gunReloadBuffDestroy'] = tuple((b * 100 for b in params['sdlvl']))
        return params


class Comp7SniperTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['damageFactors'] = tuple((getPercentFromFloat(b - 1.0, 1) for b in params['damageFactors']))
        return params


class Comp7RiskyAttackTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['extraHealFactor'] = tuple((b * 100 for b in params['extraHealFactor']))
        return params


class Comp7ReconTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['lampDelay'] = tankmen.getSkillsConfig().getSkill('commander_sixthSense').delay
        return params


class Comp7AggressiveDetectionTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['visionBuff'] = tuple((getPercentFromFloat(b - 1.0, 1) for b in params['visionFactor']))
        return params


class Comp7MarchTooltipPreprocessor(TooltipPreprocessor):

    @staticmethod
    def processParams(params):
        params['enginePowerBuff'] = params['enginePowerBuff'] * 100
        params['invisibilityFactor'] = getPercentFromFloat(params['invisibilityFactor'] - 1.0, 1)
        return params


ROLE_TOOLTIP_PREPROCESSORS = {'role_HT_assault': Comp7AoeHealTooltipPreprocessor,
 'role_HT_universal': Comp7AllyHunterTooltipPreprocessor,
 'role_HT_support': Comp7ConcentrationTooltipPreprocessor,
 'role_MT_assault': Comp7BerserkTooltipPreprocessor,
 'role_MT_support': Comp7FastRechargeTooltipPreprocessor,
 'role_ATSPG_assault': Comp7JuggernautTooltipPreprocessor,
 'role_ATSPG_universal': Comp7SureShotTooltipPreprocessor,
 'role_ATSPG_sniper': Comp7SniperTooltipPreprocessor,
 'role_ATSPG_support': Comp7RiskyAttackTooltipPreprocessor,
 'role_LT_universal': Comp7ReconTooltipPreprocessor,
 'role_LT_wheeled': Comp7AggressiveDetectionTooltipPreprocessor,
 'role_SPG': Comp7MarchTooltipPreprocessor}
