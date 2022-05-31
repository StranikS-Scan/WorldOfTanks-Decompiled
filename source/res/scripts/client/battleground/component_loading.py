# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/component_loading.py
import functools
import weakref
import BigWorld
from battleground.iself_assembler import ISelfAssembler
from cgf_obsolete_script.script_game_object import ComponentDescriptorTyped, ScriptGameObject
from vehicle_systems import stricted_loading

class Loader(object):

    def __init__(self, resourceLoader, *args, **kwargs):
        self.resourceLoader = resourceLoader
        self.args = args
        self.kwargs = kwargs


class CompositeLoaderMixin(object):

    def __init__(self):
        self.__pieces = 1
        self.__callback = None
        return

    def prepareCompositeLoader(self, callback):
        self.__pieces = self._piecesNum()
        self.__callback = stricted_loading.makeCallbackWeak(callback)

    def appendPiece(self, *_):
        self.__pieces -= 1
        if self.__pieces == 0:
            self.__invoke()

    def __invoke(self):
        if self.__callback is not None:
            self.__callback(self)
        return

    def _piecesNum(self):
        pass


def loadComponentSystem(componentSystem, callback, resourceMapping=None, forceForegroundLoad=False):
    componentSystem = weakref.ref(componentSystem)
    resourceLoadingList = [ loader.resourceLoader for loader in resourceMapping.itervalues() ]
    if forceForegroundLoad:
        loadedRes = BigWorld.loadResourceListFG(resourceLoadingList)
        _processLoadedList(componentSystem, callback, resourceMapping, loadedRes)
        return
    else:
        wrappedCallback = None if callback is None else stricted_loading.makeCallbackWeak(callback)
        loadingCallback = functools.partial(_processLoadedList, componentSystem, wrappedCallback, resourceMapping)
        BigWorld.loadResourceListBG(resourceLoadingList, loadingCallback)
        return


def loadResourceMapping(resourceMapping, callback, *args, **kwargs):
    resourceLoadingList = [ loader.resourceLoader for loader in resourceMapping.itervalues() ]
    BigWorld.loadResourceListBG(resourceLoadingList, stricted_loading.makeCallbackWeak(callback, *args, **kwargs))


def _processLoadedList(componentSystemWeak, callback, resourceMapping, resourceList):
    componentSystem = componentSystemWeak()
    if componentSystem is None:
        return
    elif getattr(componentSystem, 'stopLoading', False):
        return
    else:
        for componentName, loader in resourceMapping.iteritems():
            classMember = getattr(componentSystem.__class__, componentName)
            resourceLoader = loader.resourceLoader
            componentFactory = classMember.allowedType
            if isinstance(resourceLoader, str):
                resourceName = resourceLoader
            else:
                resourceName = resourceLoader.name
            if resourceName in resourceList.failedIDs:
                return
            resourceLoaded = resourceList[resourceName]
            component = componentFactory(resourceLoaded, *loader.args, **loader.kwargs)
            setattr(componentSystem, componentName, component)

        if isinstance(componentSystem, ISelfAssembler):
            componentSystem.assembleOnLoad()
        if callback is not None:
            callback(componentSystem)
        return
