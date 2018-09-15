# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair/container.py
from debug_utils import LOG_WARNING, LOG_DEBUG, LOG_ERROR, LOG_DEBUG_DEV
from gui import DEPTH_OF_Aim
from gui.Scaleform.daapi.view.battle.shared.crosshair import gm_factory, plugins, settings
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.meta.CrosshairPanelContainerMeta import CrosshairPanelContainerMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.shared.utils.plugins import PluginsCollection
from helpers import i18n
from gui.shared.utils.TimeInterval import TimeInterval
from AvatarInputHandler import aih_constants
import math
import BigWorld
CHECK_LEN = 2.2
CONSTANT_MERGE_OFFSET = 2
UNZOOMED_RADIUS_COEFF = 0.1
FULLY_ZOOMED_RADIUS_COEFF = 0.08
UNZOOMED_ZOOM_FACTOR = 1.0
FULLY_ZOOMED_ZOOM_FACTOR = 25.0
DISTANCE_COEFF = 0.9
SECONDARY_RADIUS_COEFF = 1.5
HYSTERESIS_TIMEOUT_CONSTANT = 0.7
HYSTERESIS_DISTANCE_CONSTANT_FULL_ZOOM = 50
HYSTERESIS_DISTANCE_CONSTANT_NO_ZOOM = 10

