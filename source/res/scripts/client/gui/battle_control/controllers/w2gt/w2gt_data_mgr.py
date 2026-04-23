# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/w2gt/w2gt_data_mgr.py
from collections import namedtuple
import typing
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, List, Tuple
    from helpers.server_settings import _W2GTConfig
    from gui.game_control.w2gt_controller import _W2gtResponseData

class _ZoneTags(object):
    BRAWLING = 'brawling'
    AMBUSH = 'ambush'
    UNIVERSAL = 'universal'
    RECON = 'recon'
    ARTILLERY = 'artillery'
    UNKNOWN = 'unknown'
    ALL = (BRAWLING,
     AMBUSH,
     UNIVERSAL,
     RECON,
     ARTILLERY)


_ZONE_TYPE_MAP = {_ZoneTags.BRAWLING: 'brawling',
 _ZoneTags.AMBUSH: 'ambush',
 _ZoneTags.UNIVERSAL: 'universal',
 _ZoneTags.RECON: 'recon',
 _ZoneTags.ARTILLERY: 'artillery',
 _ZoneTags.UNKNOWN: 'unknown'}

class W2gtProgress(namedtuple('W2gtProgress', ('stageID', 'startTime', 'ctx'))):

    def __new__(cls, **kwargs):
        defaults = dict(stageID=None, startTime=None, ctx=None)
        defaults.update(kwargs)
        return super(W2gtProgress, cls).__new__(cls, **defaults)

    @property
    def isCapable(self):
        return self.stageID is not None and self.ctx is not None

    def asDict(self):
        return self._asdict()

    def replace(self, **kwargs):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in kwargs.items() if k in allowedFields))
        if self.stageID == dataToUpdate.get('stageID') and 'startTime' in dataToUpdate:
            del dataToUpdate['startTime']
        return self._replace(**dataToUpdate)


class W2GTDataMgr(object):

    def __init__(self):
        self.__progress = None
        self.__w2gtConfig = None
        self.__zones = None
        return

    def init(self, data, progress, w2gtConfig):
        self.__progress = progress
        self.__w2gtConfig = w2gtConfig
        self.__readData(data.data)

    def __readData(self, data):
        self.__zones = self.__readZones(data)

    @property
    def progress(self):
        return self.__progress

    @property
    def zones(self):
        return self.__zones.values()

    @property
    def config(self):
        return self.__w2gtConfig

    def destroy(self):
        self.__progress = None
        self.__zones.clear()
        self.__zones = None
        self.__w2gtConfig = None
        return

    def __readZones(self, data):
        return {zone.get('id'):_BattleZone(zone.get('id'), zone) for zone in data.get('battle_zones', [])}


class _BattleZone(object):

    def __init__(self, zoneID, ctx):
        self.__id = zoneID
        self.__tags = self._readTags(ctx)
        self.__zoneType = _ZONE_TYPE_MAP.get(self.__tags[0] if self.__tags else _ZoneTags.UNKNOWN)
        self.__area2D = ctx.get('contour', [])
        self.__center2D = ctx.get('center', [])

    @property
    def zoneID(self):
        return self.__id

    @property
    def zoneType(self):
        return self.__zoneType

    @property
    def area2D(self):
        return self.__area2D

    @property
    def center2D(self):
        return self.__center2D

    @staticmethod
    def _readTags(ctx):
        return [ tag for tag in ctx.get('tags', []) if tag in _ZoneTags.ALL ]
