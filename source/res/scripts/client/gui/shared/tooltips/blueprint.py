# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/blueprint.py
import nations
from blueprints.BlueprintTypes import BlueprintTypes
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.NATIONS import NATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData, DynamicBlocksTooltipData
from gui.shared.utils.requesters.blueprints_requester import SPECIAL_BLUEPRINT_LEVEL
from helpers import int2roman, i18n, dependency
from helpers.blueprint_generator import g_blueprintGenerator
from skeletons.gui.game_control import IEarlyAccessController

class BlueprintTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(BlueprintTooltipData, self).__init__(context, TOOLTIP_TYPE.BLUEPRINTS)
        self._setMargins(afterBlock=10, afterSeparator=10)
        self._setContentMargin(top=13, left=18, bottom=18, right=13)
        self._fragmentCD = None
        self._items = None
        return

    def _packBlocks(self, fragmentCD):
        self._fragmentCD = fragmentCD
        self._items = super(BlueprintTooltipData, self)._packBlocks(fragmentCD)
        return self._items

    @staticmethod
    def _getVehicleDescrStr(vehicle):
        if vehicle.isElite:
            vehTypeIcon = icons.makeImageTag(source=RES_ICONS.maps_icons_vehicletypes_elite_all_png(vehicle.type), width=24, height=24, vSpace=-6)
        else:
            vehTypeIcon = icons.makeImageTag(RES_ICONS.maps_icons_vehicletypes_all_png(vehicle.type))
        return text_styles.concatStylesToSingleLine(text_styles.stats(int2roman(vehicle.level)), vehTypeIcon, text_styles.main(vehicle.userName))

    @staticmethod
    def _getUnlockDiscountBlock(percentValue, xpValue, title, showPlus=False):
        if percentValue == 100:
            discountPadding = 8 if showPlus else 19
        elif percentValue < 10:
            discountPadding = 30 if showPlus else 41
        else:
            discountPadding = 19 if showPlus else 30
        percentStr = ''.join(('+' if showPlus else '', str(percentValue), '%'))
        discountValueStr = text_styles.concatStylesToSingleLine(text_styles.bonusLocalText(percentStr), text_styles.main(i18n.makeString(TOOLTIPS.VEHICLE_TEXTDELIMITER_OR).join(('  ', ' '))), text_styles.expText(backport.getIntegralFormat(xpValue)), icons.xpCost())
        blockPadding = -discountPadding - (0 if showPlus else -10)
        imgPadding = -79 - (3 if percentValue < 10 else 0)
        return formatters.packImageTextBlockData(title=text_styles.main(title), desc=discountValueStr, img=backport.image(R.images.gui.maps.icons.blueprints.blueprintScreen.discountShine()), txtGap=-6, imgPadding=formatters.packPadding(top=0, right=imgPadding), txtPadding=formatters.packPadding(left=discountPadding), padding=formatters.packPadding(top=4, left=blockPadding, bottom=-6), blockWidth=300)

    @staticmethod
    def _getImageWithBottomTitleBlock(imagePath, imageTitle, blockPadding=None):
        titleBlock = formatters.packAlignedTextBlockData(text=text_styles.stats(imageTitle), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-5))
        imageBlock = formatters.packImageBlockData(img=imagePath, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        return formatters.packBuildUpBlockData(blocks=[imageBlock, titleBlock], align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, blockWidth=140, padding=blockPadding)

    @staticmethod
    def _getAllianceTextWithIcon(alliance):
        allianceIcon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.blueprints.fragment.conversion.dyn(alliance)()), width=13, height=16)
        return text_styles.concatStylesToSingleLine(allianceIcon, text_styles.stats(backport.text(R.strings.blueprints.conversionView.alliance.name.dyn(alliance)())))

    def _setNationFlagCornerBg(self, nationName):
        flagBlock = formatters.packImageBlockData(img=RES_ICONS.getTooltipFlag(nationName), align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=-13, left=-18, bottom=-87))
        self._items.insert(0, flagBlock)

    def _packConversionFormulaBlock(self, intelRequired, nationRequired, vehicle):
        nationalRequiredOptions, nationalAllianceFragments = self.context.getAllianceNationFragmentsData(vehicle)
        blocks = []
        if intelRequired > self.context.getUniversalCount():
            intelText = text_styles.critical(str(intelRequired))
        else:
            intelText = text_styles.warning(str(intelRequired))
        blocks.append(formatters.packImageTextBlockData(desc=intelText, img=backport.image(R.images.gui.maps.icons.blueprints.fragment.special.intelligence()), imgAtLeft=False, txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, imgPadding=formatters.packPadding(top=4, left=2), padding=formatters.packPadding(top=4)))
        blocks.append(formatters.packImageTextBlockData(desc=text_styles.main(backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.chose())), img=backport.image(R.images.gui.maps.icons.blueprints.blueprintScreen.icPlus()), txtPadding=formatters.packPadding(top=1, left=4), padding=formatters.packPadding(top=3, left=6)))
        for index, (nationId, cost) in enumerate(nationalRequiredOptions.iteritems()):
            nationName = nations.MAP[nationId]
            if cost > nationalAllianceFragments[nationId]:
                nationText = text_styles.critical(backport.getIntegralFormat(cost))
            else:
                nationText = text_styles.warning(backport.getIntegralFormat(cost))
            blocks.append(formatters.packImageTextBlockData(desc=nationText, img=backport.image(R.images.gui.maps.icons.blueprints.fragment.special.dyn(nationName)()), imgAtLeft=False, txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, imgPadding=formatters.packPadding(top=4, left=2), padding=formatters.packPadding(top=4)))
            if index < len(nationalRequiredOptions) - 1:
                blocks.append(formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.library.delimeter()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-4, left=2, right=-2, bottom=4)))

        return formatters.packBuildUpBlockData(blocks=blocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=1, bottom=-15))


