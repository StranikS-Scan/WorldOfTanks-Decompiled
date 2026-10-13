# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/bestiary_view.py
from __future__ import absolute_import
import BigWorld
from frameworks.wulf import WindowFlags
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import getIconResourceName
from halloween.gui.impl.gen.view_models.views.lobby.bestiary_view_model import BestiaryViewModel
from halloween.gui.impl.gen.view_models.views.lobby.enemy_model import EnemyModel
from halloween.gui.impl.lobby.hw_helpers.bestiary_helper import getEnemyRole, isEnemyUnlocked, getUnlockMissionIdx, getEnemiesSeenList, markEnemyAsSeen, getLastSelectedEnemy, setLastSelectedEnemy
from halloween.gui.impl.lobby.widgets.shop_style_panel import ShopStylePanelPresenter
from halloween.gui.shared.event_dispatcher import showBestiaryWindow
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import BESTIARY_ENTER, BESTIARY_EXIT
from halloween.skeletons.halloween_bestiary_controller import IHalloweenBestiaryController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys, HWLogActions
from helpers import dependency
from items.vehicles import getVehicleType

class BestiaryView(ViewComponent):
    __hwBestiaryCtrl = dependency.descriptor(IHalloweenBestiaryController)

    def __init__(self, ctx):
        self.__enemyIntCD = ctx.get('vehIntCD', None)
        super(BestiaryView, self).__init__(R.views.halloween.mono.lobby.bestiary(), BestiaryViewModel)
        self.__uiLogger = HWMetricsLogger(HWLogKeys.BESTIARY_VIEW)
        return

    @property
    def viewModel(self):
        return super(BestiaryView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(BestiaryView, self).createToolTipContent(event, contentID)

    def _getChildComponents(self):
        return {R.aliases.halloween.shared.ShopStylePanel(): ShopStylePanelPresenter}

    def _getEvents(self):
        return ((self.viewModel.onChangeEnemy, self.__onSelectEnemy),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onResize, self.__onResize),
         (self.viewModel.onClose, self.__onClose),
         (self.__hwBestiaryCtrl.onSettingsUpdate, self.__onSettingsUpdate))

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            intCD = self.__enemyIntCD or self.__hwBestiaryCtrl.getFirstNewEnemy() or getLastSelectedEnemy()
            self.__selectEnemy(vm, intCD, isInit=True)
            self.__updateEnemiesModel(vm)
        super(BestiaryView, self)._onLoading()
        self.__uiLogger.onStartView(HWLogActions.LIFETIME)

    def _initialize(self, *args, **kwargs):
        super(BestiaryView, self)._initialize()
        playSound(BESTIARY_ENTER)

    def _finalize(self):
        playSound(BESTIARY_EXIT)
        self.__uiLogger.onStopView(HWLogActions.LIFETIME)
        super(BestiaryView, self)._finalize()

    def __onClose(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    @staticmethod
    def __onMoveSpace(moveTypeArgs=None):
        if moveTypeArgs is None:
            return
        else:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=moveTypeArgs), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx=moveTypeArgs), EVENT_BUS_SCOPE.GLOBAL)
            return

    @args2params(int)
    def __onSelectEnemy(self, intCD):
        showBestiaryWindow(intCD)
        with self.viewModel.transaction() as vm:
            self.__selectEnemy(vm, intCD)

    @staticmethod
    def __onResize(args):
        if args is None:
            return
        else:
            screenWidth, screenHeight = BigWorld.windowSize()
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.ON_RESIZE, ctx={'xmin': float(args.get('xmin', 0)),
             'ymin': float(args.get('ymin', 0)),
             'xmax': float(args.get('xmax', screenWidth)),
             'ymax': float(args.get('ymax', screenHeight))}))
            return

    def __onSettingsUpdate(self):
        with self.viewModel.transaction() as vm:
            self.__updateEnemiesModel(vm)

    def __selectEnemy(self, vm, intCD, isInit=False):
        vm.setSelectedIntCD(intCD)
        modelEnemies = vm.getEnemies()
        for enemy in modelEnemies:
            if enemy.getIntCD() == intCD:
                enemy.setIsNew(False)
                break

        modelEnemies.invalidate()
        markEnemyAsSeen(intCD)
        setLastSelectedEnemy(intCD)
        enemy = self.__hwBestiaryCtrl.getEnemyByIntCD(intCD)
        if not isInit:
            playSound(enemy.sounds.select)

    def __updateEnemiesModel(self, vm):
        enemiesSeenList = getEnemiesSeenList()
        modelEnemies = vm.getEnemies()
        modelEnemies.clear()
        for intCD, enemy in self.__hwBestiaryCtrl.enemies:
            enemyType = getVehicleType(intCD)
            isUnlocked = isEnemyUnlocked(enemy)
            modelEnemy = EnemyModel()
            modelEnemy.setIntCD(intCD)
            modelEnemy.setName(enemyType.userString)
            modelEnemy.setResourceKey(getIconResourceName(enemy.name))
            modelEnemy.setRole(getEnemyRole(enemyType))
            modelEnemy.setAbility(enemy.ability)
            modelEnemy.setUnlockedByMission(getUnlockMissionIdx(enemy))
            modelEnemy.setHasShopStyle(bool(enemy.shop.bundles))
            modelEnemy.setIsNew(isUnlocked and intCD not in enemiesSeenList)
            modelEnemy.setIsLocked(not isUnlocked)
            modelEnemies.addViewModel(modelEnemy)

        modelEnemies.invalidate()


class BestiaryWindow(WindowImpl):

    def __init__(self, layer, ctx, **_):
        super(BestiaryWindow, self).__init__(content=BestiaryView(ctx), wndFlags=WindowFlags.WINDOW, layer=layer)
