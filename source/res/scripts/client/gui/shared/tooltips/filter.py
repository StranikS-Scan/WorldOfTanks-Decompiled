# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/filter.py
import constants
from frameworks.wulf import WindowLayer
from helpers import dependency
from helpers import int2roman
from helpers.i18n import makeString as _ms
from gui import GUI_NATIONS
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.Scaleform import getNationsFilterAssetPath, getVehicleTypeAssetPath
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from skeletons.gui.shared import IItemsCache

class VehicleFilterTooltip(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(VehicleFilterTooltip, self).__init__(ctx, TOOLTIP_TYPE.VEHICLE_FILTER)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(300)
        self._currentVehiclesCount = None
        self._totalVehiclesCount = None
        self._nations = None
        self._vehicleTypes = None
        self._levels = None
        self._rented = None
        self._event = None
        self._specials = None
        return

    def _packBlocks(self, *args):
        container = self.app.containerManager.getContainer(WindowLayer.SUB_VIEW)
        view = container.getView()
        if view.alias == VIEW_ALIAS.LOBBY_HANGAR:
            tankCarousel = view.getComponent(HANGAR_ALIASES.TANK_CAROUSEL)
        elif view.alias == VIEW_ALIAS.LOBBY_MISSIONS:
            currentTab = view.getComponent(QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS)
            tankCarousel = currentTab.getComponent(HANGAR_ALIASES.TANK_CAROUSEL)
        else:
            tankCarousel = None
        if tankCarousel is None:
            return []
        else:
            self.__gatherData(tankCarousel)
            items = [self._packHeaderBlock()]
            if self.__hasBody():
                items.append(self._packBodyBlock())
            if not self._event or not self._rented:
                items.append(self._packHiddenBlock())
            if self._searchNameVehicle:
                items.append(self._packSearchNameVehicle())
            items.append(self._packCounterBlock())
            return items

    def _packSearchNameVehicle(self):
        subBlocks = [self.__getParagraphNameBlock(TANK_CAROUSEL_FILTER.INFOTIP_SEARCHNAMEVEHICLE), self.__packSearchNameVehicle(self._searchNameVehicle)]
        return formatters.packBuildUpBlockData(subBlocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(TANK_CAROUSEL_FILTER.INFOTIP_HEADER_TITLE), padding=formatters.packPadding(top=-5), desc=text_styles.main(TANK_CAROUSEL_FILTER.INFOTIP_HEADER_DESCRIPTION))

    def _packHiddenBlock(self):
        subBlocks = []
        if not self._rented:
            subBlocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TANK_CAROUSEL_FILTER.INFOTIP_RENT), value='', icon=ICON_TEXT_FRAMES.RENTALS, padding=formatters.packPadding(left=-50, top=-3, bottom=-18), nameOffset=20))
        if not self._event:
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_BATTLETYPES_40X40_EVENT, width=22, height=22, vSpace=-8)
            text = text_styles.main(TANK_CAROUSEL_FILTER.INFOTIP_EVENT)
            subBlocks.append(formatters.packTextBlockData(text='{}      {}'.format(icon, text), padding=formatters.packPadding(left=6, top=5, bottom=0)))
        return formatters.packBuildUpBlockData(subBlocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packCounterBlock(self):
        if self._currentVehiclesCount == 0:
            textStyle = text_styles.critical
        else:
            textStyle = text_styles.warning
        return formatters.packTextBlockData(padding=formatters.packPadding(top=1), text=textStyle(_ms(TANK_CAROUSEL_FILTER.INFOTIP_COUNTER, count=self._currentVehiclesCount, total=self._totalVehiclesCount)))

    def _packBodyBlock(self):
        subBlocks = []
        if self._nations:
            subBlocks.append(self.__getParagraphNameBlock(TANK_CAROUSEL_FILTER.INFOTIP_NATIONS))
            subBlocks.append(self.__packNationsListBlock())
        if self._vehicleTypes:
            subBlocks.append(self.__getParagraphNameBlock(TANK_CAROUSEL_FILTER.INFOTIP_VEHICLETYPES))
            subBlocks.append(self.__packTypesListBlock())
        if self._levels and len(self._levels) < len(VEHICLE_LEVELS):
            subBlocks.append(self.__getParagraphNameBlock(TANK_CAROUSEL_FILTER.INFOTIP_LEVELS))
            subBlocks.append(self.__packLevelBlock())
        if any(self._specials.values()):
            subBlocks.append(self.__getParagraphNameBlock(TANK_CAROUSEL_FILTER.INFOTIP_ONLY))
            subBlocks.append(self.__packSpecialTypeBlock())
        return formatters.packBuildUpBlockData(subBlocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(top=-5, bottom=-5))

    def __getParagraphNameBlock(self, name):
        return formatters.packTextBlockData(text=text_styles.standard(name), padding=formatters.packPadding(bottom=6))

    def __packNationsListBlock(self):
        return formatters.packImageListParameterBlockData(listIconSrc=[ formatters.packImageListIconData(getNationsFilterAssetPath(n)) for n in self._nations ], columnWidth=32, rowHeight=20, padding=formatters.packPadding(left=15, bottom=8))

    def __packTypesListBlock(self):
        return formatters.packImageListParameterBlockData(listIconSrc=[ formatters.packImageListIconData(getVehicleTypeAssetPath(v)) for v in self._vehicleTypes ], columnWidth=27, rowHeight=20, padding=formatters.packPadding(bottom=8, left=7))

    def __packLevelBlock(self):
        string = ', '.join((int2roman(level) for level in self._levels))
        return formatters.packTextBlockData(text=text_styles.stats(string), padding=formatters.packPadding(bottom=8, top=-5, left=15))

    def __packSpecialTypeBlock(self):
        string = ''
        addComma = lambda str: '{0}, '.format(str) if str else str
        if self._specials['premium']:
            string += _ms(TANK_CAROUSEL_FILTER.INFOTIP_ONLY_PREMIUM)
        if self._specials['elite']:
            string = addComma(string)
            string += _ms(TANK_CAROUSEL_FILTER.INFOTIP_ONLY_ELITE)
        if self._specials['favorite']:
            string = addComma(string)
            string += _ms(TANK_CAROUSEL_FILTER.INFOTIP_ONLY_FAVORITE)
        if self._specials['bonus']:
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_MULTYXP)
            xpRate = text_styles.stats('x{0}'.format(self.itemsCache.items.shop.dailyXPFactor))
            string = addComma(string)
            string += '{0}{1}'.format(icon, xpRate)
        if self._specials['igr']:
            string = addComma(string)
            string += icons.premiumIgrSmall()
        return formatters.packTextBlockData(text=text_styles.main(string), padding=formatters.packPadding(top=-5, bottom=5, left=15))

    def __packSearchNameVehicle(self, text):
        return formatters.packTextBlockData(text=text_styles.main(text), padding=formatters.packPadding(top=-5, bottom=5, left=15))

    def __gatherData(self, tankCarousel):
        filters = tankCarousel.filter.getFilters()
        self._currentVehiclesCount = tankCarousel.getCurrentVehiclesCount()
        self._totalVehiclesCount = tankCarousel.getTotalVehiclesCount()
        self._nations = [ nation for nation in GUI_NATIONS if filters[nation] ]
        self._vehicleTypes = [ vehType for vehType in VEHICLE_TYPES_ORDER if filters[vehType] ]
        self._levels = []
        for level in VEHICLE_LEVELS:
            if filters['level_%d' % level]:
                self._levels.append(level)

        self._rented = filters['rented']
        self._event = filters['event']
        self._searchNameVehicle = filters['searchNameVehicle']
        self._specials = {'premium': filters['premium'],
         'elite': filters['elite'],
         'igr': filters['igr'] if constants.IS_KOREA else False,
         'bonus': filters['bonus'],
         'favorite': filters['favorite']}

    def __hasBody(self):
        return bool(self._nations) or bool(self._vehicleTypes) or bool(self._levels and len(self._levels)) or any(self._specials.values())
