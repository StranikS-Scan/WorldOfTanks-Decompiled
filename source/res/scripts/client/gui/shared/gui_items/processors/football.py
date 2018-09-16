# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/football.py
import BigWorld
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess
from gui.SystemMessages import SM_TYPE
from debug_utils import LOG_DEBUG
from helpers import dependency
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class PacketsOpener(Processor):

    def _request(self, callback):
        LOG_DEBUG('Make server request to open football packets')
        BigWorld.player().inventory.fb18OpenPackets(lambda code: self._response(code, callback))


class BuffonRecruiter(Processor):
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, vehicleIntCD):
        super(BuffonRecruiter, self).__init__()
        self.vehicleIntCD = vehicleIntCD

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('recruit_window/%s' % errStr, defaultSysMsgKey='recruit_window/server_error', auxData=ctx)

    def _successHandler(self, code, ctx=None):
        tankman = self.itemsFactory.createTankman(ctx.get('tman'))
        vehicle = self.itemsFactory.createVehicle(typeCompDescr=self.vehicleIntCD)
        return makeI18nSuccess('football_recruit_window/success', type=SM_TYPE.Information, rank=tankman.rankUserName, name=tankman.fullUserName, role=tankman.roleUserName, vehicle=vehicle.shortUserName)

    def _request(self, callback):
        LOG_DEBUG('Make server request to recruit buffon')
        BigWorld.player().inventory.fb18RecruitBuffon(self.vehicleIntCD, lambda code, ctx: self._response(code, callback, ctx=ctx))
