# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/new_year.py
import BigWorld
from gui import GUI_NATIONS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.NATIONS import NATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import NyDecorationTooltipData, BlocksTooltipData, TOOLTIP_SETTINGS_ICON_BY_NATION_ID
from gui.shared.tooltips.personal_missions import TankwomanTooltipData
from gui.Scaleform.locale.NY import NY
from gui.shared.formatters import text_styles, icons
from helpers import dependency, int2roman
from items.new_year_types import NATIONAL_SETTINGS_IDS_BY_NAME, NATIONS_BY_SETTING
from skeletons.new_year import INewYearController
from helpers.i18n import makeString as _ms
from items.new_year_types import BOUND_COLLECTION_RATING_BY_LEVEL, COLLECTION_BONUSES_BY_LEVEL
from items.new_year_types import _BONUS_FACTOR_BY_ATMOSPHERE_LEVEL

def _makeNationBlock(header, setting):
    nationsBlock = [formatters.packTextBlockData(text=text_styles.middleTitle(header))]
    nations_by_setting = NATIONS_BY_SETTING[setting]
    nations_by_setting = sorted(nations_by_setting, key=lambda nation: GUI_NATIONS.index(nation))
    for nation in nations_by_setting:
        nationsBlock.append(formatters.packImageTextBlockData(img='../maps/icons/filters/nations/%s.png' % nation, title=text_styles.main(NATIONS.all(nation)), imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=6, top=2), padding=formatters.packPadding(left=3, bottom=2)))

    return nationsBlock


class TankwomanNYTooltipData(TankwomanTooltipData):

    def _getConditions(self):
        return text_styles.main(NY.TOOLTIP_TANKMEN)


class NyDecorationWithStatusTooltipData(NyDecorationTooltipData):

    def _packBlocks(self, *args, **kwargs):
        self.__isReceived = bool(args[1])
        items = super(NyDecorationWithStatusTooltipData, self)._packBlocks(*args, **kwargs)
        if self.__isReceived:
            statusText = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_NY_ICONS_CHECK, width=24, height=24, vSpace=-6, hSpace=-2), text_styles.statInfo(NY.COLLECTIONS_TOOLTIP_DECORATION_OBTAINED))
            statusPadding = formatters.packPadding(left=4, top=-12, bottom=-14)
        else:
            statusText = text_styles.concatStylesWithSpace(text_styles.critical(NY.COLLECTIONS_TOOLTIP_DECORATION_NOTOBTAINED))
            statusPadding = formatters.packPadding(left=16, top=-8, bottom=-10)
        bottomBuildUpBlock = [formatters.packAlignedTextBlockData(text=statusText, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=statusPadding)]
        items.append(formatters.packBuildUpBlockData(bottomBuildUpBlock))
        return items

    def _canShowDescription(self):
        return self.__isReceived and super(NyDecorationWithStatusTooltipData, self)._canShowDescription()

    def _getIcon(self, toyDescr):
        return RES_ICONS.getNyDecorationTooltipIcon(toyDescr.type)

    def _packHeaderBlock(self):
        block = super(NyDecorationWithStatusTooltipData, self)._packHeaderBlock()
        block['data']['level'] = int2roman(self._level)
        return block

    def _packBottomBlock(self):
        return formatters.packBuildUpBlockData(self.__packReceivedDescBlock() if self.__isReceived else self.__packNotReceivedDescBlock(), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=5, bottom=-20))

    def __packReceivedDescBlock(self):
        return [formatters.packTextBlockData(text=text_styles.middleTitle(NY.COLLECTIONS_TOOLTIP_DECORATIONS_INFO_TIPS_TITLE)), formatters.packTextBlockData(text=text_styles.main(_ms(NY.COLLECTIONS_TOOLTIP_DECORATIONS_INFO_TIPS_TEXT, text=text_styles.neutral(NY.COLLECTIONS_TOOLTIP_DECORATIONS_INFO_TIPS_STAYINCOLLECTION))))]

    def __packNotReceivedDescBlock(self):
        return [formatters.packTextBlockData(text=text_styles.middleTitle(NY.COLLECTIONS_TOOLTIP_DECORATIONS_INFO_HOWTO_TITLE)),
         formatters.packTextBlockData(text=text_styles.main(NY.COLLECTIONS_TOOLTIP_DECORATIONS_INFO_HOWTO_TEXT)),
         formatters.packTextBlockData(text=text_styles.middleTitle(NY.COLLECTIONS_TOOLTIP_DECORATIONS_INFO_BONUS_TITLE), padding=formatters.packPadding(top=20)),
         formatters.packTextBlockData(text=text_styles.main(NY.COLLECTIONS_TOOLTIP_DECORATIONS_INFO_BONUS_TEXT))]