class ConvertInfoBlueprintTooltipData(BlueprintTooltipData):

    def __init__(self, context):
        super(ConvertInfoBlueprintTooltipData, self).__init__(context)
        self.__vehicle = None
        self.__blueprintData = None
        return

    def _packBlocks(self, vehicleCD):
        items = super(ConvertInfoBlueprintTooltipData, self)._packBlocks(vehicleCD)
        self.__vehicle, self.__blueprintData, self.__convertibleCount = self.context.getVehicleBlueprintData(vehicleCD)
        titleBlock = formatters.packTextBlockData(text=text_styles.middleTitle(TOOLTIPS.TECHTREEPAGE_BLUEPRINTCONVERTTOOLTIP_HEADER), blockWidth=190)
        description1Block = formatters.packTextBlockData(text=text_styles.main(i18n.makeString(TOOLTIPS.TECHTREEPAGE_BLUEPRINTCONVERTTOOLTIP_BODY, fragCount=text_styles.stats(str(self.__convertibleCount)))), blockWidth=190)
        items.append(formatters.packBuildUpBlockData(blocks=[titleBlock, description1Block], stretchLast=True, padding=formatters.packPadding(1, -1, -10, 0), gap=3))
        return self._items


class VehicleBlueprintTooltipData(BlueprintTooltipData, DynamicBlocksTooltipData):
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)

    def __init__(self, context):
        super(VehicleBlueprintTooltipData, self).__init__(context)
        self._setWidth(420)
        self.__vehicle = None
        self.__blueprintData = None
        self.__texture = None
        self.__allianceName = None
        return

    def isDynamic(self):
        return self.__texture is not None

    def stopUpdates(self):
        super(VehicleBlueprintTooltipData, self).stopUpdates()
        if self.__texture is not None and self.__vehicle is not None:
            g_blueprintGenerator.cancel(vehicleCD=self.__vehicle.intCD)
            self.__texture = None
        return

    def changeVisibility(self, isVisible):
        super(VehicleBlueprintTooltipData, self).changeVisibility(isVisible)
        if not isVisible and self.__texture is not None and self.__vehicle is not None:
            g_blueprintGenerator.cancel(vehicleCD=self.__vehicle.intCD)
            self.__texture = None
        return

    def _packBlocks(self, vehicleCD, isShortForm=False):
        items = super(VehicleBlueprintTooltipData, self)._packBlocks(vehicleCD)
        blueprintData = self.context.getVehicleBlueprintData(vehicleCD)
        if blueprintData is None:
            return []
        else:
            self.__vehicle, self.__blueprintData, _ = blueprintData
            _, _, self.__allianceName = self.context.getFragmentData(vehicleCD)
            if self.__vehicle.isUnlocked:
                self._setWidth(350)
                return [formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.vehicleUnlocked.header())), desc=text_styles.main(backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.vehicleUnlocked.body())), gap=3, padding=formatters.packPadding(top=1, bottom=-10, left=-1, right=12))]
            if self.__vehicle.isEarlyAccess:
                self._setWidth(350)
                if self.__vehicle.intCD in self.__earlyAccessController.getBlockedVehicles():
                    title = text_styles.middleTitle(backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.vehicleIsInEarlyAccessBlocked.header()))
                    desc = text_styles.main(backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.vehicleIsInEarlyAccessBlocked.body()))
                else:
                    title = text_styles.middleTitle(backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.vehicleIsInEarlyAccess.header()))
                    desc = text_styles.main(backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.vehicleIsInEarlyAccess.body()))
                return [formatters.packTitleDescBlock(title=title, desc=desc, gap=3, padding=formatters.packPadding(top=1, bottom=-10, left=-1, right=12))]
            self._setWidth(420)
            self._setNationFlagCornerBg(self.__vehicle.nationName)
            items.append(self.__packTitleBlock(isShortForm))
            if not isShortForm:
                items.append(self.__packBlueprintBlock())
            if self.__blueprintData.filledCount == 0:
                items.append(self.__packBlueprintDescrBlock())
                items.append(self.__packGatherDescrBlock())
                self._items = [formatters.packBuildUpBlockData(items)]
            else:
                items.append(formatters.packTextBlockData(text=text_styles.middleTitle(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_BLUEPRINTFRAGMENTS), padding=formatters.packPadding(bottom=-3)))
                self._items = [formatters.packBuildUpBlockData(blocks=items), self.__packFragmentsInfoBlock()]
                items = []
                if self.__blueprintData.filledCount == self.__blueprintData.totalCount:
                    items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.InformationIcon()), desc=text_styles.main(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_FRAGMENTSCONVERT), imgPadding=formatters.packPadding(top=3), descPadding=formatters.packPadding(left=3), padding=formatters.packPadding(bottom=3)))
                    items.append(self.__packStatusBlock())
                    self._items.append(formatters.packBuildUpBlockData(items, padding=formatters.packPadding(bottom=-7)))
                else:
                    items.append(self.__packGatherDescrBlock())
                    self._items.append(formatters.packBuildUpBlockData(items))
            if self.__blueprintData.filledCount != self.__blueprintData.totalCount:
                intelRequired, nationRequired = self.context.getFragmentConvertData(self.__vehicle.level)
                self._items.append(self._packConversionFormulaBlock(intelRequired, nationRequired, self.__vehicle))
                self._items.append(self.__packStatusBlock())
            return self._items

    def __packTitleBlock(self, isShortForm):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_HEADER), desc=self._getVehicleDescrStr(self.__vehicle), gap=0, descPadding=formatters.packPadding(top=-5, left=1), padding=formatters.packPadding(top=5, bottom=1 if isShortForm else 0))

    def __packBlueprintBlock(self):
        layoutBg = RES_ICONS.getBlueprintTooltipLayout(self.__blueprintData.totalCount)
        numRows, numCols, layout = self.context.getBlueprintLayout(self.__vehicle)
        bottomPadding = -20 if self.__vehicle.level not in SPECIAL_BLUEPRINT_LEVEL else -30
        if self.__blueprintData.filledCount > 0:
            self.__texture = g_blueprintGenerator.generate(vehicleCD=self.__vehicle.intCD, clear=True)
        else:
            self.__texture = None
        return formatters.packBlueprintBlockData(blueprintImg=self.__texture, schemeImg=layoutBg, layout=layout, numCols=numCols, numRows=numRows, width=354, height=274, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-33, bottom=bottomPadding))

    def __packFragmentsInfoBlock(self):
        countBlock = formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_FRAGMENTSACQUIRED), desc=text_styles.concatStylesWithSpace(text_styles.bonusLocalText(str(self.__blueprintData.filledCount)), text_styles.main(' '.join(('/', str(self.__blueprintData.totalCount))))), img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_FRAGMENT_SMALL_VEHICLE, txtPadding=formatters.packPadding(left=11), txtGap=-6, padding=formatters.packPadding(top=4))
        transitionBlock = formatters.packImageBlockData(img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_TOOLTIP_POINTER, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-3, left=24, right=24))
        if self.__blueprintData.filledCount != self.__blueprintData.totalCount:
            discountBlock = self.__packDiscountBlock()
        else:
            discountBlock = self.__packFreeUnlockBlock()
        return formatters.packBuildUpBlockData(blocks=[countBlock, transitionBlock, discountBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(bottom=-7), blockWidth=390)

    def __packDiscountBlock(self):
        percentDiscount, xpDiscount = self.context.getDiscountValues(self.__vehicle)
        return self._getUnlockDiscountBlock(percentDiscount, xpDiscount, TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_RESEARCHDISCOUNT)

    def __packGatherDescrBlock(self):
        titleBlock = formatters.packTextBlockData(text=text_styles.middleTitle(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_GATHERHEADER))
        alliance = self.__allianceName.replace('-', '_')
        description1Block = formatters.packTextBlockData(text=i18n.makeString(text_styles.main(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_GATHERDESCRIPTION1), alliance=self._getAllianceTextWithIcon(alliance), nations=i18n.makeString(backport.text(R.strings.blueprints.conversionView.alliance.nations.dyn(alliance)()))))
        return formatters.packBuildUpBlockData(blocks=[titleBlock, description1Block], gap=3, padding=formatters.packPadding(top=4, bottom=-11))

    def __packStatusBlock(self):
        if self.__blueprintData.filledCount == 0:
            status = text_styles.warning(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_EMPTYSTATUS)
        elif self.__blueprintData.filledCount == self.__blueprintData.totalCount:
            status = text_styles.statInfo(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_COMPLETESTATUS)
        else:
            status = text_styles.statusAttention(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_INCOMPLETESTATUS)
        status = text_styles.alignText(status, 'center')
        return formatters.packTextBlockData(text=status, padding=formatters.packPadding(top=5, bottom=-3))

    @staticmethod
    def __packBlueprintDescrBlock():
        fragmentInfo = formatters.packImageTextBlockData(desc=text_styles.main(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_DESCRIPTIONFIRST), img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_FRAGMENT_SMALL_VEHICLE, txtPadding=formatters.packPadding(top=2, left=21))
        discountInfo = formatters.packImageTextBlockData(desc=text_styles.main(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_DESCRIPTIONSECOND), img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_TOOLTIP_DISCOUNT, txtPadding=formatters.packPadding(top=4, left=21))
        return formatters.packBuildUpBlockData(blocks=[fragmentInfo, discountInfo], gap=5, padding=formatters.packPadding(top=8, bottom=3))

    @staticmethod
    def __packFreeUnlockBlock():
        return formatters.packImageTextBlockData(desc=text_styles.main(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_FREEUNLOCK), img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_TOOLTIP_DISCOUNT, txtPadding=formatters.packPadding(left=2), descLeading=4, padding=formatters.packPadding(top=4, left=-20))


class BlueprintFragmentRandomTooltipData(BlueprintTooltipData):

    def __init__(self, context):
        super(BlueprintFragmentRandomTooltipData, self).__init__(context)
        self._setWidth(390)
        self.__nationName = None
        return

    def _packBlocks(self, fragmentCD):
        super(BlueprintFragmentRandomTooltipData, self)._packBlocks(fragmentCD)
        self.__packRandomFragmentBlocks()
        return self._items

    @staticmethod
    def __packDiscountBlock():
        return formatters.packImageTextBlockData(desc=text_styles.main(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_RANDOM_DISCOUNT), img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_TOOLTIP_DISCOUNT_SMALL, imgPadding=formatters.packPadding(top=2, right=5), padding=formatters.packPadding(left=40))

    def __packRandomFragmentBlocks(self):
        self._items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(self._getHeader()), img=RES_ICONS.getBlueprintFragment('small', 'random'), imgPadding=formatters.packPadding(top=3), txtPadding=formatters.packPadding(left=21)))
        descriptionBlock = formatters.packImageTextBlockData(desc=text_styles.main(self._getDescr()), img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_PLUS, imgPadding=formatters.packPadding(top=0, right=5), padding=formatters.packPadding(left=40))
        self._items.append(formatters.packBuildUpBlockData(blocks=[descriptionBlock, self.__packDiscountBlock()], gap=5, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))

    def _getHeader(self):
        return backport.text(R.strings.tooltips.blueprint.BlueprintFragmentTooltip.random.header())

    def _getDescr(self):
        return backport.text(R.strings.tooltips.blueprint.BlueprintFragmentTooltip.random.description())


