# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_post_progression_view.py
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.crew_post_progression_view_model import CrewPostProgressionViewModel, PauseReasonType
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import decorators
from gui.shared.gui_items.processors.common import ClaimRewardForPostProgression
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from items.components.crew_books_constants import CREW_BOOK_RARITY
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from crew_sounds import CREW_SOUND_OVERLAY_SPACE
from PlayerEvents import g_playerEvents

class CrewPostProgressionView(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    gui = dependency.descriptor(IGuiLoader)
    _COMMON_SOUND_SPACE = CREW_SOUND_OVERLAY_SPACE

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.crew.CrewPostProgressionView(), flags=ViewFlags.VIEW, model=CrewPostProgressionViewModel(), args=args, kwargs=kwargs)
        super(CrewPostProgressionView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrewPostProgressionView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrewPostProgressionView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setTitle(R.strings.crew_books.items.universalGuide.Name())
            vm.setDescription(backport.text(R.strings.crew_books.tooltip.universalGuide.mainText(), xp=self.__amountXpForBook()))
            vm.setIcon(R.images.gui.maps.icons.crewBooks.books.s600x450.universalGuide())
            self.__updateCountAndProgression(vm)
            self.__setPause(vm)

    def _getEvents(self):
        return ((self.viewModel.onClaim, self.__onClaim), (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _getCallbacks(self):
        return (('stats.XPpp', self.__onUpdateXpp),)

    def __amountXpForBook(self):
        return self.__itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.CREW_ITEM.BOOK_RARITIES(CREW_BOOK_RARITY.UNIVERSAL_GUIDE)).values()[0].getXP()

    def __setPause(self, vm):
        tmen = self.__itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.IS_POST_PROGRESSION_AVAILABLE | REQ_CRITERIA.TANKMAN.ACTIVE).values()
        tmenWithLowEfficiency = filter(REQ_CRITERIA.TANKMAN.IS_LOW_EFFICIENCY, tmen)
        reason = PauseReasonType.NONE
        if not tmen:
            reason = PauseReasonType.RETIRE
        elif len(tmen) == len(tmenWithLowEfficiency):
            reason = PauseReasonType.LOWEFFICIENCY
        vm.setPauseReason(reason)

    def __onUpdateXpp(self, *args):
        with self.viewModel.transaction() as vm:
            self.__updateCountAndProgression(vm)

    def __updateCountAndProgression(self, vm):
        count, progress = divmod(self.__itemsCache.items.stats.postProgressionXP, self.__amountXpForBook())
        vm.setCount(count)
        vm.setProgressCurrent(progress)
        vm.setProgressMax(crewBooksViewedCache().xppToConvert())

    @decorators.adisp_process('updating')
    def __onClaim(self):
        processor = ClaimRewardForPostProgression(crewBooksViewedCache().xppToConvert())
        result = yield processor.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, messageData=result.auxData)

    def __onDisconnected(self):
        self.destroyWindow()


class CrewPostProgressionWindow(WindowImpl):

    def __init__(self, parent=None):
        super(CrewPostProgressionWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=CrewPostProgressionView(), parent=parent)
