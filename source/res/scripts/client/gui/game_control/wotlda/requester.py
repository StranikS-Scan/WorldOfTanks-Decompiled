# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wotlda/requester.py
import logging
from functools import partial
from BWUtil import AsyncReturn
from typing import Dict, Callable, Optional, Tuple, Set
import adisp
from gui.wgcg.loadouts_assistant.context import LoadoutsAssistantCtx, EasyTankEquipCtx, GenericLoadoutAssistanceCtx
from gui.game_control.wotlda.constants import SupportedWotldaLoadoutType
from gui.game_control.wotlda.response import WotldaResponse
from helpers import dependency
from helpers.time_utils import QUARTER
from skeletons.gui.web import IWebController
from wg_async import wg_async, await_callback, wg_await, BrokenPromiseError, TimeoutError, delay
_logger = logging.getLogger(__name__)

class WotldaRequester(object):
    MAX_REQUEST_RETRIES = 3
    _webController = dependency.descriptor(IWebController)

    def __init__(self):
        self._destroyed = False

    def destroy(self):
        self._destroyed = True
        _logger.debug('Wotlda requester destroyed.')

    @wg_async
    def getEasyTankEquipLoadouts(self, clientCacheUpdatedAt):
        context = EasyTankEquipCtx(clientCacheUpdatedAt=clientCacheUpdatedAt)
        _logger.debug('Requesting easy tank equip loadouts.')
        response = yield wg_await(self._getLoadouts(context))
        raise AsyncReturn(response)

    @wg_async
    def getSubscriptionLoadouts(self, clientCacheUpdatedAt, loadoutTypes):
        context = GenericLoadoutAssistanceCtx(clientCacheUpdatedAt=clientCacheUpdatedAt)
        context.addLoadoutTypes(loadoutTypes)
        _logger.debug('Requesting equipment for %s ', context.getLoadoutTypesForRequest())
        response = yield wg_await(self._getLoadouts(context))
        if response.isSuccess():
            _logger.debug('Loadouts obtained, result = %s', response.getData())
        raise AsyncReturn(response)

    @wg_async
    def _getLoadouts(self, context):
        retries = self.MAX_REQUEST_RETRIES
        response = WotldaResponse(None)
        try:
            while retries > 0 and not self._destroyed:
                response = yield await_callback(partial(self._requestLoadouts, context))()
                if not response.isServiceUnavailable():
                    break
                retries -= 1
                yield delay(QUARTER)

        except TimeoutError as e:
            _logger.debug('Request session timout reached.')
            response.setException(e)
        except BrokenPromiseError as e:
            _logger.debug('Broken promise error.')
            response.setException(e)
        except Exception as e:
            _logger.debug('Failed to get loadouts data.')
            response.setException(e)

        raise AsyncReturn(response)
        return

    @adisp.adisp_process
    def _requestLoadouts(self, context, callback):
        response = yield self._webController.sendRequest(ctx=context)
        wotldaResponse = WotldaResponse(response)
        callback(wotldaResponse)
