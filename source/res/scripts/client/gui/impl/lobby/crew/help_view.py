# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/help_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.help_view_model import HelpViewModel
from gui.impl.gen.view_models.views.lobby.crew.help_slide_view_model import HelpSlideViewModel
from gui.impl.gen.view_models.views.lobby.crew.help_slide_section_view_model import HelpSlideSectionViewModel, SlideSectionSize
from gui.impl.auxiliary.crew_help_config_reader import getHelpViewConfig
from gui.impl.pub import WindowImpl
from base_crew_view import BaseCrewSubView
SLIDE_SIZES = {SlideSectionSize.BIG.value: SlideSectionSize.BIG,
 SlideSectionSize.SMALL.value: SlideSectionSize.SMALL}

class HelpView(BaseCrewSubView):
    __slots__ = ('__navigateFrom',)

    def __init__(self, layoutID=R.views.lobby.crew.HelpView(), navigateFrom=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = HelpViewModel()
        self.__navigateFrom = navigateFrom
        super(HelpView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HelpView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onViewClose),)

    def _onLoading(self, *args, **kwargs):
        super(HelpView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        slidesConfig = getHelpViewConfig()
        with self.viewModel.transaction() as vm:
            slides = vm.getSlides()
            slides.clear()
            for index, slide in enumerate(slidesConfig):
                slideModel = HelpSlideViewModel()
                slideModel.setTitle(slide['title']())
                if self.__navigateFrom and self.__navigateFrom == slide['navigateFrom']:
                    vm.setSelectedSlideIndex(index)
                sections = slideModel.getSections()
                sections.clear()
                for section in slide['sections']:
                    sectionModel = HelpSlideSectionViewModel()
                    sectionModel.setSize(SLIDE_SIZES[section['size']])
                    sectionModel.setImage(section['image']())
                    sectionModel.setDescription(section['description']())
                    sections.addViewModel(sectionModel)

                slides.addViewModel(slideModel)

    def _onViewClose(self):
        self.destroyWindow()


class HelpViewWindow(WindowImpl):

    def __init__(self, navigateFrom=None, parent=None):
        super(HelpViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=HelpView(navigateFrom=navigateFrom), parent=parent)
