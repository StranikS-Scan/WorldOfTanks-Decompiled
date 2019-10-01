# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/crew_bundle.py
from collections import namedtuple
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from shared_utils import CONST_CONTAINER
from soft_exception import SoftException
_R_TOOLTIPS_TEXT = R.strings.tooltips.crewBundle
_R_SKILLS_IMAGES = R.images.gui.maps.icons.tankmen.skills.big

class _Bonuses(CONST_CONTAINER):
    BASIC_ROLE_BOOST_100 = 'basicRoleBoost_100'
    ANY_ADDITIONAL_SKILL = 'anyAdditionalSkill'
    SAME_BLOOD_ZERO_SKILL = 'sameBloodZeroSkill'


_BUNDLE_PRESETS = {'offspring': (_Bonuses.BASIC_ROLE_BOOST_100, _Bonuses.ANY_ADDITIONAL_SKILL, _Bonuses.SAME_BLOOD_ZERO_SKILL)}

class _BonusPreset(namedtuple('BonusPreset', ('imageRPath', 'textRPath', 'top', 'left', 'bottom', 'right'))):

    def __new__(cls, imageRPath, textRPath, top=0, left=15, bottom=0, right=30):
        return super(_BonusPreset, cls).__new__(cls, imageRPath, textRPath, top, left, bottom, right)


_BONUS_PRESETS = {_Bonuses.BASIC_ROLE_BOOST_100: _BonusPreset(R.images.gui.maps.icons.crewBundles.bonuses.basicRoleBoost_100, _R_TOOLTIPS_TEXT.bonus.basicRoleBoost_100, top=10, left=4, right=16),
 _Bonuses.ANY_ADDITIONAL_SKILL: _BonusPreset(_R_SKILLS_IMAGES.new_skill, _R_TOOLTIPS_TEXT.bonus.anyAdditionalSkill),
 _Bonuses.SAME_BLOOD_ZERO_SKILL: _BonusPreset(_R_SKILLS_IMAGES.offspring_brotherhood, _R_TOOLTIPS_TEXT.bonus.sameBloodZeroSkill)}

class CrewBundleTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(CrewBundleTooltipData, self).__init__(context, TOOLTIP_TYPE.CREW_BUNDLE)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setWidth(364)

    def _packBlocks(self, *args, **kwargs):
        bundleName = args[0]
        if bundleName not in _BUNDLE_PRESETS:
            raise SoftException('Bundle "{}" is not supported.'.format(bundleName))
        return [formatters.packBuildUpBlockData(blocks=self.__packHeaderBlock(bundleName), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL), formatters.packBuildUpBlockData(blocks=self.__packHowToGetBlock(bundleName), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE), formatters.packBuildUpBlockData(blocks=self.__packInfoBlock(_BUNDLE_PRESETS[bundleName]), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL)]

    @staticmethod
    def __packHeaderBlock(bundleName):
        return [formatters.packTextBlockData(text=text_styles.highTitle(backport.text(_R_TOOLTIPS_TEXT.header.dyn(bundleName)()))), formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.crewBundles.dyn(bundleName)()), imgPadding=formatters.packPadding(top=17, left=24))]

    @staticmethod
    def __packHowToGetBlock(bundleName):
        return [formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(_R_TOOLTIPS_TEXT.howToGet())), padding=formatters.packPadding(bottom=4)), formatters.packTextBlockData(text=text_styles.main(backport.text(_R_TOOLTIPS_TEXT.howToGet.dyn(bundleName)())), padding=formatters.packPadding(bottom=7))]

    def __packInfoBlock(self, bonuses):
        return [formatters.packTextBlockData(text=text_styles.titleFont(backport.text(_R_TOOLTIPS_TEXT.bonuses())), padding=formatters.packPadding(bottom=20))] + [ self.__getBonus(_BONUS_PRESETS[bonusId]) for bonusId in bonuses ]

    @staticmethod
    def __getBonus(preset):
        return formatters.packImageTextBlockData(img=backport.image(preset.imageRPath()), imgPadding=formatters.packPadding(preset.top, preset.left, preset.bottom, preset.right), title=text_styles.main(backport.text(preset.textRPath())), padding=formatters.packPadding(bottom=20))
