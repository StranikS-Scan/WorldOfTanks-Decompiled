# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/select_respawn.py
import logging
import time
import weakref
from frameworks.wulf import ViewFlags
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from gui.doc_loaders.battle_royale_settings_loader import getBattleRoyaleSettings
from gui.impl import backport
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.battle_royale.select_respawn_view_model import SelectRespawnViewModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.respawn_point_view_model import RespawnPointViewModel
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class SelectRespawnComponent(InjectComponentAdaptor, ISpawnListener):

    def __init__(self):
        super(SelectRespawnComponent, self).__init__()
        self.__view = None
        return

    def _makeInjectView(self):
        self.__view = SelectRespawnView()
        return self.__view

    def _dispose(self):
        super(SelectRespawnComponent, self)._dispose()
        if self.__view:
            self.__view.dispose()
        self.__view = None
        return

    def setSpawnPoints(self, points):
        if self.__view:
            self.__view.setPoints(points)

    def updateCloseTime(self, timeLeft, state):
        if self.__view:
            self.__view.updateCloseTime(timeLeft, state)

    def updatePoint(self, vehicleId, pointId, prevPointId):
        if self.__view:
            self.__view.updatePoint(vehicleId, pointId, prevPointId)


class BRPrebattleTimer(IAbstractPeriodView):

    def __init__(self, parentView):
        self.__timeLeft = 0
        self._parentView = parentView
        self.__endingTime = getBattleRoyaleSettings().spawn.selectEndingSoonTime

    def updateCloseTime(self, timeLeft, state):
        self.__timeLeft = timeLeft
        if state == COUNTDOWN_STATE.WAIT:
            self._parentView.viewModel.setLeftTime(self.__getWaitMessage())
            self._parentView.viewModel.setIsWaitingPlayers(True)
        else:
            self.__updateTimer()

    def __updateTimer(self):
        with self._parentView.viewModel.transaction() as vm:
            vm.setLeftTime(time.strftime('%M:%S', time.gmtime(round(self.__timeLeft))))
            vm.setIsWaitingPlayers(False)
            if round(self.__timeLeft) <= self.__endingTime:
                vm.setIsTimeRunningOut(True)

    @staticmethod
    def __getWaitMessage():
        return backport.text(R.strings.ingame_gui.timer.waiting())


class SelectRespawnView(ViewImpl):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(SelectRespawnView, self).__init__(R.views.battle.battleRoyale.select_respawn.SelectRespawn(), ViewFlags.COMPONENT, SelectRespawnViewModel, *args, **kwargs)
        arenaVisitor = self.__sessionProvider.arenaVisitor
        self.__mapTexture = 'url:../../{}'.format(arenaVisitor.type.getMinimapTexture())
        self.__background = self.__getBgByGeometryName(arenaVisitor.type.getGeometryName())
        bottomLeft, topRight = arenaVisitor.type.getBoundingBox()
        self.__mapSize, _ = topRight - bottomLeft
        self.__offset = bottomLeft
        self.__closeTime = 0
        self.__points = []
        self.__pointsById = {}
        self.__timer = BRPrebattleTimer(weakref.proxy(self))

    @property
    def viewModel(self):
        return super(SelectRespawnView, self).getViewModel()

    def updateCloseTime(self, timeLeft, state):
        self.__timer.updateCloseTime(timeLeft, state)

    def dispose(self):
        pass

    def setPoints(self, points):
        with self.viewModel.transaction() as vm:
            vmPoints = vm.getPoints()
            vmPoints.clear()
            for point in points:
                pointId = point['guid']
                coordX, coordY = point['position'] - self.__offset
                pointVM = RespawnPointViewModel()
                pointVM.setPointID(pointId)
                pointVM.setCoordX(coordX)
                pointVM.setCoordY(coordY)
                vmPoints.addViewModel(pointVM)

            vmPoints.invalidate()

    def updatePoint(self, vehicleId, pointId, prevPointId):
        arenaDP = self.__sessionProvider.getArenaDP()
        playerName = arenaDP.getVehicleInfo(vehicleId).player.name
        with self.viewModel.transaction() as vm:
            vmPoints = vm.getPoints()
            for vmPoint in vmPoints:
                if vmPoint.getPointID() == pointId:
                    if not vmPoint.getPlayerName1():
                        vmPoint.setPlayerName1(playerName)
                    else:
                        vmPoint.setPlayerName2(playerName)
                if vmPoint.getPointID() == prevPointId:
                    if vmPoint.getPlayerName1() == playerName:
                        vmPoint.setPlayerName1(vmPoint.getPlayerName2() or '')
                        vmPoint.setPlayerName2('')
                    if vmPoint.getPlayerName2() == playerName:
                        vmPoint.setPlayerName2('')

            vmPoints.invalidate()

    def _initialize(self, *args, **kwargs):
        super(SelectRespawnView, self)._initialize()
        self.viewModel.onCompleteBtnClick += self.__onCompleteBtnClick
        self.viewModel.onSelectPoint += self.__onSelectPoint
        with self.viewModel.transaction() as vm:
            vm.setMapSize(abs(self.__mapSize))
            vm.setMinimapBG(self.__mapTexture)
            vm.setHeader(R.strings.battle_royale.selectRespawn.header())
            vm.setDescription(R.strings.battle_royale.selectRespawn.description())
            vm.setBtnDescription(R.strings.battle_royale.selectRespawn.btnDescription())
            vm.setBackground(self.__background)

    def _finalize(self):
        super(SelectRespawnView, self)._finalize()
        self.viewModel.onCompleteBtnClick -= self.__onCompleteBtnClick
        self.viewModel.onSelectPoint -= self.__onSelectPoint

    def __getBgByGeometryName(self, geometry):
        if geometry == '250_br_battle_city2-1':
            return R.images.gui.maps.icons.battleRoyale.spawnBg.c_250_br_battle_city2_1()
        else:
            return R.images.gui.maps.icons.battleRoyale.spawnBg.c_251_br_battle_city3() if geometry == '251_br_battle_city3' else None

    def __onSelectPoint(self):
        spawnCtrl = self.__sessionProvider.dynamic.spawn
        if spawnCtrl:
            _logger.info('Selected point ID = %s', self.viewModel.getSelectedPointID())
            spawnCtrl.chooseSpawnKeyPoint(self.viewModel.getSelectedPointID())

    def __onCompleteBtnClick(self):
        spawnCtrl = self.__sessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.placeVehicle()
