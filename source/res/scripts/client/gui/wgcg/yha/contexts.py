# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/yha/contexts.py
import typing
from gui.clans import items
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
from shared_utils import makeTupleByDict, first

class YhaVideoCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.YHA_VIDEO

    def isAuthorizationRequired(self):
        return False

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    @classmethod
    def getDataObj(cls, incomeData):
        if incomeData:
            data = first(incomeData.get('data', ()), {})
            return makeTupleByDict(items.YhaVideoData, data)
        return cls.getDefDataObj()

    @staticmethod
    def getDefDataObj():
        return items.YhaVideoData()
