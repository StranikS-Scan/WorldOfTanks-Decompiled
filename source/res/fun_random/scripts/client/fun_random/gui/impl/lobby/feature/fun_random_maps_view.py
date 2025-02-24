# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_maps_view.py
import typing
import ArenaType
from account_helpers.AccountSettings import FunRandomMaps
from fun_random.gui.feature.util.fun_mixins import FunSubModeHolder, FunSubModesWatcher
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_maps_view_model import FunRandomMapsViewModel
from fun_random_common.fun_constants import UNKNOWN_EVENT_ID
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_maps_modifier import FunRandomMapsModifier
from fun_random.gui.impl.lobby.feature.fun_random_tactical_maps_config import TacticalMapsConfigReader
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_maps_map_model import FunRandomMapsMapModel
from fun_random.gui.shared.event_dispatcher import showFunRandomProgressionWindow
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from fun_random.gui.impl.lobby.feature.fun_random_tactical_maps_config import MapPoint
from fun_random.gui.impl.lobby.tooltips.fun_random_domain_tooltip_view import FunRandomDomainTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_maps_domain_tooltip import FunRandomMapsDomainTooltip
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.lobby_context import ILobbyContext
from battle_modifiers_ext.constants_ext import ClientDomain
from account_helpers import AccountSettings
from shared_utils import first
SERVER_SETTINGS_KEYS = ('geometryIDs',)
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, Array
    from frameworks.wulf.view.view_event import ViewEvent

