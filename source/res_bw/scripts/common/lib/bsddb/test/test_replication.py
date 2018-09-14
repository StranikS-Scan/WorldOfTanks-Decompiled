# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/bsddb/test/test_replication.py
"""TestCases for distributed transactions.
"""
import os
import time
import unittest
from test_all import db, test_support, have_threads, verbose, get_new_environment_path, get_new_database_path

class DBReplication(unittest.TestCase):

    def setUp(self):
        self.homeDirMaster = get_new_environment_path()
        self.homeDirClient = get_new_environment_path()
        self.dbenvMaster = db.DBEnv()
        self.dbenvClient = db.DBEnv()
        self.dbenvMaster.open(self.homeDirMaster, db.DB_CREATE | db.DB_INIT_TXN | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_INIT_REP | db.DB_RECOVER | db.DB_THREAD, 438)
        self.dbenvClient.open(self.homeDirClient, db.DB_CREATE | db.DB_INIT_TXN | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_INIT_REP | db.DB_RECOVER | db.DB_THREAD, 438)
        self.confirmed_master = self.client_startupdone = False

        def confirmed_master(a, b, c):
            if b == db.DB_EVENT_REP_MASTER:
                self.confirmed_master = True

        def client_startupdone(a, b, c):
            if b == db.DB_EVENT_REP_STARTUPDONE:
                self.client_startupdone = True

        self.dbenvMaster.set_event_notify(confirmed_master)
        self.dbenvClient.set_event_notify(client_startupdone)
        self.dbMaster = self.dbClient = None
        return

    def tearDown(self):
        if self.dbClient:
            self.dbClient.close()
        if self.dbMaster:
            self.dbMaster.close()

        def dummy(*args):
            pass

        self.dbenvMaster.set_event_notify(dummy)
        self.dbenvClient.set_event_notify(dummy)
        self.dbenvClient.close()
        self.dbenvMaster.close()
        test_support.rmtree(self.homeDirClient)
        test_support.rmtree(self.homeDirMaster)


