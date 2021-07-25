# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/title_convert_books_tooltip_view.py
from crew2.crew2_consts import XP_TRASH_LIMIT
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.title_convert_books_tooltip_model import TitleConvertBooksTooltipModel
from gui.impl.pub import ViewImpl
from helpers.dependency import descriptor
from skeletons.gui.shared import IItemsCache
_VERSION_UPDATER_TOKEN_PREFIX = 'token:crew_conversion:crewBooks'
_VERSION_UPDATER_PERSONAL_CREW_BOOK_PREFIX = 'personalCrewBook'
_VERSION_UPDATER_TRASH_TANKMEN_PREFIX = 'trashTankmen'
_VERSION_UPDATER_TANKMEN_TOKEN_PREFIX = 'tankmenToken'
_UNIVERSAL_BOOK_CD = 15646

class TitleConvertBooksTooltipView(ViewImpl):
    __itemsCache = descriptor(IItemsCache)

    def __init__(self, showPersonal=True, showNation=True):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.TitleConvertBooksTooltip())
        settings.model = TitleConvertBooksTooltipModel()
        super(TitleConvertBooksTooltipView, self).__init__(settings)
        self._showPersonal = showPersonal
        self._showNation = showNation

    @property
    def viewModel(self):
        return super(TitleConvertBooksTooltipView, self).getViewModel()

    def _onLoading(self):
        super(TitleConvertBooksTooltipView, self)._onLoading()
        self.__updatePersonalInfo()

    def __updatePersonalInfo(self):
        with self.viewModel.transaction() as vm:
            vm.setExpCount(XP_TRASH_LIMIT)
            vm.setShowPersonal(self._showPersonal)
            vm.setShowNation(self._showNation)
            if self._showPersonal:
                vm.setBooksCount(self.__countCrewBookTokens(_VERSION_UPDATER_PERSONAL_CREW_BOOK_PREFIX))
            if self._showNation:
                vm.setRecruitsCount(self.__countCrewBookTokens(_VERSION_UPDATER_TRASH_TANKMEN_PREFIX) + self.__countCrewBookTokens(_VERSION_UPDATER_TANKMEN_TOKEN_PREFIX))

    def __countCrewBookTokens(self, reasonPrefix):
        return sum((v[1] for k, v in self.__itemsCache.items.tokens.getTokens().iteritems() if '{}:{}'.format(_VERSION_UPDATER_TOKEN_PREFIX, reasonPrefix) in k))
