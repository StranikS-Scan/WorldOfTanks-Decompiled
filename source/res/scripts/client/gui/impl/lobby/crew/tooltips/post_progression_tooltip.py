# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/post_progression_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.post_progression_tooltip_model import PostProgressionTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache

class PostProgressionTooltip(ViewImpl):
    __slots__ = ('_tankmanID',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanID, *args, **kwargs):
        self._tankmanID = tankmanID
        settings = ViewSettings(R.views.lobby.crew.tooltips.PostProgressionTooltip(), args=args, kwargs=kwargs)
        settings.model = PostProgressionTooltipModel()
        super(PostProgressionTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PostProgressionTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PostProgressionTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        crewBooksCache = crewBooksViewedCache()
        rewardBookId = crewBooksCache.rewardBookId()
        crewBook = first(self._itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.CREW_ITEM.ID(rewardBookId)).values())
        _, progress = divmod(self._itemsCache.items.stats.postProgressionXP, crewBook.getXP())
        tankman = self._itemsCache.items.getTankman(self._tankmanID)
        with self.viewModel.transaction() as vm:
            vm.setBookXp(crewBook.getXP())
            vm.setProgressCurrent(progress)
            vm.setProgressMax(crewBooksViewedCache().xppToConvert())
            vm.setHasWarning(not tankman.isMaxSkillEfficiency)