class NYCollectionAbstractTooltipData(BlocksTooltipData):
    _newYearController = dependency.descriptor(INewYearController)

    def __init__(self, context):
        super(NYCollectionAbstractTooltipData, self).__init__(context, TOOLTIP_TYPE.NY)
        self._setContentMargin(top=20, left=15, bottom=20, right=15)
        self._setMargins(afterBlock=20, afterSeparator=20)
        self._setWidth(364)

    def _packBlocks(self, *args, **kwargs):
        setting = str(args[0])
        return self._buildBlocks(setting)

    def _buildBlocks(self, setting):
        return []


class NYCollectionProgressBarTooltipData(NYCollectionAbstractTooltipData):

    def _buildBlocks(self, setting):
        collection = _ms(NY.collections_tooltip_progressbar_awards_writings_descr_collection(setting))
        styleTitle = _ms(NY.COLLECTIONS_TOOLTIP_PROGRESSBAR_AWARDS_STYLE_TITLE, style=_ms(VEHICLE_CUSTOMIZATION.getStyleName(setting)))
        headerBlock = [formatters.packTextBlockData(text_styles.highTitle(NY.COLLECTIONS_TOOLTIP_PROGRESSBAR_HEADER_TITLE), useHtml=True, padding=formatters.packPadding(bottom=5)),
         self.__makeAwardBlock(RES_ICONS.MAPS_ICONS_NY_REWARDS_NY_STYLE, styleTitle, _ms(NY.COLLECTIONS_TOOLTIP_PROGRESSBAR_AWARDS_STYLE_DESCRIPTION), setting),
         self.__makeAwardBlock(RES_ICONS.MAPS_ICONS_NY_REWARDS_INSCRIPTIONS, NY.collections_tooltip_progressbar_awards_writings_title, _ms(NY.COLLECTIONS_TOOLTIP_PROGRESSBAR_AWARDS_WRITINGS_DESCR, collection=collection), setting),
         self.__makeAwardBlock(RES_ICONS.MAPS_ICONS_NY_REWARDS_EMBLEM, NY.collections_tooltip_progressbar_awards_emblems_title, _ms(NY.COLLECTIONS_TOOLTIP_PROGRESSBAR_AWARDS_EMBLEMS_DESCR, collection=collection), setting)]
        return [formatters.packBuildUpBlockData(headerBlock, padding=formatters.packPadding(left=5)), formatters.packBuildUpBlockData(_makeNationBlock(NY.COLLECTIONS_TOOLTIP_NATIONS_HEADER, setting), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=5))]

    def __makeAwardBlock(self, icon, titleEnumFunc, descr, setting):
        title = titleEnumFunc(setting) if callable(titleEnumFunc) else titleEnumFunc
        return formatters.packImageTextBlockData(img=icon, title=text_styles.stats(title), desc=text_styles.standard(descr), imgPadding=formatters.packPadding(left=3, top=-10), txtPadding=formatters.packPadding(left=15), padding=formatters.packPadding(top=16))