class BlueprintFragmentRandomNationalTooltipData(BlueprintTooltipData):

    def __init__(self, context):
        super(BlueprintFragmentRandomNationalTooltipData, self).__init__(context)
        self._setWidth(420)
        self.__nationName = None
        return

    def _packBlocks(self, fragmentCD):
        super(BlueprintFragmentRandomNationalTooltipData, self)._packBlocks(fragmentCD)
        self.__packRandomFragmentBlocks()
        return self._items

    def __packAdditionalInfoBlock(self):
        return formatters.packImageTextBlockData(desc=text_styles.main(backport.text(R.strings.tooltips.blueprint.randomNational.additionalInfo())), img=backport.image(R.images.gui.maps.icons.library.InformationIcon_1()), imgPadding=formatters.packPadding(top=2, right=9, left=4), padding=formatters.packPadding(top=-1, left=40))

    def __packRandomFragmentBlocks(self):
        self._items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.tooltips.blueprint.randomNational.header())), img=backport.image(R.images.gui.maps.icons.blueprints.fragment.small.randomNational()), imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(top=5, left=19), descLeading=-1))
        descriptionBlock = formatters.packImageTextBlockData(desc=text_styles.main(backport.text(R.strings.tooltips.blueprint.randomNational.description())), img=backport.image(R.images.gui.maps.icons.blueprints.plus()), imgPadding=formatters.packPadding(top=0, right=5), padding=formatters.packPadding(left=40))
        self._items.append(formatters.packBuildUpBlockData(blocks=[descriptionBlock, self.__packAdditionalInfoBlock()], gap=3, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-3)))
        self._items.append(formatters.packTextBlockData(text='', padding=formatters.packPadding(bottom=-12)))


