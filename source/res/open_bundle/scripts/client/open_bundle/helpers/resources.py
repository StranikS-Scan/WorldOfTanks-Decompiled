# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/helpers/resources.py
from __future__ import absolute_import
import typing
from gui.impl.gen import R
from helpers import dependency
from open_bundle.gui.constants import OPEN_BUNDLE_ENTRY_POINT_NAME
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
if typing.TYPE_CHECKING:
    from typing import Iterable
    from frameworks.wulf import PyResAccessor
_TEXT_PATH_PREFIX = 'open_bundle_lobby_{}'
_IMAGES_PATH_PREFIX = 'open_bundle.gui.maps.icons.bundles.{}'
_DEFAULT_BUNDLE_TYPE = 'default'

@dependency.replace_none_kwargs(openBundle=IOpenBundleController)
def getTextResource(bundleID, path, openBundle=None):
    bundle = openBundle.config.getBundle(bundleID)
    customResource = _getResourceFromPath(R.strings.dyn(_TEXT_PATH_PREFIX.format(bundle.type)), path)
    return customResource if customResource.isValid() else _getResourceFromPath(R.strings.open_bundle_lobby_default, path)


@dependency.replace_none_kwargs(openBundle=IOpenBundleController)
def getBannerImagesPath(bundleID, openBundle=None):
    bundle = openBundle.config.getBundle(bundleID)
    if bundle.type:
        bannerPath = ['hangarEventBanners', 'event', OPEN_BUNDLE_ENTRY_POINT_NAME]
        customImages = R.images.open_bundle.gui.maps.icons.bundles.dyn(bundle.type)
        if _getResourceFromPath(customImages, bannerPath).isValid():
            return _IMAGES_PATH_PREFIX.format(bundle.type)
    return _IMAGES_PATH_PREFIX.format(_DEFAULT_BUNDLE_TYPE)


def _getResourceFromPath(resource, path):
    for part in path:
        resource = resource.dyn(part)

    return resource
