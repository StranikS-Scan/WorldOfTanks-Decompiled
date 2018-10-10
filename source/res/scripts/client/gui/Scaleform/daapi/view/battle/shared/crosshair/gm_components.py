# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair/gm_components.py
import logging
from collections import namedtuple
import GUI
from gui.Scaleform.daapi.view.battle.shared.crosshair import settings
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class IGunMarkerComponent(object):

    def addView(self, container):
        raise NotImplementedError

    def removeView(self, container):
        raise NotImplementedError

    def getScale(self):
        raise NotImplementedError

    def setScale(self, scale):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def getMarkerType(self):
        raise NotImplementedError

    def getViewID(self):
        raise NotImplementedError

    def getName(self):
        raise NotImplementedError

    def getViewSettings(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def setActive(self, active):
        raise NotImplementedError

    def setDataProvider(self, markerType, dataProvider):
        raise NotImplementedError


_ViewSettings = namedtuple('_ViewSettings', ('viewID', 'linkage', 'name', 'hasView'))

class GunMarkerComponent(IGunMarkerComponent):

    def __init__(self, markerType, viewID, name, linkage, dataProvider, isActive=False):
        super(GunMarkerComponent, self).__init__()
        self._markerType = markerType
        self._viewID = viewID
        self._name = name
        self._linkage = linkage
        self._dataProvider = dataProvider
        self._view = None
        self._isActive = isActive
        self._scale = 1.0
        return

    def addView(self, container):
        if self._view is not None:
            _logger.error('GunMarkerComponent "%s" is already created.', self._name)
            return
        else:
            self._view = self._createView(container)
            _logger.debug('GunMarkerComponent "%s" is created', self._name)
            if self._isActive:
                self._setupDataProvider()
            container.addChild(self._view, self._name)
            return

    def removeView(self, container):
        if self._view is None:
            _logger.error('GunMarkerComponent "%s" is already removed.', self._name)
            return
        else:
            self._clearDataProvider()
            container.delChild(self._view)
            self._view = None
            return

    def getScale(self):
        return self._scale

    def setScale(self, scale):
        self._scale = scale

    def destroy(self):
        self._dataProvider = None
        if self._view is not None:
            self._view.clearDataProvider()
            self._view = None
        return

    def getMarkerType(self):
        return self._markerType

    def getViewID(self):
        return self._viewID

    def getName(self):
        return self._name

    def getViewSettings(self):
        return _ViewSettings(self._viewID, self._linkage, self._name, self._view is not None)

    def isActive(self):
        return self._isActive

    def setActive(self, active):
        self._isActive = active
        if self._view is not None:
            if self._isActive:
                self._setupDataProvider()
            else:
                self._clearDataProvider()
        return

    def setDataProvider(self, markerType, dataProvider):
        self._markerType = markerType
        self._dataProvider = dataProvider
        if self._isActive and self._view is not None:
            self._setupDataProvider()
        return

    def _setupDataProvider(self):
        if self._dataProvider is not None:
            self._view.setDataProvider(self._dataProvider)
        return

    def _clearDataProvider(self):
        self._view.clearDataProvider()

    def _createView(self, movie):
        raise NotImplementedError


class DefaultGunMarkerComponent(GunMarkerComponent):

    def _createView(self, container):
        view = GUI.WGCrosshairFlash(container.movie, settings.CROSSHAIR_ITEM_PATH_FORMAT.format(self._name), settings.CROSSHAIR_RADIUS_MC_NAME)
        view.wg_inputKeyMode = 2
        view.focus = False
        view.moveFocus = False
        view.heightMode = 'PIXEL'
        view.widthMode = 'PIXEL'
        return view


class SPGGunMarkerComponent(GunMarkerComponent):

    def setScale(self, scale):
        super(SPGGunMarkerComponent, self).setScale(scale)
        if self._view is not None:
            self._view.setPointsBaseScale(self._scale)
        return

    def _createView(self, container):
        view = GUI.WGSPGCrosshairFlash(container.movie, settings.CROSSHAIR_ITEM_PATH_FORMAT.format(self._name), settings.SPG_GUN_MARKER_ELEMENTS_COUNT)
        view.wg_inputKeyMode = 2
        view.focus = False
        view.moveFocus = False
        view.heightMode = 'PIXEL'
        view.widthMode = 'PIXEL'
        view.setPointsBaseScale(self._scale)
        return view


class VideoGunMarkerComponent(DefaultGunMarkerComponent):

    def getViewSettings(self):
        return _ViewSettings(CROSSHAIR_VIEW_ID.ARCADE, self._linkage, self._name, self._view is not None)


class GunMarkersComponents(object):

    def __init__(self, components):
        super(GunMarkersComponents, self).__init__()
        self.__components = {}
        for component in components:
            name = component.getName()
            if name in self.__components:
                raise SoftException('Name of component must be unique. {} is already existed'.format(name))
            self.__components[name] = component

    def addView(self, container, name):
        component = self.getComponentByName(name)
        if component is not None:
            self.__components[name].addView(container)
            return True
        else:
            return False

    def removeView(self, container, name):
        component = self.getComponentByName(name)
        if component is not None:
            component.removeView(container)
            return True
        else:
            return False

    def setScale(self, scale):
        for component in self.__components.itervalues():
            component.setScale(scale)

    def clear(self):
        while self.__components:
            _, component = self.__components.popitem()
            component.destroy()

    def switch(self, viewID):
        seq = []
        for name, component in self.__components.iteritems():
            receivedID = component.getViewID()
            if receivedID != CROSSHAIR_VIEW_ID.UNDEFINED:
                isActive = receivedID == viewID
                seq.append((isActive, name))

        seq.sort(key=lambda item: item[0])
        for isActive, name in seq:
            self.__components[name].setActive(isActive)

    def popComponent(self, name):
        if name in self.__components:
            component = self.__components.pop(name)
            component.setActive(False)
        else:
            component = None
        return component

    def getComponentsNumber(self):
        return len(self.__components)

    def getComponentByName(self, name):
        return self.__components[name] if name in self.__components else None

    def getComponentByType(self, markerType, isActive=True):
        for component in self.__components.itervalues():
            if component.getMarkerType() == markerType:
                if isActive:
                    if component.isActive():
                        return component
                else:
                    return component

        return None

    def getViewSettings(self):
        return [ c.getViewSettings() for c in self.__components.itervalues() ]
