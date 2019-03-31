# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/graphs/MessagesInterface.py
# Compiled at: 2011-06-08 20:25:48
from items import getTypeInfoByName, vehicles
from helpers import i18n
from gui import SystemMessages

class MessagesInterface(object):

    def _showMessageForVehicle(self, key, nationID, innationID, args=None, userString=None, type=SystemMessages.SM_TYPE.Error):
        key = '#system_messages:vehicleComponents/{0:>s}'.format(key)
        if args is None:
            args = {}
        if userString is not None:
            args.update({'userString': userString})
        else:
            vehicle = vehicles.g_cache.vehicle(nationID, innationID)
            args.update({'userString': vehicle.userString if vehicle is not None else 'N/A'})
        SystemMessages.pushMessage(i18n.makeString(key, **args), type=type)
        return

    def _showMessageForModule(self, key, itemTypeName, itemCompDescr, args=None, type=SystemMessages.SM_TYPE.Error):
        key = '#system_messages:vehicleComponents/{0:>s}'.format(key)
        if args is None:
            args = {}
        args.update({'typeString': getTypeInfoByName(itemTypeName)['userString'],
         'userString': vehicles.getDictDescr(itemCompDescr)['userString']})
        SystemMessages.pushMessage(i18n.makeString(key, **args), type=type)
        return
