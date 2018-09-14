# Embedded file name: scripts/common/unit_helpers/ExtrasHandler.py
import cPickle

class EmptyExtrasHandler(object):

    def __init__(self, unit):
        pass

    def new(self):
        return {}

    def pack(self, extras):
        return ''

    def unpack(self, extrasStr):
        return None

    def onUnitExtrasUpdate(self, extras, updateStr):
        pass


class FortBattleExtrasHandler(EmptyExtrasHandler):

    def __init__(self, unit):
        self._unit = unit
        from unit_helpers.MsgProcessor import FortBattleMgrMsgProcessor
        self._processor = FortBattleMgrMsgProcessor(unit)

    def new(self):
        return {'isBattleReound': 0,
         'prevBuildNum': 0,
         'currentBuildNum': 0,
         'roundStart': 0,
         'battleResultList': [],
         'isEnemyReadyForBattle': 0}

    def pack(self, extras):
        return cPickle.dumps(extras, -1)

    def unpack(self, extrasStr):
        return cPickle.loads(extrasStr)

    def onUnitExtrasUpdate(self, extras, updateStr):
        self._processor.unpackOps(updateStr)


class ClubExtrasHandler(EmptyExtrasHandler):

    def __init__(self, unit):
        self._unit = unit

    def new(self):
        return {'mapID': None,
         'isEnemyReady': False}

    def pack(self, extras):
        return cPickle.dumps(extras, -1)

    def unpack(self, extrasStr):
        return cPickle.loads(extrasStr)

    def onUnitExtrasUpdate(self, extras, updateStr):
        extras.update(cPickle.loads(updateStr))
