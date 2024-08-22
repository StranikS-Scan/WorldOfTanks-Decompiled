# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/conversion_awards_view.py
import SoundGroups
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.awards_view_model import AwardsViewModel
from gui.impl.lobby.crew.base_crew_view import BaseCrewSubView
from gui.impl.lobby.crew.tooltips.conversion_tooltip import ConversionTooltip
from gui.impl.lobby.crew.utils import packCompensationData
from gui.impl.pub import WindowImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from crew_sounds import SOUNDS

class ConversionAwardsView(BaseCrewSubView):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__conversionResult', '__tooltipData')

    def __init__(self, layoutID=R.views.lobby.common.AwardsView(), *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=AwardsViewModel(), args=args, kwargs=kwargs)
        self.__conversionResult = kwargs.get('conversionResults')
        self.__tooltipData = {}
        super(ConversionAwardsView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.ConversionTooltip():
            tooltipId = event.getArgument('tooltipId')
            books = self.__tooltipData[tooltipId] if tooltipId in self.__tooltipData else []
            return ConversionTooltip(books, title=R.strings.tooltips.conversion.received.header(), description=R.strings.tooltips.conversion.received.body())
        return super(ConversionAwardsView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(ConversionAwardsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ConversionAwardsView, self)._onLoading(*args, **kwargs)
        locales = R.strings.crew.conversionAwards
        with self.viewModel.transaction() as tx:
            tx.setBackground(R.images.gui.maps.icons.windows.background())
            tx.setTitle(locales.title())
            tx.setUnderTitle(locales.underTitle())
            tx.setBottomNote(locales.buttonNote())
            tx.setButtonTitle(locales.button.submit())
            packCompensationData(self.__conversionResult, tx.mainRewards, self.__tooltipData)

    def _onLoaded(self, *args, **kwargs):
        super(ConversionAwardsView, self)._onLoaded(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(SOUNDS.CONVERSION_AWARD)

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _onClose(self, *_):
        self.destroyWindow()

    def __onDisconnected(self):
        self._onClose()


class ConversionAwardsWindow(WindowImpl):

    def __init__(self, **kwargs):
        super(ConversionAwardsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=ConversionAwardsView(**kwargs))