class NYHangarCollectionBonusInfoTooltipData(NYCollectionAbstractTooltipData):

    def _buildBlocks(self, setting):
        nyLevelMax = 10
        nationId = NATIONAL_SETTINGS_IDS_BY_NAME[setting]
        settingsIcon = TOOLTIP_SETTINGS_ICON_BY_NATION_ID[nationId]
        bonuses = self._newYearController.getBonusesForSetting(NATIONAL_SETTINGS_IDS_BY_NAME[setting])
        nyLevel, _, nyProgress, nyBound = self._newYearController.getProgress()
        currentLevel = self._newYearController.getCollectionLevelForNation(nationId)
        nextLevel = currentLevel + 1 if currentLevel < len(BOUND_COLLECTION_RATING_BY_LEVEL) else len(BOUND_COLLECTION_RATING_BY_LEVEL)
        currentRating = self._newYearController.getCollectionRatingForNation(nationId)
        nextRating = BOUND_COLLECTION_RATING_BY_LEVEL[nextLevel - 1]
        decorationsAmount = nextRating - currentRating if nextRating > currentRating else 0
        bonusValue = self._newYearController.calculateBonusesForCollectionLevel(nextLevel)[0] * 100
        headerBlock = [formatters.packImageTextBlockData(img=settingsIcon, title=text_styles.highTitle(NY.collections_tooltip_bonusinfo_header(setting)), desc=text_styles.standard(_ms(NY.COLLECTIONS_TOOLTIP_BONUSINFO_DESCR)), imgPadding=formatters.packPadding(left=4, top=-3), txtGap=-2, txtOffset=65, padding=formatters.packPadding(top=0, bottom=16)),
         self.__makeBonusBlock(bonuses[0], RES_ICONS.MAPS_ICONS_NY_ICONS_ICON_BUTTONS_ADD_EXP, NY.COLLECTIONS_TOOLTIP_BONUSINFO_BONUSES_VEHICLE),
         self.__makeBonusBlock(bonuses[3], RES_ICONS.MAPS_ICONS_NY_ICONS_ICON_BUTTONS_ADD_CREDITS, NY.COLLECTIONS_TOOLTIP_BONUSINFO_BONUSES_CREDITS),
         self.__makeBonusBlock(bonuses[1], RES_ICONS.MAPS_ICONS_NY_ICONS_ICON_BUTTONS_ADD_EXP_CREW, NY.COLLECTIONS_TOOLTIP_BONUSINFO_BONUSES_CREW)]
        bottomBlock = list()
        bottomBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(NY.COLLECTIONS_TOOLTIP_BONUSINFO_BOTTOM_HEADER)))
        gotDecorations = decorationsAmount > 0
        if gotDecorations:
            bottomBlock.append(formatters.packTextBlockData(text=text_styles.main(_ms(NY.COLLECTIONS_TOOLTIP_BONUSINFO_BOTTOM_LINE1, bonus=bonusValue, count=text_styles.neutral(_ms(NY.COLLECTIONS_TOOLTIP_BONUSINFO_BOTTOM_DECORATIONS, count=decorationsAmount))))))
        reachedMaxLevel = nyLevel >= nyLevelMax
        if not reachedMaxLevel:
            bottomBlock.append(formatters.packTextBlockData(text=text_styles.main(_ms(NY.COLLECTIONS_TOOLTIP_BONUSINFO_BOTTOM_LINE2, level=nyLevel))))
        items = list()
        items.append(formatters.packBuildUpBlockData(headerBlock))
        items.append(formatters.packBuildUpBlockData(_makeNationBlock(NY.COLLECTIONS_TOOLTIP_BONUSINFO_NATIONS_HEADER, setting), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=65)))
        if gotDecorations or not reachedMaxLevel:
            items.append(formatters.packBuildUpBlockData(bottomBlock, padding=formatters.packPadding(left=65)))
        return items

    def __makeBonusBlock(self, bonus, icon, desc):
        return formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(desc), value=text_styles.stats('+%d%%' % (bonus * 100) if bonus > 0 else '0%'), icon=icon, titlePadding=formatters.packPadding(left=3), iconPadding=formatters.packPadding(left=17, top=-1), padding=formatters.packPadding(left=47))


