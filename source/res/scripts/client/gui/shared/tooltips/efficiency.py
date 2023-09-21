# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/efficiency.py
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_results.components.style import getTooltipParamsStyle
from gui import makeHtmlString
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.formatters import text_styles
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from helpers.i18n import makeString as ms

def makeHtmlText(pattern, text):
    return makeHtmlString('html_templates:lobby/battle_results', pattern, {'text': text})


class HeaderItemPacker(object):

    def __init__(self, headerTitle, icon):
        super(HeaderItemPacker, self).__init__()
        self.__headerTitle = headerTitle
        self.__icon = icon

    def pack(self, data):
        titleStr = text_styles.highTitle(self.__headerTitle)
        return [formatters.packImageTextBlockData(titleStr, img=self.__icon, txtPadding={'left': 18,
          'top': 9,
          'bottom': 1}, padding={'left': 2,
          'top': 7}, titleAtMiddle=True)]


class TermsItemPacker(HeaderItemPacker):
    _titleID = R.invalid()
    _descriptionID = R.invalid()
    _iconID = R.invalid()

    def __init__(self):
        super(TermsItemPacker, self).__init__(backport.text(self._titleID), backport.image(self._iconID))
        self._termsAlias = backport.text(self._descriptionID)

    def pack(self, data):
        items = super(TermsItemPacker, self).pack(data)
        items.append(formatters.packBuildUpBlockData(self._packTerms(data)))
        return items

    def _packTerms(self, data):
        text = makeHtmlText('tooltip_terms_label', ms(self._termsAlias))
        return [formatters.packTextBlockData(text)]


class LinerItemPacker(TermsItemPacker):

    def pack(self, data):
        items = super(LinerItemPacker, self).pack(data)
        values = data.get('values', None)
        discript = data.get('discript', None)
        if values is not None and discript:
            packer = formatters.packTextParameterBlockData
            blocks = [ packer(value=value, name=name) for value, name in zip(values, discript) ]
            blockToInsert = formatters.packBuildUpBlockData(blocks)
            items.append(blockToInsert)
        return items