class DBReplicationManager(DBReplication):

    def test01_basic_replication(self):
        master_port = test_support.find_unused_port()
        client_port = test_support.find_unused_port()
        if db.version() >= (5, 2):
            self.site = self.dbenvMaster.repmgr_site('127.0.0.1', master_port)
            self.site.set_config(db.DB_GROUP_CREATOR, True)
            self.site.set_config(db.DB_LOCAL_SITE, True)
            self.site2 = self.dbenvMaster.repmgr_site('127.0.0.1', client_port)
            self.site3 = self.dbenvClient.repmgr_site('127.0.0.1', master_port)
            self.site3.set_config(db.DB_BOOTSTRAP_HELPER, True)
            self.site4 = self.dbenvClient.repmgr_site('127.0.0.1', client_port)
            self.site4.set_config(db.DB_LOCAL_SITE, True)
            d = {db.DB_BOOTSTRAP_HELPER: [False,
                                      False,
                                      True,
                                      False],
             db.DB_GROUP_CREATOR: [True,
                                   False,
                                   False,
                                   False],
             db.DB_LEGACY: [False,
                            False,
                            False,
                            False],
             db.DB_LOCAL_SITE: [True,
                                False,
                                False,
                                True],
             db.DB_REPMGR_PEER: [False,
                                 False,
                                 False,
                                 False]}
            for i, j in d.items():
                for k, v in zip([self.site,
                 self.site2,
                 self.site3,
                 self.site4], j):
                    if v:
                        self.assertTrue(k.get_config(i))
                    else:
                        self.assertFalse(k.get_config(i))

            self.assertNotEqual(self.site.get_eid(), self.site2.get_eid())
            self.assertNotEqual(self.site3.get_eid(), self.site4.get_eid())
            for i, j in zip([self.site,
             self.site2,
             self.site3,
             self.site4], [master_port,
             client_port,
             master_port,
             client_port]):
                addr = i.get_address()
                self.assertEqual(addr, ('127.0.0.1', j))

            for i in [self.site, self.site2]:
                self.assertEqual(i.get_address(), self.dbenvMaster.repmgr_site_by_eid(i.get_eid()).get_address())

            for i in [self.site3, self.site4]:
                self.assertEqual(i.get_address(), self.dbenvClient.repmgr_site_by_eid(i.get_eid()).get_address())

        else:
            self.dbenvMaster.repmgr_set_local_site('127.0.0.1', master_port)
            self.dbenvClient.repmgr_set_local_site('127.0.0.1', client_port)
            self.dbenvMaster.repmgr_add_remote_site('127.0.0.1', client_port)
            self.dbenvClient.repmgr_add_remote_site('127.0.0.1', master_port)
            self.dbenvMaster.rep_set_nsites(2)
            self.dbenvClient.rep_set_nsites(2)
        self.dbenvMaster.rep_set_priority(10)
        self.dbenvClient.rep_set_priority(0)
        self.dbenvMaster.rep_set_timeout(db.DB_REP_CONNECTION_RETRY, 100123)
        self.dbenvClient.rep_set_timeout(db.DB_REP_CONNECTION_RETRY, 100321)
        self.assertEqual(self.dbenvMaster.rep_get_timeout(db.DB_REP_CONNECTION_RETRY), 100123)
        self.assertEqual(self.dbenvClient.rep_get_timeout(db.DB_REP_CONNECTION_RETRY), 100321)
        self.dbenvMaster.rep_set_timeout(db.DB_REP_ELECTION_TIMEOUT, 100234)
        self.dbenvClient.rep_set_timeout(db.DB_REP_ELECTION_TIMEOUT, 100432)
        self.assertEqual(self.dbenvMaster.rep_get_timeout(db.DB_REP_ELECTION_TIMEOUT), 100234)
        self.assertEqual(self.dbenvClient.rep_get_timeout(db.DB_REP_ELECTION_TIMEOUT), 100432)
        self.dbenvMaster.rep_set_timeout(db.DB_REP_ELECTION_RETRY, 100345)
        self.dbenvClient.rep_set_timeout(db.DB_REP_ELECTION_RETRY, 100543)
        self.assertEqual(self.dbenvMaster.rep_get_timeout(db.DB_REP_ELECTION_RETRY), 100345)
        self.assertEqual(self.dbenvClient.rep_get_timeout(db.DB_REP_ELECTION_RETRY), 100543)
        self.dbenvMaster.repmgr_set_ack_policy(db.DB_REPMGR_ACKS_ALL)
        self.dbenvClient.repmgr_set_ack_policy(db.DB_REPMGR_ACKS_ALL)
        self.dbenvMaster.repmgr_start(1, db.DB_REP_MASTER)
        self.dbenvClient.repmgr_start(1, db.DB_REP_CLIENT)
        self.assertEqual(self.dbenvMaster.rep_get_nsites(), 2)
        self.assertEqual(self.dbenvClient.rep_get_nsites(), 2)
        self.assertEqual(self.dbenvMaster.rep_get_priority(), 10)
        self.assertEqual(self.dbenvClient.rep_get_priority(), 0)
        self.assertEqual(self.dbenvMaster.repmgr_get_ack_policy(), db.DB_REPMGR_ACKS_ALL)
        self.assertEqual(self.dbenvClient.repmgr_get_ack_policy(), db.DB_REPMGR_ACKS_ALL)
        import time
        timeout = time.time() + 60
        while time.time() < timeout and not (self.confirmed_master and self.client_startupdone):
            time.sleep(0.02)

        if time.time() > timeout:
            import sys
            print >> sys.stderr, 'XXX: timeout happened beforestartup was confirmed - see issue 3892'
            startup_timeout = True
        d = self.dbenvMaster.repmgr_site_list()
        self.assertEqual(len(d), 1)
        d = d.values()[0]
        self.assertEqual(d[0], '127.0.0.1')
        self.assertEqual(d[1], client_port)
        self.assertTrue(d[2] == db.DB_REPMGR_CONNECTED or d[2] == db.DB_REPMGR_DISCONNECTED)
        d = self.dbenvClient.repmgr_site_list()
        self.assertEqual(len(d), 1)
        d = d.values()[0]
        self.assertEqual(d[0], '127.0.0.1')
        self.assertEqual(d[1], master_port)
        self.assertTrue(d[2] == db.DB_REPMGR_CONNECTED or d[2] == db.DB_REPMGR_DISCONNECTED)
        if db.version() >= (4, 6):
            d = self.dbenvMaster.repmgr_stat(flags=db.DB_STAT_CLEAR)
            self.assertTrue('msgs_queued' in d)
        self.dbMaster = db.DB(self.dbenvMaster)
        txn = self.dbenvMaster.txn_begin()
        self.dbMaster.open('test', db.DB_HASH, db.DB_CREATE, 438, txn=txn)
        txn.commit()
        import time, os.path
        timeout = time.time() + 10
        while time.time() < timeout and not os.path.exists(os.path.join(self.homeDirClient, 'test')):
            time.sleep(0.01)

        self.dbClient = db.DB(self.dbenvClient)
        while True:
            txn = self.dbenvClient.txn_begin()
            try:
                self.dbClient.open('test', db.DB_HASH, flags=db.DB_RDONLY, mode=438, txn=txn)
            except db.DBRepHandleDeadError:
                txn.abort()
                self.dbClient.close()
                self.dbClient = db.DB(self.dbenvClient)
                continue

            txn.commit()
            break

        txn = self.dbenvMaster.txn_begin()
        self.dbMaster.put('ABC', '123', txn=txn)
        txn.commit()
        import time
        timeout = time.time() + 10
        v = None
        while time.time() < timeout and v is None:
            txn = self.dbenvClient.txn_begin()
            v = self.dbClient.get('ABC', txn=txn)
            txn.commit()
            if v is None:
                time.sleep(0.02)

        if time.time() >= timeout and startup_timeout:
            self.skipTest('replication test skipped due to random failure, see issue 3892')
        self.assertTrue(time.time() < timeout)
        self.assertEqual('123', v)
        txn = self.dbenvMaster.txn_begin()
        self.dbMaster.delete('ABC', txn=txn)
        txn.commit()
        timeout = time.time() + 10
        while time.time() < timeout and v is not None:
            txn = self.dbenvClient.txn_begin()
            v = self.dbClient.get('ABC', txn=txn)
            txn.commit()
            if v is None:
                time.sleep(0.02)

        self.assertTrue(time.time() < timeout)
        self.assertEqual(None, v)
        return