class NYCollectionBonusInfoTooltipData(BlocksTooltipData):
    _newYearController = dependency.descriptor(INewYearController)

    def __init__(self, context):
        super(NYCollectionBonusInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.NY)
        self._setContentMargin(top=20, left=0, bottom=20, right=0)
        self._setMargins(afterBlock=20, afterSeparator=20)
        self._setWidth(364)

    def _packBlocks(self, *args, **kwargs):
        setting = str(args[0])
        return self._buildBlocks(setting)

    def _buildBlocks(self, setting):
        nyLevel, _, _, _ = self._newYearController.getProgress()
        nationId = NATIONAL_SETTINGS_IDS_BY_NAME[setting]
        collectionLevel = self._newYearController.getCollectionLevelForNation(nationId)
        bonus = COLLECTION_BONUSES_BY_LEVEL[collectionLevel - 1].xp
        calculatingLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_NY_COLLECTION_BONUS_CALCULATING_LINKAGE
        calculatingData = {'celebrationTitle': NY.COLLECTIONS_TOOLTIP_BONUS_CELEBRATION_LEVEL_TITLE,
         'celebrationValue': str(nyLevel),
         'bonusTitle': NY.COLLECTIONS_TOOLTIP_BONUS_CELEBRATION_TITLE,
         'bonusValue': '{}%'.format(BigWorld.wg_getNiceNumberFormat(bonus * 100.0))}
        headerBlock = [formatters.packTextBlockData(text_styles.highTitle(NY.COLLECTIONS_TOOLTIP_BONUSINFO), useHtml=True, padding=formatters.packPadding(left=8, top=-5, bottom=12)), formatters.packBlockDataItem(calculatingLinkage, calculatingData, padding=formatters.packPadding(left=12, bottom=-11))]
        countSign = text_styles.neutral(_ms(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_TABLE_TOYS_HEADER_COUNT))
        countSign = text_styles.standard(_ms(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_TABLE_VALUE_SIGN, value=countSign))
        leftColumnHeader = _ms(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_TABLE_TOYS_HEADER, sign=countSign)
        rewardSign = text_styles.neutral(_ms(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_TABLE_REWARD_VALUE))
        rewardSign = text_styles.standard(_ms(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_TABLE_VALUE_SIGN, value=rewardSign))
        rightColumnHeader = _ms(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_TABLE_REWARD_HEADER, sign=rewardSign)
        leftValues = []
        rightValues = []
        for i in range(0, len(BOUND_COLLECTION_RATING_BY_LEVEL) - 1):
            leftValues.append(_ms(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_TABLE_TOYS_VALUES, min=BOUND_COLLECTION_RATING_BY_LEVEL[i], max=BOUND_COLLECTION_RATING_BY_LEVEL[i + 1] - 1))

        leftValues.append(_ms(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_TABLE_TOYS_MORE, count=BOUND_COLLECTION_RATING_BY_LEVEL[len(BOUND_COLLECTION_RATING_BY_LEVEL) - 1]))
        for bonus in COLLECTION_BONUSES_BY_LEVEL:
            rightValues.append(BigWorld.wg_getNiceNumberFormat(bonus.xp * 100.0))

        tableData = {'leftColumn': {'header': leftColumnHeader,
                        'values': leftValues},
         'rightColumn': {'header': rightColumnHeader,
                         'values': rightValues},
         'selectedIndex': collectionLevel - 1}
        receivedCount = 0
        totalCount = 0
        alreadyReceived = self._newYearController.receivedToysCollection
        toys = self._newYearController.toysDescrs
        toysBySetting = []
        for toy in toys.values():
            if toy.setting == setting:
                totalCount += 1
                received = toy.id in alreadyReceived
                if received:
                    receivedCount += 1
                toysBySetting.append(toy)

        progress = text_styles.main(_ms(NY.COLLECTIONS_TOOLTIP_BONUS_TOYS, value=text_styles.stats(str(receivedCount)), max=totalCount))
        middleBlock = [formatters.packTextBlockData(text_styles.middleTitle(NY.COLLECTIONS_TOOLTIP_BONUS_INFO_HEADER), useHtml=True, padding=formatters.packPadding(top=5, bottom=9, left=25)), formatters.packBlockDataItem(BLOCKS_TOOLTIP_TYPES.TOOLTIP_NY_COLLECTION_BONUS_TABLE_LINKAGE, tableData), formatters.packAlignedTextBlockData(text=progress, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=20))]
        permanentBonus = BigWorld.wg_getNiceNumberFormat(_BONUS_FACTOR_BY_ATMOSPHERE_LEVEL[-1])
        description = text_styles.main(_ms(NY.COLLECTIONS_TOOLTIP_BONUSINFO_BOTTOM_DESCRIPTION, value=text_styles.neutral(permanentBonus)))
        bottomBlock = _makeNationBlock(NY.COLLECTIONS_TOOLTIP_AWARDS_NATIONS_HEADER, setting)
        bottomBlock.append(formatters.packAlignedTextBlockData(text=description, align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=10)))
        return [formatters.packBuildUpBlockData(headerBlock, padding=formatters.packPadding(left=15, right=15)), formatters.packBuildUpBlockData(middleBlock, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=0)), formatters.packBuildUpBlockData(bottomBlock, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding=formatters.packPadding(left=25))]
