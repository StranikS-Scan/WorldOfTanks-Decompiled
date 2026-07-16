# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/unit_helpers/ExtrasHandler.py
from __future__ import absolute_import
from future.moves import pickle

class EmptyExtrasHandler(object):

    def __init__(self, unit):
        pass

    def new(self, initial=None):
        result = {}
        if initial:
            result.update(initial)
        return result

    def pack(self, extras):
        pass

    def unpack(self, extrasStr):
        return {}

    def reset(self, extras):
        return self.new()

    def updateUnitExtras(self, extras, updateStr):
        pass


class SimpleExtrasHandler(EmptyExtrasHandler):

    def pack(self, extras):
        return pickle.dumps(extras, -1)

    def unpack(self, extrasStr):
        return pickle.loads(extrasStr)

    def reset(self, extras):
        return extras

    def updateUnitExtras(self, extras, updateStr):
        update = pickle.loads(updateStr)
        extras.update(update)


class ClanBattleExtrasHandler(SimpleExtrasHandler):

    def __init__(self, unit=None):
        super(ClanBattleExtrasHandler, self).__init__(unit)
        self._unit = unit
        from unit_helpers.MsgProcessor import ClanBattleMgrMsgProcessor
        self._processor = ClanBattleMgrMsgProcessor(unit)

    def new(self, initial=None):
        result = {'battleID': 0,
         'scheduleTime': 0,
         'roundStart': 0,
         'battleResultList': [],
         'isEnemyReadyForBattle': 0,
         'clanEquipments': None,
         'lastEquipRev': 0,
         'localizedData': None}
        if initial:
            result.update(initial)
        return result

    def updateUnitExtras(self, extras, updateStr):
        self._processor.unpackOps(updateStr)


class SquadExtrasHandler(SimpleExtrasHandler):
    pass


class ExternalExtrasHandler(SimpleExtrasHandler):

    def new(self, initial=None):
        result = {'rev': 1}
        if initial:
            result.update(initial)
        return result
