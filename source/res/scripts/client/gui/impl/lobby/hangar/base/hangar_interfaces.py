# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/base/hangar_interfaces.py
from __future__ import absolute_import
import typing
from gui.shared.utils.requesters import RequestCriteria
if typing.TYPE_CHECKING:
    from Event import Event
    from gui.shared.gui_items import Vehicle

class IVehicleFilter(object):
    onDiff = None

    @property
    def criteria(self):
        raise NotImplementedError

    @property
    def vehicles(self):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError


class IAccountStyles(object):
    onChanged = None

    @property
    def criteria(self):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError
