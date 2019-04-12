# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair/container.py
from debug_utils import LOG_WARNING, LOG_DEBUG, LOG_ERROR
from gui import DEPTH_OF_Aim
from gui.Scaleform.daapi.view.battle.shared.crosshair import gm_factory, plugins, settings
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.meta.CrosshairPanelContainerMeta import CrosshairPanelContainerMeta
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.shared.utils.plugins import PluginsCollection
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency, i18n

class CrosshairPanelContainer(ExternalFlashComponent, CrosshairPanelContainerMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CrosshairPanelContainer, self).__init__(ExternalFlashSettings(BATTLE_VIEW_ALIASES.CROSSHAIR_PANEL, settings.CROSSHAIR_CONTAINER_SWF, settings.CROSSHAIR_ROOT_PATH, settings.CROSSHAIR_INIT_CALLBACK))
        self.__plugins = PluginsCollection(self)
        self.__plugins.addPlugins(plugins.createPlugins())
        self.__gunMarkers = None
        self.__viewID = CROSSHAIR_VIEW_ID.UNDEFINED
        self.__zoomFactor = 0.0
        self.__scale = 1.0
        self.__distance = 0
        self.__hasAmmo = True
        return

    def getViewID(self):
        return self.__viewID

    def setViewID(self, viewID):
        if viewID != self.__viewID:
            self.__viewID = viewID
            if self.__gunMarkers is not None:
                self.__gunMarkers.switch(viewID)
            chosenSettingID = plugins.chooseSetting(self.__viewID)
            self.as_setViewS(self.__viewID, chosenSettingID)
        return

    def setPosition(self, x, y):
        self.as_recreateDeviceS(x, y)

    def getScale(self):
        return self.__scale

    def setScale(self, scale):
        if self.__scale == scale:
            return
        else:
            self.__scale = scale
            self.as_setScaleS(scale)
            if self.__gunMarkers is not None:
                self.__gunMarkers.setScale(scale)
            return

    def getZoom(self):
        return self.__zoomFactor

    def setZoom(self, zoomFactor):
        if zoomFactor == self.__zoomFactor:
            return
        self.__zoomFactor = zoomFactor
        if zoomFactor > 1:
            zoomString = i18n.makeString(INGAME_GUI.AIM_ZOOM, zoom=zoomFactor)
        else:
            zoomString = ''
        self.as_setZoomS(zoomString)

    def getDistance(self):
        return self.__distance

    def setDistance(self, distance):
        if distance != self.__distance:
            self.__distance = distance
            self.as_setDistanceS(i18n.makeString(INGAME_GUI.DISTANCE_METERS, meters=distance))

    def clearDistance(self, immediate=True):
        self.__distance = 0
        self.as_clearDistanceS(immediate)

    def setHasAmmo(self, hasAmmo):
        if self.__hasAmmo != hasAmmo:
            self.__hasAmmo = hasAmmo
            if not hasAmmo:
                self.as_updateAmmoStateS(i18n.makeString(INGAME_GUI.PLAYER_MESSAGES_POSTMORTEM_USERNOHASAMMO))
            else:
                self.as_updateAmmoStateS('')

    def setSettings(self, vo):
        self.as_setSettingsS(vo)

    def createGunMarkers(self, markersInfo, vehicleInfo):
        if self.__gunMarkers is not None:
            LOG_WARNING('Set of gun markers is already created.')
            return
        else:
            self.__setGunMarkers(gm_factory.createComponents(markersInfo, vehicleInfo))
            return

    def invalidateGunMarkers(self, markersInfo, vehicleInfo):
        if self.__gunMarkers is None:
            LOG_WARNING('Set of gun markers is not created')
            return
        else:
            newSet = gm_factory.overrideComponents(self.__gunMarkers, markersInfo, vehicleInfo)
            self.__clearGunMarkers()
            self.__setGunMarkers(newSet)
            return

    def setGunMarkerColor(self, markerType, color):
        if self.__gunMarkers is None:
            return False
        else:
            component = self.__gunMarkers.getComponentByType(markerType, isActive=True)
            if component is not None:
                self.as_setGunMarkerColorS(component.getName(), color)
            return True

    def startPlugins(self):
        self.__plugins.start()

    def stopPlugins(self):
        self.__clearGunMarkers()
        self.__plugins.stop()

    def createExternalComponent(self):
        super(CrosshairPanelContainer, self).createExternalComponent()
        self.__configure()

    def _populate(self):
        super(CrosshairPanelContainer, self)._populate()
        self.__plugins.init()
        self.startPlugins()

    def _dispose(self):
        self.stopPlugins()
        self.__plugins.fini()
        super(CrosshairPanelContainer, self)._dispose()

    def __configure(self):
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.component.position.z = DEPTH_OF_Aim
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.backgroundAlpha = 0

    def __setGunMarkers(self, gunMarkers):
        self.__gunMarkers = gunMarkers
        viewSettings = self.__gunMarkers.getViewSettings()
        LOG_DEBUG('Present view settings of gun markers', viewSettings)
        for item in viewSettings:
            if item.hasView:
                continue
            if self.as_createGunMarkerS(item.viewID, item.linkage, item.name):
                self.__gunMarkers.addView(self.component, item.name)
                LOG_DEBUG('Gun marker has been created', item)
            LOG_ERROR('Gun marker can not be created', item)

        self.__gunMarkers.setScale(self.getScale())
        self.__gunMarkers.switch(self.getViewID())

    def __clearGunMarkers(self):
        if self.__gunMarkers is None:
            return
        else:
            viewSettings = self.__gunMarkers.getViewSettings()
            LOG_DEBUG('Previous view settings of gun markers', viewSettings)
            for item in viewSettings:
                if not item.hasView:
                    continue
                if self.as_destroyGunMarkerS(item.name):
                    self.__gunMarkers.removeView(self.component, item.name)
                    LOG_DEBUG('Gun marker has been destroyed', item)

            self.__gunMarkers.clear()
            self.__gunMarkers = None
            return
