# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair/gm_components.py
from collections import namedtuple
import GUI
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared.crosshair import settings
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID

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
        assert self._view is None, 'View is already created.'
        self._view = self._createView(container)
        LOG_DEBUG('FlashGUIComponent is created', self._name, self._view)
        if self._isActive:
            self._setupDataProvider()
        container.addChild(self._view, self._name)
        return

    def removeView(self, container):
        assert self._view is not None, 'View is already removed.'
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
    """Class contains set of gun marker components, provides access to them."""

    def __init__(self, components):
        super(GunMarkersComponents, self).__init__()
        self.__components = {}
        for component in components:
            name = component.getName()
            if name in self.__components:
                raise ValueError('Name of component must be unique. {} is already existed'.format(name))
            self.__components[name] = component

    def addView(self, container, name):
        """ Adds view to appropriate component by name.
        :param container: FlashGUIComponent which created gun marker view on the Action Script side.
        :param name: unique name of component.
        :return: True if component is found by name, otherwise - False.
        """
        component = self.getComponentByName(name)
        if component is not None:
            self.__components[name].addView(container)
            return True
        else:
            return False
            return

    def removeView(self, container, name):
        """ Removes view from appropriate component by name.
        :param container: FlashGUIComponent which contains gun marker view.
        :param name: unique name of component.
        :return: True if component is found by name, otherwise - False.
        """
        component = self.getComponentByName(name)
        if component is not None:
            component.removeView(container)
            return True
        else:
            return False
            return

    def setScale(self, scale):
        """ Sets scale for all components.
        :param scale: float containing present value of scale.
        """
        for component in self.__components.itervalues():
            component.setScale(scale)

    def clear(self):
        """Clears all components and removes from this object."""
        while self.__components:
            _, component = self.__components.popitem()
            component.destroy()

    def switch(self, viewID):
        """ Sets active flag for each component.
        Active flag equals True if component's view ID equals specified view ID, otherwise - False.
        :param viewID: one of CROSSHAIR_VIEW_ID.*.
        """
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
        """ Removes component by name.
        :param name: uniques name of component.
        :return: instance of component if component is found, otherwise - None.
        """
        if name in self.__components:
            component = self.__components.pop(name)
            component.setActive(False)
        else:
            component = None
        return component

    def getComponentsNumber(self):
        return len(self.__components)

    def getComponentByName(self, name):
        """ Gets components by unique name.
        :param name: string containing unique name of component.
        :return: instance of component or None.
        """
        if name in self.__components:
            return self.__components[name]
        else:
            return None
            return None

    def getComponentByType(self, markerType, isActive=True):
        """ Try to find first component by type of marker and active flag.
        :param markerType: one of GUN_MARKER_TYPE.*.
        :param isActive: bool.
        :return: instance of component if component is found, otherwise - None.
        """
        for component in self.__components.itervalues():
            if component.getMarkerType() == markerType:
                if isActive:
                    if component.isActive():
                        return component
                else:
                    return component

        return None

    def getViewSettings(self):
        """ Gets present settings of components.
        :return: list[_ViewSettings(...), ...].
        """
        return map(lambda component: component.getViewSettings(), self.__components.itervalues())
