# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_craft.py
import BigWorld
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.ny.ny_helper_view import NYHelperView
from gui.Scaleform.daapi.view.meta.NYScreenCraftMeta import NYScreenCraftMeta
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from gui.Scaleform.locale.NY import NY
from gui.shared.formatters import text_styles
from helpers import dependency
from items.new_year_types import TOY_TYPES, NATIONAL_SETTINGS, NATIONAL_SETTINGS_IDS_BY_NAME, TOY_TYPES_IDS_BY_NAME
from items.new_year_types import g_cache
from new_year.new_year_sounds import NYSoundEvents
from skeletons.new_year import INewYearUIManager

def toyTypeByIndex(index):
    return None if index == 0 or len(TOY_TYPES) < index else TOY_TYPES[index - 1]


def toyLevelByIndex(index):
    return None if index == 0 else index


def toyNationByIndex(index):
    if index == 2:
        return 'modernWestern'
    elif index == 3:
        return 'traditionalWestern'
    else:
        return None if index == 0 or len(NATIONAL_SETTINGS) < index else NATIONAL_SETTINGS[index - 1]


def indexByToyType(type):
    return 0 if type is None else TOY_TYPES_IDS_BY_NAME.get(type, None) + 1


def indexByToyLevel(level):
    return 0 if level is None else level


def indexByToyNation(nation):
    if nation == 'modernWestern':
        return 2
    elif nation == 'traditionalWestern':
        return 3
    else:
        return 0 if nation is None else NATIONAL_SETTINGS_IDS_BY_NAME.get(nation, None) + 1


def getStyle(isEnabled):
    return text_styles.tutorial if isEnabled else text_styles.main


