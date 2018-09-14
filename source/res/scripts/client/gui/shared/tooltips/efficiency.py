# Embedded file name: scripts/client/gui/shared/tooltips/efficiency.py
from gui import makeHtmlString
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.tooltips import formatters
from helpers.i18n import makeString as ms
from gui.shared.formatters import text_styles

def makeHtmlText(pattern, text):
    return makeHtmlString('html_templates:lobby/battle_results', pattern, {'text': text})


class HeaderItemPacker(object):

    def __init__(self, headerTitle, icon):
        super(HeaderItemPacker, self).__init__()
        self.__headerTitle = headerTitle
        self.__icon = icon

    def pack(self, data):
        titleStr = text_styles.highTitle(self.__headerTitle)
        return [formatters.packHeadBlockData(titleStr, self.__icon)]


class TermsItemPacker(HeaderItemPacker):

    def __init__(self, headerTitle, icon, termsAlias):
        super(TermsItemPacker, self).__init__(headerTitle, icon)
        self.__termsAlias = termsAlias

    def pack(self, data):
        items = super(TermsItemPacker, self).pack(data)
        items.append(formatters.packBuildUpBlockData(self._packTerms(data)))
        return items

    def _packTerms(self, data):
        text = makeHtmlText('tooltip_terms_label', ms(self.__termsAlias))
        return [formatters.packTextBlockData(text)]


class KillItemPacker(TermsItemPacker):

    def __init__(self):
        super(KillItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_KILL_HEADER, RES_ICONS.MAPS_ICONS_LIBRARY_RIBBONS_180X68_DESTRUCTION, BATTLE_RESULTS.COMMON_TOOLTIP_KILL_1_DESCRIPTION)

    def pack(self, data):
        items = super(KillItemPacker, self).pack(data)
        reason = data.get('killReason', None)
        if reason is not None and reason >= 0:
            alias = '#battle_results:common/tooltip/kill{0}/description'.format(reason)
            text = makeHtmlText('tooltip_add_info_label', ms(alias))
            items.append(formatters.packTextBlockData(text))
        return items


class DetectionItemPacker(TermsItemPacker):

    def __init__(self):
        super(DetectionItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_SPOTTED_HEADER, RES_ICONS.MAPS_ICONS_LIBRARY_RIBBONS_180X68_DETECTION, BATTLE_RESULTS.COMMON_TOOLTIP_SPOTTED_DESCRIPTION)


class LinerItemPacker(TermsItemPacker):

    def __init__(self, headerTitle, icon, termsAlias):
        super(LinerItemPacker, self).__init__(headerTitle, icon, termsAlias)

    def pack(self, data):
        items = super(LinerItemPacker, self).pack(data)
        values = data.get('values', None)
        discript = data.get('discript', None)
        if values is not None and discript is not None:
            blocks = [formatters.packTextParameterBlockData(discript, values)]
            blockToInsert = formatters.packBuildUpBlockData(blocks)
            items.append(blockToInsert)
        return items


class DamageItemPacker(LinerItemPacker):

    def __init__(self):
        super(DamageItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_DAMAGE_HEADER, RES_ICONS.MAPS_ICONS_LIBRARY_RIBBONS_180X68_DAMAGE, BATTLE_RESULTS.COMMON_TOOLTIP_DAMAGE_DESCRIPTION)


class ArmorItemPacker(LinerItemPacker):

    def __init__(self):
        super(ArmorItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_HEADER, RES_ICONS.MAPS_ICONS_LIBRARY_RIBBONS_180X68_ARMOR, BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_DESCRIPTION)


class AssistItemPacker(LinerItemPacker):

    def __init__(self):
        super(AssistItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_HEADER, RES_ICONS.MAPS_ICONS_LIBRARY_RIBBONS_180X68_HELP, BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_DESCRIPTION)


class CaptureItemPacker(LinerItemPacker):

    def __init__(self):
        super(CaptureItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_CAPTURE_HEADER, RES_ICONS.MAPS_ICONS_LIBRARY_RIBBONS_180X68_CAPTURE, BATTLE_RESULTS.COMMON_TOOLTIP_CAPTURE_DESCRIPTION)


class DefenceItemPacker(LinerItemPacker):

    def __init__(self):
        super(DefenceItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_DEFENCE_HEADER, RES_ICONS.MAPS_ICONS_LIBRARY_RIBBONS_180X68_DEFENCE, BATTLE_RESULTS.COMMON_TOOLTIP_DEFENCE_DESCRIPTION)


class CritsItemPacker(TermsItemPacker):

    def __init__(self):
        super(CritsItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_CRITS_HEADER, RES_ICONS.MAPS_ICONS_LIBRARY_RIBBONS_180X68_MODULE, BATTLE_RESULTS.COMMON_TOOLTIP_CRITS_DESCRIPTION)

    def pack(self, data):
        items = super(CritsItemPacker, self).pack(data)
        critDamage = data.get('critDamage', None)
        critWound = data.get('critWound', None)
        critDestruction = data.get('critDestruction', None)
        if critDamage is not None and len(critDamage) > 0:
            self.__addResultBlock(items, BATTLE_RESULTS.COMMON_TOOLTIP_CRITS_CRITDAMAGE, critDamage)
        if critDestruction is not None and len(critDestruction) > 0:
            self.__addResultBlock(items, BATTLE_RESULTS.COMMON_TOOLTIP_CRITS_CRITDESTRUCTION, critDestruction)
        if critWound is not None and len(critWound) > 0:
            self.__addResultBlock(items, BATTLE_RESULTS.COMMON_TOOLTIP_CRITS_CRITWOUND, critWound)
        if data['isGarage']:
            text = makeHtmlText('tooltip_add_info_label', ms(BATTLE_RESULTS.FALLOUT_UNIQUEDAMAGE))
            items.append(formatters.packTextBlockData(text))
        return items

    def __addResultBlock(self, items, title, text):
        htmlTitle = makeHtmlText('tooltip_block_title_label', ms(title))
        items.append(formatters.packResultBlockData(htmlTitle, text))
