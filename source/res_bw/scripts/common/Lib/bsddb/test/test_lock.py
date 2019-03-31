# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/bsddb/test/test_lock.py
# Compiled at: 2010-05-25 20:46:16
"""
TestCases for testing the locking sub-system.
"""
import time
import unittest
from test_all import db, test_support, verbose, have_threads, get_new_environment_path, get_new_database_path
if have_threads:
    from threading import Thread
    import sys
    if sys.version_info[0] < 3:
        from threading import currentThread
    else:
        from threading import current_thread as currentThread

class LockingTestCase(unittest.TestCase):
    import sys
    if sys.version_info[:3] < (2, 4, 0):

        def assertTrue(self, expr, msg=None):
            self.failUnless(expr, msg=msg)

    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()
        self.env.open(self.homeDir, db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_CREATE)

    def tearDown(self):
        self.env.close()
        test_support.rmtree(self.homeDir)

    def test01_simple(self):
        if verbose:
            print '\n', '-=' * 30
            print 'Running %s.test01_simple...' % self.__class__.__name__
        anID = self.env.lock_id()
        if verbose:
            print 'locker ID: %s' % anID
        lock = self.env.lock_get(anID, 'some locked thing', db.DB_LOCK_WRITE)
        if verbose:
            print 'Aquired lock: %s' % lock
        self.env.lock_put(lock)
        if verbose:
            print 'Released lock: %s' % lock
        self.env.lock_id_free(anID)

    def test02_threaded(self):
        if verbose:
            print '\n', '-=' * 30
            print 'Running %s.test02_threaded...' % self.__class__.__name__
        threads = []
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_WRITE,)))
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_READ,)))
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_READ,)))
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_WRITE,)))
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_READ,)))
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_READ,)))
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_WRITE,)))
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_WRITE,)))
        threads.append(Thread(target=self.theThread, args=(db.DB_LOCK_WRITE,)))
        for t in threads:
            import sys
            if sys.version_info[0] < 3:
                t.setDaemon(True)
            else:
                t.daemon = True
            t.start()

        for t in threads:
            t.join()

    def test03_lock_timeout(self):
        self.env.set_timeout(0, db.DB_SET_LOCK_TIMEOUT)
        self.env.set_timeout(0, db.DB_SET_TXN_TIMEOUT)
        self.env.set_timeout(123456, db.DB_SET_LOCK_TIMEOUT)
        self.env.set_timeout(7890123, db.DB_SET_TXN_TIMEOUT)

        def deadlock_detection--- This code section failed: ---

  99       0	SETUP_LOOP        '82'
           3	LOAD_DEREF        'deadlock_detection'
           6	LOAD_ATTR         'end'
           9	JUMP_IF_TRUE      '81'

 101      12	LOAD_DEREF        'self'
          15	LOAD_ATTR         'env'
          18	LOAD_ATTR         'lock_detect'
          21	LOAD_GLOBAL       'db'
          24	LOAD_ATTR         'DB_LOCK_EXPIRE'
          27	CALL_FUNCTION_1   ''
          30	LOAD_DEREF        'deadlock_detection'
          33	STORE_ATTR        'count'

 102      36	LOAD_DEREF        'deadlock_detection'
          39	LOAD_ATTR         'count'
          42	JUMP_IF_FALSE     '65'

 103      45	SETUP_LOOP        '61'
          48	LOAD_DEREF        'deadlock_detection'
          51	LOAD_ATTR         'end'
          54	JUMP_IF_TRUE      '60'

 104      57	JUMP_BACK         '48'
          60	POP_BLOCK         ''
        61_0	COME_FROM         '45'

 105      61	BREAK_LOOP        ''
          62	JUMP_FORWARD      '65'
        65_0	COME_FROM         '62'

 106      65	LOAD_GLOBAL       'time'
          68	LOAD_ATTR         'sleep'
          71	LOAD_CONST        0.01
          74	CALL_FUNCTION_1   ''
          77	POP_TOP           ''
          78	JUMP_BACK         '3'
          81	POP_BLOCK         ''
        82_0	COME_FROM         '0'

Syntax error at or near 'POP_BLOCK' token at offset 60

        deadlock_detection.end = False
        deadlock_detection.count = 0
        t = Thread(target=deadlock_detection)
        import sys
        if sys.version_info[0] < 3:
            t.setDaemon(True)
        else:
            t.daemon = True
        t.start()
        self.env.set_timeout(100000, db.DB_SET_LOCK_TIMEOUT)
        anID = self.env.lock_id()
        anID2 = self.env.lock_id()
        self.assertNotEqual(anID, anID2)
        lock = self.env.lock_get(anID, 'shared lock', db.DB_LOCK_WRITE)
        start_time = time.time()
        self.assertRaises(db.DBLockNotGrantedError, self.env.lock_get, anID2, 'shared lock', db.DB_LOCK_READ)
        end_time = time.time()
        deadlock_detection.end = True
        self.assertTrue(end_time - start_time >= 0.0999)
        self.env.lock_put(lock)
        t.join()
        self.env.lock_id_free(anID)
        self.env.lock_id_free(anID2)
        if db.version() >= (4, 6):
            self.assertTrue(deadlock_detection.count > 0)

    def theThread(self, lockType):
        import sys
        if sys.version_info[0] < 3:
            name = currentThread().getName()
        else:
            name = currentThread().name
        if lockType == db.DB_LOCK_WRITE:
            lt = 'write'
        else:
            lt = 'read'
        anID = self.env.lock_id()
        if verbose:
            print '%s: locker ID: %s' % (name, anID)
        for i in xrange(1000):
            lock = self.env.lock_get(anID, 'some locked thing', lockType)
            if verbose:
                print '%s: Aquired %s lock: %s' % (name, lt, lock)
            self.env.lock_put(lock)
            if verbose:
                print '%s: Released %s lock: %s' % (name, lt, lock)

        self.env.lock_id_free(anID)


def test_suite():
    suite = unittest.TestSuite()
    if have_threads:
        suite.addTest(unittest.makeSuite(LockingTestCase))
    else:
        suite.addTest(unittest.makeSuite(LockingTestCase, 'test01'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')