class BlueprintFragmentTooltipData(BlueprintTooltipData):

    def __init__(self, context):
        super(BlueprintFragmentTooltipData, self).__init__(context)
        self._setWidth(420)
        self.__nationName = None
        self.__allianceName = None
        return

    def _packBlocks(self, fragmentCD):
        fragmentType, self.__nationName, self.__allianceName = self.context.getFragmentData(fragmentCD)
        super(BlueprintFragmentTooltipData, self)._packBlocks(fragmentCD)
        if fragmentType == BlueprintTypes.VEHICLE:
            self.__packVehicleFragmentBlocks()
        elif fragmentType == BlueprintTypes.NATIONAL:
            self.__packNationalFragmentBlocks()
        elif fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
            self.__packIntelFragmentBlocks()
        return self._items

    @staticmethod
    def __packInStorageBlock(count=0):
        inStorageStr = text_styles.concatStylesWithSpace(text_styles.stats(int(count)), icons.makeImageTag(source=RES_ICONS.MAPS_ICONS_LIBRARY_STORAGE_ICON, width=30, height=24, vSpace=-6), text_styles.main(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_INSTORAGE))
        return formatters.packTextBlockData(text=inStorageStr, padding=formatters.packPadding(left=69, bottom=-2, top=1))

    def __packAdditionalInfoBlock(self):
        alliance = self.__allianceName.replace('-', '_')
        desc = i18n.makeString(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_ADDITIONALINFO, alliance=self._getAllianceTextWithIcon(alliance), nations=i18n.makeString(backport.text(R.strings.blueprints.conversionView.alliance.nations.dyn(alliance)())))
        return formatters.packImageTextBlockData(desc=text_styles.main(desc), img=RES_ICONS.MAPS_ICONS_LIBRARY_INFORMATIONICON_1, imgPadding=formatters.packPadding(top=2, right=9, left=4), padding=formatters.packPadding(left=40))

    def __packIntelFragmentBlocks(self):
        self._items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_INTELFRAGMENT), img=RES_ICONS.getBlueprintFragment('small', 'intelligence'), imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(top=5, left=19)))
        descriptionBlock = formatters.packImageTextBlockData(desc=text_styles.main(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_INTELDESCRIPTION), img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_PLUS, imgPadding=formatters.packPadding(top=0, right=5), padding=formatters.packPadding(left=40))
        self._items.append(formatters.packBuildUpBlockData(blocks=[descriptionBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-4)))
        fragmentsCount = self.context.getUniversalCount()
        self._items.append(self.__packInStorageBlock(fragmentsCount))

    def __packNationalFragmentBlocks(self):
        items = self._items
        self._setNationFlagCornerBg(self.__nationName)
        items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_NATIONALFRAGMENT), img=RES_ICONS.getBlueprintFragment('small', self.__nationName), imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(top=5, left=19), padding=formatters.packPadding(bottom=-8)))
        self._items = [formatters.packBuildUpBlockData(blocks=items)]
        items = self._items
        nation = i18n.makeString(NATIONS.genetiveCase(self.__nationName))
        descriptionBlock = formatters.packImageTextBlockData(desc=text_styles.main(i18n.makeString(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_NATIONALDESCRIPTION, nation=nation)), img=RES_ICONS.MAPS_ICONS_BLUEPRINTS_PLUS, imgPadding=formatters.packPadding(top=0, right=5), padding=formatters.packPadding(left=40))
        items.append(formatters.packBuildUpBlockData(blocks=[descriptionBlock, self.__packAdditionalInfoBlock()], gap=3, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-4)))
        fragmentsCount = self.context.getUniversalCount(self._fragmentCD)
        items.append(self.__packInStorageBlock(fragmentsCount))

    def __packVehicleFragmentBlocks(self):
        vehicle, blueprintData, _ = self.context.getVehicleBlueprintData(self._fragmentCD)
        if blueprintData is None:
            return
        else:
            items = self._items
            self._setNationFlagCornerBg(vehicle.nationName)
            items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_FRAGMENTHEADER), desc=self._getVehicleDescrStr(vehicle), img=RES_ICONS.getBlueprintFragment('small', 'vehicle'), imgPadding=formatters.packPadding(top=3), txtPadding=formatters.packPadding(left=21)))
            self._items = [formatters.packBuildUpBlockData(blocks=items)]
            items = self._items
            percentDiscount, xpDiscount = self.context.getFragmentDiscounts(vehicle)
            items.append(formatters.packBuildUpBlockData(blocks=[self._getUnlockDiscountBlock(percentDiscount, xpDiscount, TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_RESEARCHDISCOUNT, True)], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=67)))
            gatheredInfoStr = text_styles.concatStylesWithSpace(text_styles.stats(int(blueprintData.filledCount)), text_styles.main(' '.join(('/', str(blueprintData.totalCount)))), text_styles.main(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_FRAGMENTGATHERED))
            items.append(formatters.packTextBlockData(text=gatheredInfoStr, padding=formatters.packPadding(left=67)))
            items.append(formatters.packTextBlockData(text=text_styles.main(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_FRAGMENTDESCRIPTION)))
            return


