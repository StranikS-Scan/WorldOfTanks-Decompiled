# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/models/common.py
from __future__ import absolute_import
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PeriodInfo
from gui.shared.utils.decorators import ReprInjector
from season_common import GameSeason

@ReprInjector.simple('state', 'rightBorder', 'primeDelta', 'endTime')
class FunSubModesStatus(object):
    __slots__ = ('state', 'rightBorder', 'primeDelta', 'endTime')

    def __init__(self, state, rightBorder=None, primeDelta=None, endTime=None):
        self.rightBorder = rightBorder if rightBorder is not None else -1
        self.primeDelta = primeDelta if primeDelta is not None else 0
        self.endTime = endTime if endTime is not None else -1
        self.state = state
        return


class FunRandomSeason(GameSeason):

    def __init__(self, cycleInfo, seasonData, assetsPointer):
        super(FunRandomSeason, self).__init__(cycleInfo, seasonData)
        self.__assetsPointer = assetsPointer

    def getUserName(self):
        defaultLocRes = R.strings.fun_random.sub_modes.undefined
        return backport.text(R.strings.fun_random.sub_modes.dyn(self.__assetsPointer, defaultLocRes).userName())


class FunPeriodInfo(PeriodInfo, FunAssetPacksMixin):

    def getVO(self, withBNames=False, withBDeltas=False, deltaFmt=None, timeFmt=None, dateFmt=None):
        res = super(FunPeriodInfo, self).getVO(withBNames, withBDeltas, deltaFmt, timeFmt, dateFmt)
        res['leftDetailedSeasonName'] = self.getModeDetailedUserName(subModeName=res.get('leftSeasonName', ''))
        return res
