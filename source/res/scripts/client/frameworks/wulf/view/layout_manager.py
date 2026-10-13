# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/layout_manager.py
from __future__ import absolute_import
import logging
import typing
from collections import defaultdict
from future.utils import viewitems, viewvalues
from ..py_object_binder import PyObjectEntity
if typing.TYPE_CHECKING:
    from typing import Dict
_logger = logging.getLogger(__name__)

class LayoutManager(PyObjectEntity):

    def __init__(self, *args, **kwargs):
        super(LayoutManager, self).__init__(*args, **kwargs)
        self.__layouts = defaultdict(dict)

    @classmethod
    def create(cls, proxy):
        manager = LayoutManager()
        manager.bind(proxy)
        return manager

    def createAbsoluteLayout(self, appNS, layoutName):
        if self.__layouts[appNS].get(layoutName):
            _logger.warning('Layout %s for APP name space %s already exists, keeping the existing one.', layoutName, appNS)
            return
        else:
            layoutID = 0
            if self.proxy is not None:
                layoutID = self.proxy.createAbsoluteLayout()
            self.__layouts[appNS][layoutName] = layoutID
            return

    def getLayoutByName(self, appNS, layoutName):
        return self.__layouts[appNS].get(layoutName, 0)

    def destroyLayouts(self, appNS):
        if self.proxy is None:
            _logger.error('LayoutManager is unbound with proxy.')
            return
        else:
            for layoutID in viewvalues(self.__layouts.pop(appNS, {})):
                self.proxy.destroyLayout(layoutID)

            return

    def destroy(self):
        if self.proxy is None:
            _logger.error('LayoutManager has lost its proxy before destroy, %d layouts are leaked.', len(self.__layouts))
            self.__layouts.clear()
            return
        else:
            for appNS, layouts in viewitems(self.__layouts):
                if layouts:
                    _logger.warning('Layouts storage for app name space %s is not empty', appNS)
                for layoutID in viewvalues(layouts):
                    self.proxy.destroyLayout(layoutID)

            self.__layouts.clear()
            self.proxy.pyClear()
            self.unbind()
            return
