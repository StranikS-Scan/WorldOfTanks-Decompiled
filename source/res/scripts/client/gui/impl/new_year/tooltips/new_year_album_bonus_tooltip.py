# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_album_bonus_tooltip.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.tooltips.new_year_album_bonus_tooltip_item_model import NewYearAlbumBonusTooltipItemModel
from gui.impl.gen.view_models.new_year.tooltips.new_year_album_bonus_tooltip_model import NewYearAlbumBonusTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from items.components.ny_constants import TOY_SETTING_IDS_BY_NAME, BONUS_THRESHOLDS
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.gui.shared import IItemsCache

class NewYearAlbumBonusTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__parentsModel',)

    def __init__(self, parentsModel, *args, **kwargs):
        super(NewYearAlbumBonusTooltip, self).__init__(R.views.newYearAlbumBonusTooltip, ViewFlags.VIEW, NewYearAlbumBonusTooltipModel, *args, **kwargs)
        self.__parentsModel = parentsModel

    @property
    def viewModel(self):
        return super(NewYearAlbumBonusTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NewYearAlbumBonusTooltip, self)._initialize()
        settingID = TOY_SETTING_IDS_BY_NAME[self.__parentsModel.getCurrentType()]
        with self.viewModel.transaction() as model:
            atmosphereLevel = NewYearAtmospherePresenter.getLevel()
            model.setLevel(atmosphereLevel)
            count = sum(self._itemsCache.items.festivity.getCollectionDistributions()[settingID])
            model.setCurrentDecorations(count)
            model.setTotalDecorations(self.__parentsModel.getTotalToys())
            selectedIdx = -1
            currBonus = 0
            items = model.table.getItems()
            for idx, bonusInfo in enumerate(_getCollectionBonusLevels(settingID)):
                item = NewYearAlbumBonusTooltipItemModel()
                item.setBonus(bonusInfo[0])
                if count >= bonusInfo[1]:
                    selectedIdx = idx
                    currBonus = bonusInfo[0]
                if len(bonusInfo) > 2:
                    item.setRightValue(bonusInfo[2])
                    item.setLeftValue(bonusInfo[1])
                else:
                    item.setRightValue(bonusInfo[1])
                items.addViewModel(item)

            model.setBonus(currBonus)
            model.table.addSelectedIndex(selectedIdx)
            items.invalidate()


def _getCollectionBonusLevels(collectionID):
    result = []
    levelData = [0, 0]
    for threshold, bonus in BONUS_THRESHOLDS[collectionID]:
        levelData.append(threshold - 1)
        result.append(tuple(levelData))
        levelData = [int(bonus), threshold]

    result.append(levelData)
    return result
