# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/catalog/catalog_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.achievement_card_model import AchievementCardModel
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.breadcrumb_model import BreadcrumbModel
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.details_model import DetailsModel

class CatalogViewModel(ViewModel):
    __slots__ = ('onClose', 'onBreadcrumbClick', 'onCatalogClick', 'onCardClick', 'onStylePreview', 'onDogTagPreview', 'onPurchaseVehicleClick', 'onHintClose', 'onCardHover')

    def __init__(self, properties=6, commands=9):
        super(CatalogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def details(self):
        return self._getViewModel(0)

    @staticmethod
    def getDetailsType():
        return DetailsModel

    def getBreadcrumbs(self):
        return self._getArray(1)

    def setBreadcrumbs(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBreadcrumbsType():
        return BreadcrumbModel

    def getAchievementScore(self):
        return self._getNumber(2)

    def setAchievementScore(self, value):
        self._setNumber(2, value)

    def getMaxAchievementsScore(self):
        return self._getNumber(3)

    def setMaxAchievementsScore(self, value):
        self._setNumber(3, value)

    def getIsNeededShowHint(self):
        return self._getBool(4)

    def setIsNeededShowHint(self, value):
        self._setBool(4, value)

    def getAchievementsList(self):
        return self._getArray(5)

    def setAchievementsList(self, value):
        self._setArray(5, value)

    @staticmethod
    def getAchievementsListType():
        return AchievementCardModel

    def _initialize(self):
        super(CatalogViewModel, self)._initialize()
        self._addViewModelProperty('details', DetailsModel())
        self._addArrayProperty('breadcrumbs', Array())
        self._addNumberProperty('achievementScore', 0)
        self._addNumberProperty('maxAchievementsScore', 0)
        self._addBoolProperty('isNeededShowHint', False)
        self._addArrayProperty('achievementsList', Array())
        self.onClose = self._addCommand('onClose')
        self.onBreadcrumbClick = self._addCommand('onBreadcrumbClick')
        self.onCatalogClick = self._addCommand('onCatalogClick')
        self.onCardClick = self._addCommand('onCardClick')
        self.onStylePreview = self._addCommand('onStylePreview')
        self.onDogTagPreview = self._addCommand('onDogTagPreview')
        self.onPurchaseVehicleClick = self._addCommand('onPurchaseVehicleClick')
        self.onHintClose = self._addCommand('onHintClose')
        self.onCardHover = self._addCommand('onCardHover')