class DBBaseReplication(DBReplication):

    def setUp(self):
        DBReplication.setUp(self)

        def confirmed_master(a, b, c):
            if b == db.DB_EVENT_REP_MASTER or b == db.DB_EVENT_REP_ELECTED:
                self.confirmed_master = True

        def client_startupdone(a, b, c):
            if b == db.DB_EVENT_REP_STARTUPDONE:
                self.client_startupdone = True

        self.dbenvMaster.set_event_notify(confirmed_master)
        self.dbenvClient.set_event_notify(client_startupdone)
        import Queue
        self.m2c = Queue.Queue()
        self.c2m = Queue.Queue()

        def m2c(dbenv, control, rec, lsnp, envid, flags):
            self.m2c.put((control, rec))

        def c2m(dbenv, control, rec, lsnp, envid, flags):
            self.c2m.put((control, rec))

        self.dbenvMaster.rep_set_transport(13, m2c)
        self.dbenvMaster.rep_set_priority(10)
        self.dbenvClient.rep_set_transport(3, c2m)
        self.dbenvClient.rep_set_priority(0)
        self.assertEqual(self.dbenvMaster.rep_get_priority(), 10)
        self.assertEqual(self.dbenvClient.rep_get_priority(), 0)

        def thread_master():
            return self.thread_do(self.dbenvMaster, self.c2m, 3, self.master_doing_election, True)

        def thread_client():
            return self.thread_do(self.dbenvClient, self.m2c, 13, self.client_doing_election, False)

        from threading import Thread
        t_m = Thread(target=thread_master)
        t_c = Thread(target=thread_client)
        import sys
        if sys.version_info[0] < 3:
            t_m.setDaemon(True)
            t_c.setDaemon(True)
        else:
            t_m.daemon = True
            t_c.daemon = True
        self.t_m = t_m
        self.t_c = t_c
        self.dbMaster = self.dbClient = None
        self.master_doing_election = [False]
        self.client_doing_election = [False]
        return

    def tearDown(self):
        if self.dbClient:
            self.dbClient.close()
        if self.dbMaster:
            self.dbMaster.close()
        self.m2c.put(None)
        self.c2m.put(None)
        self.t_m.join()
        self.t_c.join()

        def dummy(*args):
            pass

        self.dbenvMaster.set_event_notify(dummy)
        self.dbenvClient.set_event_notify(dummy)
        self.dbenvMaster.rep_set_transport(13, dummy)
        self.dbenvClient.rep_set_transport(3, dummy)
        self.dbenvClient.close()
        self.dbenvMaster.close()
        test_support.rmtree(self.homeDirClient)
        test_support.rmtree(self.homeDirMaster)
        return

    def basic_rep_threading(self):
        self.dbenvMaster.rep_start(flags=db.DB_REP_MASTER)
        self.dbenvClient.rep_start(flags=db.DB_REP_CLIENT)

        def thread_do(env, q, envid, election_status, must_be_master):
            while True:
                v = q.get()
                if v is None:
                    return
                env.rep_process_message(v[0], v[1], envid)

            return

        self.thread_do = thread_do
        self.t_m.start()
        self.t_c.start()

    def test01_basic_replication(self):
        self.basic_rep_threading()
        import time
        timeout = time.time() + 60
        while time.time() < timeout and not (self.confirmed_master and self.client_startupdone):
            time.sleep(0.02)

        self.assertTrue(time.time() < timeout)
        self.dbMaster = db.DB(self.dbenvMaster)
        txn = self.dbenvMaster.txn_begin()
        self.dbMaster.open('test', db.DB_HASH, db.DB_CREATE, 438, txn=txn)
        txn.commit()
        import time, os.path
        timeout = time.time() + 10
        while time.time() < timeout and not os.path.exists(os.path.join(self.homeDirClient, 'test')):
            time.sleep(0.01)

        self.dbClient = db.DB(self.dbenvClient)
        while True:
            txn = self.dbenvClient.txn_begin()
            try:
                self.dbClient.open('test', db.DB_HASH, flags=db.DB_RDONLY, mode=438, txn=txn)
            except db.DBRepHandleDeadError:
                txn.abort()
                self.dbClient.close()
                self.dbClient = db.DB(self.dbenvClient)
                continue

            txn.commit()
            break

        d = self.dbenvMaster.rep_stat(flags=db.DB_STAT_CLEAR)
        self.assertTrue('master_changes' in d)
        txn = self.dbenvMaster.txn_begin()
        self.dbMaster.put('ABC', '123', txn=txn)
        txn.commit()
        import time
        timeout = time.time() + 10
        v = None
        while time.time() < timeout and v is None:
            txn = self.dbenvClient.txn_begin()
            v = self.dbClient.get('ABC', txn=txn)
            txn.commit()
            if v is None:
                time.sleep(0.02)

        self.assertTrue(time.time() < timeout)
        self.assertEqual('123', v)
        txn = self.dbenvMaster.txn_begin()
        self.dbMaster.delete('ABC', txn=txn)
        txn.commit()
        timeout = time.time() + 10
        while time.time() < timeout and v is not None:
            txn = self.dbenvClient.txn_begin()
            v = self.dbClient.get('ABC', txn=txn)
            txn.commit()
            if v is None:
                time.sleep(0.02)

        self.assertTrue(time.time() < timeout)
        self.assertEqual(None, v)
        return

    if db.version() >= (4, 7):

        def test02_test_request(self):
            self.basic_rep_threading()
            minimum, maximum = self.dbenvClient.rep_get_request()
            self.dbenvClient.rep_set_request(minimum - 1, maximum + 1)
            self.assertEqual(self.dbenvClient.rep_get_request(), (minimum - 1, maximum + 1))

    if db.version() >= (4, 6):

        def test03_master_election(self):
            self.dbenvMaster.rep_start(flags=db.DB_REP_CLIENT)
            self.dbenvClient.rep_start(flags=db.DB_REP_CLIENT)

            def thread_do(env, q, envid, election_status, must_be_master):
                while True:
                    v = q.get()
                    if v is None:
                        return
                    r = env.rep_process_message(v[0], v[1], envid)
                    if must_be_master and self.confirmed_master:
                        self.dbenvMaster.rep_start(flags=db.DB_REP_MASTER)
                        must_be_master = False
                    if r[0] == db.DB_REP_HOLDELECTION:

                        def elect():
                            while True:
                                try:
                                    env.rep_elect(2, 1)
                                    election_status[0] = False
                                    break
                                except db.DBRepUnavailError:
                                    pass

                        if not election_status[0] and not self.confirmed_master:
                            from threading import Thread
                            election_status[0] = True
                            t = Thread(target=elect)
                            import sys
                            if sys.version_info[0] < 3:
                                t.setDaemon(True)
                            else:
                                t.daemon = True
                            t.start()

                return

            self.thread_do = thread_do
            self.t_m.start()
            self.t_c.start()
            self.dbenvMaster.rep_set_timeout(db.DB_REP_ELECTION_TIMEOUT, 50000)
            self.dbenvClient.rep_set_timeout(db.DB_REP_ELECTION_TIMEOUT, 50000)
            self.client_doing_election[0] = True
            while True:
                try:
                    self.dbenvClient.rep_elect(2, 1)
                    self.client_doing_election[0] = False
                    break
                except db.DBRepUnavailError:
                    pass

            self.assertTrue(self.confirmed_master)
            while not self.dbenvClient.rep_stat()['startup_complete']:
                pass

    if db.version() >= (4, 7):

        def test04_test_clockskew(self):
            fast, slow = (1234, 1230)
            self.dbenvMaster.rep_set_clockskew(fast, slow)
            self.assertEqual((fast, slow), self.dbenvMaster.rep_get_clockskew())
            self.basic_rep_threading()


def test_suite():
    suite = unittest.TestSuite()
    if db.version() >= (4, 6):
        dbenv = db.DBEnv()
        try:
            dbenv.repmgr_get_ack_policy()
            ReplicationManager_available = True
        except:
            ReplicationManager_available = False

        dbenv.close()
        del dbenv
        if ReplicationManager_available:
            suite.addTest(unittest.makeSuite(DBReplicationManager))
        if have_threads:
            suite.addTest(unittest.makeSuite(DBBaseReplication))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