class NYCraft(NYHelperView, NYScreenCraftMeta):
    newYearUIManager = dependency.descriptor(INewYearUIManager)

    def __init__(self, ctx=None):
        super(NYCraft, self).__init__(ctx)
        self.__toyNation = None
        self.__toyLevel = None
        self.__toyType = None
        return

    def onClose(self):
        self._switchToNYMain(previewAlias=VIEW_ALIAS.LOBBY_NY_CRAFT)

    def _populate(self):
        super(NYCraft, self)._populate()
        self._newYearController.clearCraftedToys()
        selectedToy = self.newYearUIManager.getSelectedCraftToy()
        self.__toyType = selectedToy.get('type', None) if selectedToy else None
        self.__toyLevel = selectedToy.get('level', None) if selectedToy else None
        self.__toyNation = selectedToy.get('nation', None) if selectedToy else None
        initData = {'shardsBtnLabel': NY.CRAFTSCREEN_BUTTONS_SHARDSBTN,
         'craftBtnLabel': NY.CRAFTSCREEN_BUTTONS_CRAFTBTN,
         'title': NY.CRAFTSCREEN_TITLE,
         'shardsDescription': NY.CRAFTSCREEN_DESCRIPTION,
         'toyFragmentCount': BigWorld.wg_getIntegralFormat(self._newYearController.getToyFragments()),
         'nationsBlock': {'title': NY.CRAFTSCREEN_NATIONSLIDER_TITLE,
                          'selectedId': indexByToyNation(self.__toyNation),
                          'typeId': NY_CONSTANTS.NATIONS_SECTION,
                          'tooltips': [NY.CRAFTSCREEN_NATIONSLIDER_TOOLTIP_ANY,
                                       NY.CRAFTSCREEN_NATIONSLIDER_TOOLTIP_SOVIET,
                                       NY.CRAFTSCREEN_NATIONSLIDER_TOOLTIP_MODERNWESTERN,
                                       NY.CRAFTSCREEN_NATIONSLIDER_TOOLTIP_TRADITIONALWESTERN,
                                       NY.CRAFTSCREEN_NATIONSLIDER_TOOLTIP_ASIAN]},
         'typesBlock': {'title': NY.CRAFTSCREEN_TYPESLIDER_TITLE,
                        'selectedId': indexByToyType(self.__toyType),
                        'typeId': NY_CONSTANTS.TYPES_SECTION,
                        'tooltips': [NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_ANY,
                                     NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_TOP,
                                     NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_HANGING,
                                     NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_GARLAND,
                                     NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_GIFT,
                                     NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_SNOWMAN,
                                     NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_HOUSE_DECORATION,
                                     NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_HOUSE_LAMP,
                                     NY.CRAFTSCREEN_TYPESLIDER_TOOLTIP_STREET_GARLAND]},
         'levelsBlock': {'title': NY.CRAFTSCREEN_LEVELSLIDER_TITLE,
                         'selectedId': indexByToyLevel(self.__toyLevel),
                         'typeId': NY_CONSTANTS.LEVELS_SECTION,
                         'tooltips': [NY.CRAFTSCREEN_LEVELSLIDER_TOOLTIP_ANY,
                                      NY.CRAFTSCREEN_LEVELSLIDER_TOOLTIP_1,
                                      NY.CRAFTSCREEN_LEVELSLIDER_TOOLTIP_2,
                                      NY.CRAFTSCREEN_LEVELSLIDER_TOOLTIP_3,
                                      NY.CRAFTSCREEN_LEVELSLIDER_TOOLTIP_4,
                                      NY.CRAFTSCREEN_LEVELSLIDER_TOOLTIP_5]},
         'carouselData': self.__getToysVO()}
        self.as_setInitDataS(initData)
        self.__updatePrice()
        NYSoundEvents.playSound(NYSoundEvents.ON_OPEN_CRAFT)
        NYSoundEvents.setState(NYSoundEvents.STATE_ON_CRAFT)
        self._newYearController.onToyFragmentsChanged += self.__onToyFragmentsChanged
        self._newYearController.onCraftedToysChanged += self.__onCraftedToysChanged
        return

    def __getToysVO(self):
        toys = [ g_cache.toys[toyId] for toyId in self._newYearController.craftedToys ]
        result = []
        for toy in toys:
            result.append({'icon': toy.icon})

        return result

    def __onCraftedToysChanged(self, toyId):
        toy = g_cache.toys[toyId]
        self.as_setCraftS({'icon': toy.icon,
         'id': toyId,
         'level': toy.rank,
         'settings': toy.setting})

    def __updatePrice(self):
        price = self._newYearController.getPriceForCraft(self.__toyType, self.__toyNation, self.__toyLevel)
        fragments = self._newYearController.getToyFragments()
        isCraftEnabled = price <= fragments
        self.as_setPriceS(price, isCraftEnabled)
        self.as_setCraftButtonEnableS(isCraftEnabled)
        self.as_setShardsButtonShineS(not isCraftEnabled)

    def __onToyFragmentsChanged(self, fragmentsCount):
        self.__updatePrice()
        self.as_updateShardsS(BigWorld.wg_getIntegralFormat(fragmentsCount))

    def onFilterChange(self, type, index):
        oldPrice = self._newYearController.getPriceForCraft(self.__toyType, self.__toyNation, self.__toyLevel)
        if type == NY_CONSTANTS.TYPES_SECTION:
            NYSoundEvents.playSound(NYSoundEvents.CRAFT_SELECT_TYPE_OR_LEVEL)
            self.__toyType = toyTypeByIndex(index)
        elif type == NY_CONSTANTS.LEVELS_SECTION:
            NYSoundEvents.playSound(NYSoundEvents.CRAFT_SELECT_TYPE_OR_LEVEL)
            self.__toyLevel = toyLevelByIndex(index)
        elif type == NY_CONSTANTS.NATIONS_SECTION:
            self.__toyNation = toyNationByIndex(index)
            NYSoundEvents.playSound(NYSoundEvents.CRAFT_SELECT_SETTING)
            NYSoundEvents.setBoxSwitch(self.__toyNation)
        newPrice = self._newYearController.getPriceForCraft(self.__toyType, self.__toyNation, self.__toyLevel)
        fragments = self._newYearController.getToyFragments()
        if newPrice > fragments >= oldPrice:
            NYSoundEvents.playSound(NYSoundEvents.CRAFT_COST_SAME)
        if newPrice != oldPrice:
            NYSoundEvents.playSound(NYSoundEvents.CRAFT_COST_INCREASED if newPrice > oldPrice else NYSoundEvents.CRAFT_COST_DECREASED)
        NYSoundEvents.playSound(NYSoundEvents.CRAFT_MACHINE_ANIMATION)
        selectedToy = {'type': self.__toyType,
         'level': self.__toyLevel,
         'nation': self.__toyNation}
        self.newYearUIManager.setSelectedCraftToy(selectedToy)
        self.__updatePrice()

    def onCraft(self):
        NYSoundEvents.playSound(NYSoundEvents.CRAFT_BUTTON_PRESSED_CRAFT)
        self._newYearController.craftToy(self.__toyType, self.__toyNation, self.__toyLevel)

    def onGetShards(self):
        NYSoundEvents.playSound(NYSoundEvents.CRAFT_TO_BREAK)
        self._switchToBreak(previewAlias=VIEW_ALIAS.LOBBY_NY_CRAFT)

    def onToyCreatePlaySound(self, level):
        NYSoundEvents.playSound(NYSoundEvents.CRAFT_TOY_CRAFTED)
        NYSoundEvents.setRTPC(NYSoundEvents.RTPC_TOYS, int(level))

    def _dispose(self):
        NYSoundEvents.playSound(NYSoundEvents.ON_CLOSE_CRAFT)
        self._newYearController.onToyFragmentsChanged -= self.__onToyFragmentsChanged
        self._newYearController.onCraftedToysChanged -= self.__onCraftedToysChanged
        super(NYCraft, self)._dispose()
