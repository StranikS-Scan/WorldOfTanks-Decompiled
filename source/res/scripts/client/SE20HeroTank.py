# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SE20HeroTank.py
from HeroTank import HeroTank
from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LOBBY_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from vehicle_systems.tankStructure import ModelStates

class SE20HeroTank(HeroTank):
    gameEventController = dependency.descriptor(IGameEventController)

    @property
    def name(self):
        if self.typeDescriptor is None:
            return ''
        else:
            name_ = self.typeDescriptor.type.userString
            eventHeroTank = self.eventHeroTank
            if not eventHeroTank.isPurchased() and not eventHeroTank.isRestore():
                discount = eventHeroTank.getDiscount()
                if discount != 0:
                    discountText = text_styles.markerExtraText(backport.text(R.strings.event.markers.discount(), discount=discount))
                    return text_styles.concatStylesToMultiLine(name_, discountText)
            return name_

    @property
    def eventHeroTank(self):
        return self.gameEventController.getHeroTank()

    def onEnterWorld(self, prereqs):
        self._heroTankCtrl.onEnterPreviewFromEvent += self.removeModelFromScene
        self._heroTankCtrl.onExitPreviewFromEvent += self._updateHeroTank
        self.eventHeroTank.onDiscountChanged += self.progressChangeHandler
        super(SE20HeroTank, self).onEnterWorld(prereqs)

    def onLeaveWorld(self):
        self._heroTankCtrl.onEnterPreviewFromEvent -= self.removeModelFromScene
        self._heroTankCtrl.onExitPreviewFromEvent -= self._updateHeroTank
        self.eventHeroTank.onDiscountChanged -= self.progressChangeHandler
        super(SE20HeroTank, self).onLeaveWorld()

    def removeModelFromScene(self):
        self.eventHeroTank.onDiscountChanged -= self.progressChangeHandler
        if self.isVehicleLoaded and self.isVehicleAppearanceLoaded:
            self._onVehicleDestroy()
            self.removeVehicle()
            self.typeDescriptor = None
        return

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None):
        super(SE20HeroTank, self).recreateVehicle(typeDescriptor, state, callback)
        self.setEnable(True)

    def progressChangeHandler(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_UPDATED, ctx={'entity': self,
         'lobbyType': LOBBY_TYPE.EVENT}), scope=EVENT_BUS_SCOPE.LOBBY)