class BlueprintEmptySlotTooltipData(BlueprintTooltipData):

    def __init__(self, context):
        super(BlueprintEmptySlotTooltipData, self).__init__(context)
        self._setWidth(420)
        self.__vehicle = None
        self.__blueprintData = None
        self.__allianceName = None
        return

    def _packBlocks(self, vehicleCD):
        items = super(BlueprintEmptySlotTooltipData, self)._packBlocks(vehicleCD)
        self.__vehicle, self.__blueprintData, _ = self.context.getVehicleBlueprintData(vehicleCD)
        _, _, self.__allianceName = self.context.getFragmentData(vehicleCD)
        items.extend([self.__packTitleBlock(), self.__packDiscountBlock(), self.__packDescriptionBlock()])
        intelRequired, nationRequired = self.context.getFragmentConvertData(self.__vehicle.level)
        items.append(self._packConversionFormulaBlock(intelRequired, nationRequired, self.__vehicle))
        if not self.__blueprintData.canConvert:
            statusStr = text_styles.critical(TOOLTIPS.BLUEPRINT_BLUEPRINTEMPTYSLOT_STATUSNOTENOUGH)
        else:
            statusStr = text_styles.statusAttention(TOOLTIPS.BLUEPRINT_BLUEPRINTEMPTYSLOT_STATUSENOUGH)
        statusStr = text_styles.alignText(statusStr, 'center')
        items.append(formatters.packTextBlockData(text=statusStr, padding=formatters.packPadding(top=5, bottom=-3)))
        return items

    @staticmethod
    def __packTitleBlock():
        return formatters.packTextBlockData(text=text_styles.highTitle(TOOLTIPS.BLUEPRINT_BLUEPRINTEMPTYSLOT_TITLE), padding=formatters.packPadding(top=5, bottom=3))

    def __packDiscountBlock(self):
        fragmentBlock = formatters.packImageBlockData(img=RES_ICONS.getBlueprintFragment('small', 'vehicle'), padding=formatters.packPadding(top=4))
        percentDiscount, xpDiscount = self.context.getFragmentDiscounts(self.__vehicle)
        discountBlock = self._getUnlockDiscountBlock(percentDiscount, xpDiscount, TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTEMPTYSLOTTOOLTIP_RESEARCHDISCOUNT, True)
        return formatters.packBuildUpBlockData(blocks=[fragmentBlock, discountBlock], gap=24, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(bottom=-10), blockWidth=370)

    def __packDescriptionBlock(self):
        alliance = self.__allianceName.replace('-', '_')
        items = [formatters.packTextBlockData(text=text_styles.middleTitle(TOOLTIPS.BLUEPRINT_BLUEPRINTEMPTYSLOT_GATHERHEADER)), formatters.packTextBlockData(text=i18n.makeString(text_styles.main(TOOLTIPS.BLUEPRINT_VEHICLEBLUEPRINTTOOLTIP_GATHERDESCRIPTION1), alliance=self._getAllianceTextWithIcon(alliance), nations=i18n.makeString(backport.text(R.strings.blueprints.conversionView.alliance.nations.dyn(alliance)()))))]
        return formatters.packBuildUpBlockData(blocks=items, gap=3, padding=formatters.packPadding(top=3, bottom=-3))