class KillItemPacker(TermsItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.kill.header()
    _descriptionID = R.strings.battle_results.common.tooltip.kill_1.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.destruction()

    def pack(self, data):
        items = super(KillItemPacker, self).pack(data)
        reason = data.get('killReason', None)
        if reason is not None and reason >= 0:
            rKill = R.strings.battle_results.common.tooltip.dyn('kill{}'.format(reason))
            if rKill:
                text = makeHtmlText('tooltip_add_info_label', backport.text(rKill.description()))
                items.append(formatters.packTextBlockData(text))
        return items

    def _packTerms(self, data):
        text = makeHtmlText('tooltip_terms_label', ms(self._termsAlias))
        return [formatters.packTextBlockData(text)]


class TotalKillItemPacker(KillItemPacker):
    _titleID = R.strings.postbattle_screen.tooltip.kill.header()
    _descriptionID = R.strings.postbattle_screen.tooltip.kill_1.description()

    def pack(self, data):
        items = super(TotalKillItemPacker, self).pack(data)
        deathReasons = data.get('deathReasons', {})
        if deathReasons:
            packer = formatters.packTextParameterBlockData
            blocks = [ packer(value=str(value), name=backport.text(R.strings.postbattle_screen.tooltip.kill.num(reason)())) for reason, value in deathReasons.iteritems() ]
            blocks.append(packer(value=str(sum(deathReasons.values())), name=backport.text(R.strings.postbattle_screen.tooltip.kill.totalKilled(), vals=getTooltipParamsStyle())))
            blockToInsert = formatters.packBuildUpBlockData(blocks)
            items.append(blockToInsert)
        return items


class DetectionItemPacker(LinerItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.spotted.header()
    _descriptionID = R.strings.battle_results.common.tooltip.spotted.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.detection()


class TotalDetectionItemPacker(DetectionItemPacker):
    _titleID = R.strings.postbattle_screen.tooltip.spotted.header()
    _descriptionID = R.strings.postbattle_screen.tooltip.spotted.description()

    def pack(self, data):
        items = super(TotalDetectionItemPacker, self).pack(data)
        value = data.get('spotted')
        if value:
            packer = formatters.packTextParameterBlockData
            blocks = [packer(value=backport.getIntegralFormat(value), name=backport.text(R.strings.postbattle_screen.tooltip.spotted.totalTanks()))]
            blockToInsert = formatters.packBuildUpBlockData(blocks)
            items.append(blockToInsert)
        return items


class DamageItemPacker(LinerItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.damage.header()
    _descriptionID = R.strings.battle_results.common.tooltip.damage.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.damage()


class TotalDamageItemPacker(DamageItemPacker):
    _titleID = R.strings.postbattle_screen.tooltip.damage.header()
    _descriptionID = R.strings.postbattle_screen.tooltip.damage.description()


class ArmorItemPacker(LinerItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.armor.header()
    _descriptionID = R.strings.battle_results.common.tooltip.armor.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.armor()


class TotalArmorItemPacker(ArmorItemPacker):
    _titleID = R.strings.postbattle_screen.tooltip.armor.header()
    _descriptionID = R.strings.postbattle_screen.tooltip.armor.description()


class StunItemPacker(LinerItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.stun.header()
    _descriptionID = R.strings.battle_results.common.tooltip.stun.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.stun()


class TotalStunItemPacker(StunItemPacker):
    _titleID = R.strings.postbattle_screen.tooltip.stun.header()
    _descriptionID = R.strings.postbattle_screen.tooltip.stun.description()


class AssistItemPacker(LinerItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.assist.header()
    _descriptionID = R.strings.battle_results.common.tooltip.assist.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.help()


class TotalAssistItemPacker(AssistItemPacker):
    _titleID = R.strings.postbattle_screen.tooltip.assist.header()
    _descriptionID = R.strings.postbattle_screen.tooltip.assist.description()


class CritsItemPacker(TermsItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.crits.header()
    _descriptionID = R.strings.battle_results.common.tooltip.crits.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.module()
    _damageLabelID = R.strings.battle_results.common.tooltip.crits.critDamage()
    _destructionLabelID = R.strings.battle_results.common.tooltip.crits.critDestruction()
    _woundLabelID = R.strings.battle_results.common.tooltip.crits.critWound()

    def pack(self, data):
        items = super(CritsItemPacker, self).pack(data)
        critDamage = data.get('critDamage', None)
        critWound = data.get('critWound', None)
        critDestruction = data.get('critDestruction', None)
        self._addMainText(critDamage, critDestruction, critWound, items)
        if data['isGarage']:
            text = makeHtmlText('tooltip_add_info_label', backport.text(R.strings.battle_results.garage.uniqueDamage()))
            items.append(formatters.packTextBlockData(text))
        return items

    @classmethod
    def _addMainText(cls, critDamage, critDestruction, critWound, items):
        if critDamage:
            cls._addResultBlock(items, backport.text(cls._damageLabelID), critDamage)
        if critDestruction:
            cls._addResultBlock(items, backport.text(cls._destructionLabelID), critDestruction)
        if critWound:
            cls._addResultBlock(items, backport.text(cls._woundLabelID), critWound)

    @classmethod
    def _addResultBlock(cls, items, title, text):
        htmlTitle = makeHtmlText('tooltip_block_title_label', title)
        items.append(formatters.packResultBlockData(htmlTitle, text))


class TotalCritsItemPacker(CritsItemPacker):
    _titleID = R.strings.postbattle_screen.tooltip.crits.header()
    _descriptionID = R.strings.postbattle_screen.tooltip.crits.description()
    _damageLabelID = R.strings.postbattle_screen.tooltip.crits.destroyedDevices()
    _destructionLabelID = R.strings.postbattle_screen.tooltip.crits.criticalDevices()
    _woundLabelID = R.strings.postbattle_screen.tooltip.crits.destroyedTankmen()

    def pack(self, data):
        items = super(TotalCritsItemPacker, self).pack(data)
        critDamage = data.get('allCritDamage')
        critDestruction = data.get('allCritDestruction')
        critWound = data.get('allCritWound')
        self._addMainText(critDamage, critDestruction, critWound, items)
        return items


class CaptureItemPacker(LinerItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.capture.header()
    _descriptionID = R.strings.battle_results.common.tooltip.capture.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.capture()


class DefenceItemPacker(LinerItemPacker):
    _titleID = R.strings.battle_results.common.tooltip.defence.header()
    _descriptionID = R.strings.battle_results.common.tooltip.defence.description()
    _iconID = R.images.gui.maps.icons.library.efficiency.c_48x48.defence()


class EfficiencyTooltipData(BlocksTooltipData):
    _tooltipType = TOOLTIP_TYPE.EFFICIENCY
    _packers = {BATTLE_EFFICIENCY_TYPES.ARMOR: ArmorItemPacker,
     BATTLE_EFFICIENCY_TYPES.DAMAGE: DamageItemPacker,
     BATTLE_EFFICIENCY_TYPES.DESTRUCTION: KillItemPacker,
     BATTLE_EFFICIENCY_TYPES.DETECTION: DetectionItemPacker,
     BATTLE_EFFICIENCY_TYPES.ASSIST: AssistItemPacker,
     BATTLE_EFFICIENCY_TYPES.CRITS: CritsItemPacker,
     BATTLE_EFFICIENCY_TYPES.CAPTURE: CaptureItemPacker,
     BATTLE_EFFICIENCY_TYPES.DEFENCE: DefenceItemPacker,
     BATTLE_EFFICIENCY_TYPES.ASSIST_STUN: StunItemPacker}

    def __init__(self, context):
        super(EfficiencyTooltipData, self).__init__(context, self._tooltipType)
        self._setWidth(300)

    def _packBlocks(self, data):
        return self._packers[data.type]().pack(data.toDict()) if data is not None and data.type in self._packers else []


class TotalEfficiencyTooltipData(EfficiencyTooltipData):
    _packers = {BATTLE_EFFICIENCY_TYPES.ARMOR: TotalArmorItemPacker,
     BATTLE_EFFICIENCY_TYPES.DAMAGE: TotalDamageItemPacker,
     BATTLE_EFFICIENCY_TYPES.DESTRUCTION: TotalKillItemPacker,
     BATTLE_EFFICIENCY_TYPES.DETECTION: TotalDetectionItemPacker,
     BATTLE_EFFICIENCY_TYPES.ASSIST: TotalAssistItemPacker,
     BATTLE_EFFICIENCY_TYPES.CRITS: TotalCritsItemPacker,
     BATTLE_EFFICIENCY_TYPES.ASSIST_STUN: TotalStunItemPacker}