class CrosshairPanelContainer(ExternalFlashComponent, CrosshairPanelContainerMeta):
    """ Class is UI component that contains gun markers and crosshair panels.
    It provides access to Action Script."""

    def __init__(self):
        LOG_DEBUG('CrosshairPanelContainer:', '__init__')
        flashSettings = ExternalFlashSettings(BATTLE_VIEW_ALIASES.CROSSHAIR_PANEL, settings.CROSSHAIR_CONTAINER_SWF, settings.CROSSHAIR_ROOT_PATH, settings.CROSSHAIR_INIT_CALLBACK)
        super(CrosshairPanelContainer, self).__init__(flashSettings)
        self.__plugins = PluginsCollection(self)
        self.__plugins.addPlugins(plugins.createPlugins())
        self.__gunMarkers = None
        self.__viewID = CROSSHAIR_VIEW_ID.UNDEFINED
        self.__zoomFactor = 0.0
        self.__scale = 1.0
        self.__distance = 0
        self.__hasAmmo = True
        self.__configure()
        self.__isMerged = False
        self.__mergeTime = 0.0
        self.__vehMoveAnimTimer = TimeInterval(0.3, self, '_checkAims')
        self.__vehMoveAnimTimer.start()
        return

    def _checkAims(self):
        if self.__gunMarkers:
            viewSettings = self.__gunMarkers.getViewSettings()
            mainGun = None
            subGun = None
            for item in viewSettings:
                if not item.hasView:
                    continue
                if self.getViewID() == item.viewID:
                    if item.subGun:
                        subGun = item
                        self.as_setVerticalDeviationLowS(item.verticalDeviation < CHECK_LEN)
                    else:
                        mainGun = item

            hasMainGun = mainGun is not None and mainGun.hasView
            hasSubGun = subGun is not None and subGun.hasView
            avatar = BigWorld.player()
            if hasMainGun and hasSubGun and avatar.vehicleTypeDescriptor.isMultiTurret:
                mainRadius = avatar.inputHandler.ctrl.getGunMarkerSize(0)
                subRadius = avatar.inputHandler.ctrl.getGunMarkerSize(1)
                inSniperMode = avatar.inputHandler.ctrlModeName == aih_constants.CTRL_MODE_NAME.SNIPER
                zoomFactor = self.getZoom() if inSniperMode else 1.0
                distance = math.fabs(math.sqrt(math.pow(mainGun.screenPosition[0] - subGun.screenPosition[0], 2) + math.pow(mainGun.screenPosition[1] - subGun.screenPosition[1], 2)))
                rise = FULLY_ZOOMED_RADIUS_COEFF - UNZOOMED_RADIUS_COEFF
                run = FULLY_ZOOMED_ZOOM_FACTOR - UNZOOMED_ZOOM_FACTOR
                slope = rise / run
                yOffset = UNZOOMED_RADIUS_COEFF - slope * UNZOOMED_ZOOM_FACTOR
                radiusCoeff = slope * zoomFactor + yOffset
                mergeThreshold = CONSTANT_MERGE_OFFSET + radiusCoeff * mainRadius + DISTANCE_COEFF * distance
                shouldMerge = distance < mergeThreshold and subRadius < SECONDARY_RADIUS_COEFF * mainRadius
                if self.__isMerged and not shouldMerge:
                    if self.__mergeTime == 0.0:
                        self.__mergeTime = BigWorld.time()
                    rise = HYSTERESIS_DISTANCE_CONSTANT_FULL_ZOOM - HYSTERESIS_DISTANCE_CONSTANT_NO_ZOOM
                    run = FULLY_ZOOMED_ZOOM_FACTOR - UNZOOMED_ZOOM_FACTOR
                    slope = rise / run
                    yOffset = HYSTERESIS_DISTANCE_CONSTANT_NO_ZOOM - slope * UNZOOMED_ZOOM_FACTOR
                    hysteresisDistance = slope * zoomFactor + yOffset
                    if abs(distance - mergeThreshold) < hysteresisDistance and BigWorld.time() - self.__mergeTime < HYSTERESIS_TIMEOUT_CONSTANT:
                        shouldMerge = True
                else:
                    self.__mergeTime = 0.0
                self.__isMerged = shouldMerge
                self.as_setMergeS(shouldMerge)
        return

    def getViewID(self):
        """Gets current view ID of panel.
        :return: integer containing of CROSSHAIR_VIEW_ID.
        """
        return self.__viewID

    def setViewID(self, viewID):
        """Sets view ID of panel to change view presentation.
        :param viewID:
        """
        LOG_DEBUG(self, 'setViewID', viewID)
        if viewID != self.__viewID:
            self.__viewID = viewID
            if self.__gunMarkers is not None:
                self.__gunMarkers.switch(viewID)
            chosenSettingID = plugins.chooseSetting(self.__viewID)
            self.as_setViewS(self.__viewID, chosenSettingID)
        return

    def setPosition(self, x, y):
        """Sets position of crosshair panel in pixels.
        :param x: integer containing x coordinate of center in pixels.
        :param y: integer containing y coordinate of center in pixels.
        """
        self.as_recreateDeviceS(x, y)

    def getScale(self):
        """Gets scale factor.
        :return: float containing scale factor.
        """
        return self.__scale

    def setScale(self, scale):
        """Sets scale factor.
        :param scale: float containing new scale factor.
        """
        if self.__scale == scale:
            return
        else:
            self.__scale = scale
            self.as_setScaleS(scale)
            if self.__gunMarkers is not None:
                self.__gunMarkers.setScale(scale)
            return

    def getZoom(self):
        """ Gets current zoom factor of player's camera.
        :return: float containing zoom factor.
        """
        return self.__zoomFactor

    def setZoom(self, zoomFactor):
        """ Gets current zoom factor of player's camera.
        :param zoomFactor: float containing zoom factor.
        """
        if zoomFactor == self.__zoomFactor:
            return
        self.__zoomFactor = zoomFactor
        if zoomFactor > 1:
            zoomString = i18n.makeString(INGAME_GUI.AIM_ZOOM, zoom=zoomFactor)
        else:
            zoomString = ''
        self.as_setZoomS(zoomString)

    def getDistance(self):
        """ Gets distance to desired target(point).
        :return: integer containing distance in meters.
        """
        return self.__distance

    def setDistance(self, distance):
        """ Sets distance to desired target(point).
        :param distance: integer containing distance in meters.
        """
        if distance != self.__distance:
            self.__distance = distance
            self.as_setDistanceS(i18n.makeString(INGAME_GUI.DISTANCE_METERS, meters=distance))

    def clearDistance(self, immediate=True):
        """ Removes distance string from UI.
        :param immediate: if value equals True than removes distance string from UI immediately,
            otherwise - hides this sting with animation.
        """
        self.__distance = 0
        self.as_clearDistanceS(immediate)

    def setHasAmmo(self, hasAmmo):
        """ Sets flag that indicates controlling vehicle has ammo.
        :param hasAmmo: bool.
        """
        if self.__hasAmmo != hasAmmo:
            self.__hasAmmo = hasAmmo
            if not hasAmmo:
                self.as_updateAmmoStateS(i18n.makeString(INGAME_GUI.PLAYER_MESSAGES_POSTMORTEM_USERNOHASAMMO))
            else:
                self.as_updateAmmoStateS('')

    def setSettings(self, vo):
        """ Sets new crosshair settings.
        :param vo: dictionary containing required settings, see _makeSettingsVO.
        """
        self.as_setSettingsS(vo)

    def createGunMarkers(self, markersInfo, vehicleInfo):
        """ Creates new set of gun markers at once if its is not created.
        :param markersInfo: instance of GunMarkersSetInfo.
        :param vehicleInfo: instance of VehicleArenaInfoVO.
        """
        LOG_DEBUG('container:', 'createGunMarkers', markersInfo, vehicleInfo)
        if self.__gunMarkers is not None:
            LOG_WARNING('Set of gun markers is already created.')
            return
        else:
            self.__setGunMarkers(gm_factory.createComponents(markersInfo, vehicleInfo))
            return

    def invalidateGunMarkers(self, markersInfo, vehicleInfo):
        """ Checks present set of of gun markers to remove unused markers or to create new markers.
        For example, player uses client's gun markers and server's gun markers together,
        he removes setting item "use server marker", we need destroy server's gun markers.
        :param markersInfo: instance of GunMarkersSetInfo.
        :param vehicleInfo: instance of VehicleArenaInfoVO.
        """
        if self.__gunMarkers is None:
            LOG_WARNING('Set of gun markers is not created')
            return
        else:
            newSet = gm_factory.overrideComponents(self.__gunMarkers, markersInfo, vehicleInfo)
            self.__clearGunMarkers()
            self.__setGunMarkers(newSet)
            return

    def setGunMarkerColor(self, markerType, color):
        """ Sets new color of gun marker.
        :param markerType: one of GUN_MARKER_TYPE.*.
        :param color: string containing alias of color.
        :return: bool.
        """
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

    def _populate(self):
        super(CrosshairPanelContainer, self)._populate()
        self.__plugins.init()
        self.startPlugins()

    def _dispose(self):
        self.stopPlugins()
        self.__plugins.fini()
        super(CrosshairPanelContainer, self)._dispose()

    def __configure(self):
        self.component.wg_inputKeyMode = 2
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
            if self.as_createGunMarkerS(item.viewID, item.linkage, item.name, item.subGun, item.id):
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
