# Embedded file name: scripts/client/TmpConsoleCmds.py
import BigWorld
from debug_utils import *

class LanServers:

    def search(self):
        BigWorld.serverDiscovery.searching = 1

    def stop(self):
        BigWorld.serverDiscovery.searching = 0

    def show(self):
        for server in BigWorld.serverDiscovery.servers:
            print server

    def searchAndConnect(self, owner, user):
        self.search()
        self.__owner = owner
        self.__user = user
        BigWorld.serverDiscovery.changeNotifier = self.__checkIfFound

    def __checkIfFound(self):
        for server in BigWorld.serverDiscovery.servers:
            if server.ownerName == self.__owner:
                self.__host = server.serverString
                del self.__owner
                self.stop()
                self.__login()
                break

    def __login(self):

        class LoginInfo:
            pass

        login = LoginInfo()
        login.username = self.__user
        BigWorld.connect(self.__host, login, self.__progressFn)

    def __progressFn(self, stage, status, serverMsg):
        print stage, status, serverMsg


def printPeriodTime():
    arena = BigWorld.player().arena
    print '%f / %f' % (arena.periodEndTime - BigWorld.serverTime(), arena.periodLength)


def printStatistics(byTotal = False, bots = True):
    statistics = BigWorld.player().arena.statistics
    teams = (None, [], [])
    for (name, team), stats in statistics.iteritems():
        if bots or not name.startswith('Bot'):
            teams[team].append((name, stats))

    key = 'totalFrags' if byTotal else 'frags'
    teams[1].sort(lambda x, y: cmp(x[1]['key'], y[1]['key']))
    teams[2].sort(lambda x, y: cmp(x[1]['key'], y[1]['key']))
    for i in xrange(1, 3):
        print 'Team %d\n' % i
        for name, stats in teams[i]:
            print '%s\t%d\t%d' % (name, stats['frags'], stats['totalFrags'])

    return


def printConst(module, prefix, value):
    mod = __import__(module)
    for c in dir(mod):
        if c.startswith(prefix) and getattr(mod, c) == value:
            print c
            return

    print 'Not found'
