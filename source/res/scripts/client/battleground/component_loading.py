# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/component_loading.py
import functools
import weakref
import BigWorld
from battleground.iself_assembler import ISelfAssembler
from svarog_script.script_game_object import ComponentDescriptorTyped
from vehicle_systems import stricted_loading

class Loader(object):

    def __init__(self, resourceLoader, *args, **kwargs):
        self.resourceLoader = resourceLoader
        self.args = args
        self.kwargs = kwargs


def loadComponentSystem(componentSystem, callback, resourceMapping=None):
    componentSystem = weakref.ref(componentSystem)
    resourceLoadingList = [ loader.resourceLoader for loader in resourceMapping.itervalues() ]
    wrappedCallback = None if callback is None else stricted_loading.makeCallbackWeak(callback)
    loadingCallback = functools.partial(_processLoadedList, componentSystem, wrappedCallback, resourceMapping)
    BigWorld.loadResourceListBG(resourceLoadingList, loadingCallback)
    return


def _processLoadedList(componentSystemWeak, callback, resourceMapping, resourceList):
    componentSystem = componentSystemWeak()
    if componentSystem is None:
        return
    elif getattr(componentSystem, 'stopLoading', False):
        return
    else:
        for componentName, loader in resourceMapping.iteritems():
            classMember = componentSystem.__class__.__getattribute__(componentSystem.__class__, componentName)
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
