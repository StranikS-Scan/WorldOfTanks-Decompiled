# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/helpers/resources.py
import typing
from gui.impl.gen import R
from helpers import dependency
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
if typing.TYPE_CHECKING:
    from typing import Iterable
    from gui.impl.gen_utils import DynAccessor
_TEXT_PATH_PREFIX = 'open_bundle_lobby_{}'

@dependency.replace_none_kwargs(openBundle=IOpenBundleController)
def getTextResource(bundleID, path, openBundle=None):
    bundle = openBundle.config.getBundle(bundleID)

    def getResourceFromPath(resource):
        for part in path:
            resource = resource.dyn(part)

        return resource

    customResource = getResourceFromPath(R.strings.dyn(_TEXT_PATH_PREFIX.format(bundle.type)))
    return customResource if customResource.isValid() else getResourceFromPath(R.strings.open_bundle_lobby_default)
