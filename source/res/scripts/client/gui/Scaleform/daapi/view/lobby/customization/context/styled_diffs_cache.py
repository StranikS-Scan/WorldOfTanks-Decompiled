# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/context/styled_diffs_cache.py
import typing
from helpers import dependency
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.customization.c11n_items import Style

class StyleDiffsCache(object):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        self.__diffs = {}

    def fini(self):
        self.clearDiffs()

    def saveDiffs(self, style, diffs):
        storage = self.__diffs.setdefault(style.intCD, {})
        for season, diff in diffs.iteritems():
            storage[season] = diff

        storage['is3D'] = style.is3D

    def saveDiff(self, style, season, diff):
        storage = self.__diffs.setdefault(style.intCD, {})
        storage[season] = diff
        storage['is3D'] = style.is3D

    def getDiffs(self, style):
        diffs = {season:self.getDiff(style, season) for season in SeasonType.COMMON_SEASONS}
        return diffs

    def getDiff(self, style, season):
        if style.intCD not in self.__diffs or season not in self.__diffs[style.intCD]:
            currentOutfit = self.__service.getCurrentOutfit(season)
            if currentOutfit.id == style.id:
                return currentOutfit.pack().makeCompDescr()
            return None
        else:
            return self.__diffs[style.intCD][season]

    def clearDiffs(self):
        self.__diffs.clear()

    def clearModeDiffs(self, is3D):
        self.__diffs = {style:storage for style, storage in self.__diffs.items() if storage['is3D'] != is3D}
