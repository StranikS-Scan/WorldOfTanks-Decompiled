# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/web/w2c_api.py
from __future__ import absolute_import
import logging
from helpers import dependency
from open_bundle.gui.shared.event_dispatcher import showOpenBundleMainView
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from web.web_client_api.ui import OpenTabWebApi
_logger = logging.getLogger(__name__)

def registerOpenBundleWebApi():

    @dependency.replace_none_kwargs(openBundle=IOpenBundleController)
    def _showOpenBundle(_, cmd, openBundle=None):
        bundleID = cmd.custom_parameters.get('bundle_id', False)
        if openBundle.isBundleActive(bundleID=bundleID):
            showOpenBundleMainView(bundleID=bundleID)
        else:
            _logger.error('Bundle with ID: %s is not active', bundleID)

    OpenTabWebApi.addTabIdCallback('open_bundle', _showOpenBundle)
    return