class FunRandomMapsView(ViewImpl, LobbyHeaderVisibility, FunSubModeHolder, FunSubModesWatcher):
    __slots__ = ('__selectedMap', '__mapsConfig', '__assetsPointer')
    _TACTICAL_MAPS_CONFIG_PATH = 'fun_random/scripts/fun_random_tactical_maps.xml'
    _EXCLUDED_MODIFIERS = {'stepRepairPoint'}
    lobbyContext = dependency.descriptor(ILobbyContext)
    funRandomCtrl = dependency.descriptor(IFunRandomController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = FunRandomMapsViewModel()
        self.__selectedMap = None
        self.__mapsConfig = TacticalMapsConfigReader.readXml(self._TACTICAL_MAPS_CONFIG_PATH)
        self.__assetsPointer = None
        super(FunRandomMapsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(FunRandomMapsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.battle_modifiers.lobby.tooltips.ModifiersDomainTooltipView():
            subModeID = int(event.getArgument('subModeId', UNKNOWN_EVENT_ID))
            modifiersDomain = event.getArgument('modifiersDomain', ClientDomain.UNDEFINED)
            return FunRandomDomainTooltipView(modifiersDomain, subModeID)
        if contentID == R.views.fun_random.lobby.tooltips.FunRandomMapsDomainTooltip():
            modifiersDomain = event.getArgument('modifiersDomain', ClientDomain.UNDEFINED)
            return FunRandomMapsDomainTooltip(modifiersDomain)
        return super(FunRandomMapsView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(FunRandomMapsView, self)._onLoading(*args, **kwargs)
        self.__fullUpdateData()
        self.suspendLobbyHeader()

    def _finalize(self):
        self.resumeLobbyHeader()
        super(FunRandomMapsView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__close),
         (self.viewModel.onSwitchSelected, self.__switchSelected),
         (self.viewModel.onNextMap, self.__nextMap),
         (self.viewModel.onPrevMap, self.__prevMap),
         (self.viewModel.onViewSwitch, self.__onViewSwitch),
         (self.viewModel.onInfo, self.__onShowInfo),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onSettingsChange))

    def __onSettingsChange(self, diff):
        if not any((key in SERVER_SETTINGS_KEYS for key in diff.iterkeys())):
            return
        self.__fullUpdateData()

    def __fullUpdateData(self):
        self.catchSubMode(self.funRandomCtrl.subModesHolder.getDesiredSubModeID())
        self.__checkUpdateSelectedMap()
        self.__updateData()

    def __nextMap(self):
        self.__updateIndexSelectedMap(1, 0)

    def __prevMap(self):
        self.__updateIndexSelectedMap(-1, 0)

    def __updateIndexSelectedMap(self, term, minVal):
        availableMaps = [ geometryType.geometryName for geometryType in self.getAvailableMaps() ]
        if self.__selectedMap not in availableMaps:
            return
        index = availableMaps.index(self.__selectedMap) + term
        if len(availableMaps) > index >= minVal:
            self.__setNewSelectedMap(availableMaps[index])
            self.__updateData()

    def __close(self):
        showHangar()

    def __setNewSelectedMap(self, selectedMap):
        self.__selectedMap = selectedMap
        AccountSettings.setFunRandom(FunRandomMaps.FUN_RANDOM_LAST_SELECTED_MAP, selectedMap)

    def __switchSelected(self, args):
        selectedMap = args.get('selectedMap')
        if selectedMap is None:
            return
        else:
            self.__setNewSelectedMap(selectedMap)
            self.__updateData()
            return

    def updateSelectedSubModeID(self):
        subMode = self.funRandomCtrl.subModesHolder.getDesiredSubMode()
        self.__assetsPointer = subMode.getAssetsPointer() if subMode and subMode.isAvailable() else ''

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            self.updateSelectedSubModeID()
            vm.setAssetsPointer(self.__assetsPointer)
            self.__fillMapsArray(vm)
            self.__fillSelectedMap(vm)

    def __checkUpdateSelectedMap(self):
        self.__selectedMap = AccountSettings.getFunRandom(FunRandomMaps.FUN_RANDOM_LAST_SELECTED_MAP)
        availableMaps = [ geometryType.geometryName for geometryType in self.getAvailableMaps() ]
        if not self.__selectedMap or self.__selectedMap not in availableMaps:
            self.__setNewSelectedMap(first(availableMaps))

    def getAvailableMaps(self):
        availableMaps = []
        mapIDs = self.funRandomCtrl.subModesHolder.getDesiredSubMode().getModeSettings().geometryIDs
        for geometryID in mapIDs:
            geometryType = ArenaType.g_geometryCache.get(geometryID)
            if geometryType is not None:
                availableMaps.append(geometryType)

        return availableMaps

    def __fillMapsArray(self, vm):
        mapsArray = vm.getMaps()
        mapsArray.clear()
        availableMaps = self.getAvailableMaps()
        funRandomMapsIds = self.__mapsConfig.getMapsIds()
        for geometryType in availableMaps:
            mapsArrayItemModel = FunRandomMapsMapModel()
            mapId = geometryType.geometryName
            mapsArrayItemModel.setId(mapId)
            mapsArrayItemModel.setIsEnabled(geometryType.geometryID in funRandomMapsIds)
            mapsArrayItemModel.setIsSelected(mapId == self.__selectedMap)
            mapsArray.addViewModel(mapsArrayItemModel)

        mapsArray.invalidate()

    def __fillSelectedMap(self, vm):
        selectedMapView = vm.selectedMapModel
        selectedMapId = self.__selectedMap
        mapPoints = self.__mapsConfig.getMapConfig(selectedMapId).mapPoints
        selectedMapView.setId(selectedMapId)
        mapPointsModel = selectedMapView.getPoints()
        mapPointsModel.clear()
        for mapPoint in mapPoints:
            self.__addMapPointToSelectedMap(mapPointsModel, mapPoint)

        mapPointsModel.invalidate()
        modifiers = selectedMapView.getModifiers()
        modifiers.clear()
        modifiersProvider = self.getHoldingSubMode().getModifiersDataProvider()
        rawModifiers = modifiersProvider.getModifiers().getModifiersIterValues()
        rawModifiersNames = set((modifier.param.clientData.domain for modifier in rawModifiers)).difference(set((mapPoint.typeName for mapPoint in mapPoints))).difference(self._EXCLUDED_MODIFIERS)
        for modifierName in rawModifiersNames:
            modifiers.addViewModel(self.__packModifierModel(modifierName))

        modifiers.invalidate()

    @staticmethod
    def __addMapPointToSelectedMap(mapPointsModel, mapPoint):
        mapPointModel = FunRandomMapsModifier()
        mapPointModel.setId(mapPoint.id)
        position = mapPoint.position
        mapPointModel.setPositionX(position.x)
        mapPointModel.setPositionY(position.y)
        mapPointModel.setType(mapPoint.typeName)
        mapPointsModel.addViewModel(mapPointModel)

    @staticmethod
    def __packModifierModel(modifierName):
        modifierModel = FunRandomMapsModifier()
        modifierModel.setType(modifierName)
        return modifierModel

    def __onViewSwitch(self):
        showFunRandomProgressionWindow()

    def __onShowInfo(self):
        self.showSubModeInfoPage(self.funRandomCtrl.subModesHolder.getDesiredSubModeID())
