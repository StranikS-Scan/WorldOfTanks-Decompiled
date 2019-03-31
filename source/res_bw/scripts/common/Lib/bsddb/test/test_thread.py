# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/bsddb/test/test_thread.py
# Compiled at: 2010-05-25 20:46:16
"""TestCases for multi-threaded access to a DB.
"""
import os
import sys
import time
import errno
from random import random
DASH = '-'
try:
    WindowsError
except NameError:

    class WindowsError(Exception):
        pass


import unittest
from test_all import db, dbutils, test_support, verbose, have_threads, get_new_environment_path, get_new_database_path
if have_threads:
    from threading import Thread
    import sys
    if sys.version_info[0] < 3:
        from threading import currentThread
    else:
        from threading import current_thread as currentThread

class BaseThreadedTestCase(unittest.TestCase):
    dbtype = db.DB_UNKNOWN
    dbopenflags = 0
    dbsetflags = 0
    envflags = 0
    import sys
    if sys.version_info[:3] < (2, 4, 0):

        def assertTrue(self, expr, msg=None):
            self.failUnless(expr, msg=msg)

    def setUp(self):
        if verbose:
            dbutils._deadlock_VerboseFile = sys.stdout
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()
        self.setEnvOpts()
        self.env.open(self.homeDir, self.envflags | db.DB_CREATE)
        self.filename = self.__class__.__name__ + '.db'
        self.d = db.DB(self.env)
        if self.dbsetflags:
            self.d.set_flags(self.dbsetflags)
        self.d.open(self.filename, self.dbtype, self.dbopenflags | db.DB_CREATE)

    def tearDown(self):
        self.d.close()
        self.env.close()
        test_support.rmtree(self.homeDir)

    def setEnvOpts(self):
        pass

    def makeData(self, key):
        return DASH.join([key] * 5)


class ConcurrentDataStoreBase(BaseThreadedTestCase):
    dbopenflags = db.DB_THREAD
    envflags = db.DB_THREAD | db.DB_INIT_CDB | db.DB_INIT_MPOOL
    readers = 0
    writers = 0
    records = 1000

    def test01_1WriterMultiReaders(self):
        if verbose:
            print '\n', '-=' * 30
            print 'Running %s.test01_1WriterMultiReaders...' % self.__class__.__name__
        keys = range(self.records)
        import random
        random.shuffle(keys)
        records_per_writer = self.records // self.writers
        readers_per_writer = self.readers // self.writers
        self.assertEqual(self.records, self.writers * records_per_writer)
        self.assertEqual(self.readers, self.writers * readers_per_writer)
        self.assertTrue(records_per_writer % readers_per_writer == 0)
        readers = []
        for x in xrange(self.readers):
            rt = Thread(target=self.readerThread, args=(self.d, x), name='reader %d' % x)
            import sys
            if sys.version_info[0] < 3:
                rt.setDaemon(True)
            else:
                rt.daemon = True
            readers.append(rt)

        writers = []
        for x in xrange(self.writers):
            a = keys[records_per_writer * x:records_per_writer * (x + 1)]
            a.sort()
            b = readers[readers_per_writer * x:readers_per_writer * (x + 1)]
            wt = Thread(target=self.writerThread, args=(self.d, a, b), name='writer %d' % x)
            writers.append(wt)

        for t in writers:
            import sys
            if sys.version_info[0] < 3:
                t.setDaemon(True)
            else:
                t.daemon = True
            t.start()

        for t in writers:
            t.join()

        for t in readers:
            t.join()

    def writerThread(self, d, keys, readers):
        import sys
        if sys.version_info[0] < 3:
            name = currentThread().getName()
        else:
            name = currentThread().name
        if verbose:
            print '%s: creating records %d - %d' % (name, start, stop)
        count = len(keys) // len(readers)
        count2 = count
        for x in keys:
            key = '%04d' % x
            dbutils.DeadlockWrap(d.put, key, self.makeData(key), max_retries=12)
            if verbose and x % 100 == 0:
                print '%s: records %d - %d finished' % (name, start, x)
            count2 -= 1
            if not count2:
                readers.pop().start()
                count2 = count

        if verbose:
            print '%s: finished creating records' % name
        if verbose:
            print '%s: thread finished' % name

    def readerThread(self, d, readerNum):
        import sys
        if sys.version_info[0] < 3:
            name = currentThread().getName()
        else:
            name = currentThread().name
        for i in xrange(5):
            c = d.cursor()
            count = 0
            rec = c.first()
            while 1:
                rec and count += 1
                key, data = rec
                self.assertEqual(self.makeData(key), data)
                rec = c.next()

            if verbose:
                print '%s: found %d records' % (name, count)
            c.close()

        if verbose:
            print '%s: thread finished' % name


class BTreeConcurrentDataStore(ConcurrentDataStoreBase):
    dbtype = db.DB_BTREE
    writers = 2
    readers = 10
    records = 1000


class HashConcurrentDataStore(ConcurrentDataStoreBase):
    dbtype = db.DB_HASH
    writers = 2
    readers = 10
    records = 1000


class SimpleThreadedBase(BaseThreadedTestCase):
    dbopenflags = db.DB_THREAD
    envflags = db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK
    readers = 10
    writers = 2
    records = 1000

    def setEnvOpts(self):
        self.env.set_lk_detect(db.DB_LOCK_DEFAULT)

    def test02_SimpleLocks(self):
        if verbose:
            print '\n', '-=' * 30
            print 'Running %s.test02_SimpleLocks...' % self.__class__.__name__
        keys = range(self.records)
        import random
        random.shuffle(keys)
        records_per_writer = self.records // self.writers
        readers_per_writer = self.readers // self.writers
        self.assertEqual(self.records, self.writers * records_per_writer)
        self.assertEqual(self.readers, self.writers * readers_per_writer)
        self.assertTrue(records_per_writer % readers_per_writer == 0)
        readers = []
        for x in xrange(self.readers):
            rt = Thread(target=self.readerThread, args=(self.d, x), name='reader %d' % x)
            import sys
            if sys.version_info[0] < 3:
                rt.setDaemon(True)
            else:
                rt.daemon = True
            readers.append(rt)

        writers = []
        for x in xrange(self.writers):
            a = keys[records_per_writer * x:records_per_writer * (x + 1)]
            a.sort()
            b = readers[readers_per_writer * x:readers_per_writer * (x + 1)]
            wt = Thread(target=self.writerThread, args=(self.d, a, b), name='writer %d' % x)
            writers.append(wt)

        for t in writers:
            import sys
            if sys.version_info[0] < 3:
                t.setDaemon(True)
            else:
                t.daemon = True
            t.start()

        for t in writers:
            t.join()

        for t in readers:
            t.join()

    def writerThread(self, d, keys, readers):
        import sys
        if sys.version_info[0] < 3:
            name = currentThread().getName()
        else:
            name = currentThread().name
        if verbose:
            print '%s: creating records %d - %d' % (name, start, stop)
        count = len(keys) // len(readers)
        count2 = count
        for x in keys:
            key = '%04d' % x
            dbutils.DeadlockWrap(d.put, key, self.makeData(key), max_retries=12)
            if verbose and x % 100 == 0:
                print '%s: records %d - %d finished' % (name, start, x)
            count2 -= 1
            if not count2:
                readers.pop().start()
                count2 = count

        if verbose:
            print '%s: thread finished' % name

    def readerThread(self, d, readerNum):
        import sys
        if sys.version_info[0] < 3:
            name = currentThread().getName()
        else:
            name = currentThread().name
        c = d.cursor()
        count = 0
        rec = dbutils.DeadlockWrap(c.first, max_retries=10)
        while 1:
            rec and count += 1
            key, data = rec
            self.assertEqual(self.makeData(key), data)
            rec = dbutils.DeadlockWrap(c.next, max_retries=10)

        if verbose:
            print '%s: found %d records' % (name, count)
        c.close()
        if verbose:
            print '%s: thread finished' % name


class BTreeSimpleThreaded(SimpleThreadedBase):
    dbtype = db.DB_BTREE


class HashSimpleThreaded(SimpleThreadedBase):
    dbtype = db.DB_HASH


class ThreadedTransactionsBase(BaseThreadedTestCase):
    dbopenflags = db.DB_THREAD | db.DB_AUTO_COMMIT
    envflags = db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_INIT_LOG | db.DB_INIT_TXN
    readers = 0
    writers = 0
    records = 2000
    txnFlag = 0

    def setEnvOpts(self):
        pass

    def test03_ThreadedTransactions(self):
        if verbose:
            print '\n', '-=' * 30
            print 'Running %s.test03_ThreadedTransactions...' % self.__class__.__name__
        keys = range(self.records)
        import random
        random.shuffle(keys)
        records_per_writer = self.records // self.writers
        readers_per_writer = self.readers // self.writers
        self.assertEqual(self.records, self.writers * records_per_writer)
        self.assertEqual(self.readers, self.writers * readers_per_writer)
        self.assertTrue(records_per_writer % readers_per_writer == 0)
        readers = []
        for x in xrange(self.readers):
            rt = Thread(target=self.readerThread, args=(self.d, x), name='reader %d' % x)
            import sys
            if sys.version_info[0] < 3:
                rt.setDaemon(True)
            else:
                rt.daemon = True
            readers.append(rt)

        writers = []
        for x in xrange(self.writers):
            a = keys[records_per_writer * x:records_per_writer * (x + 1)]
            b = readers[readers_per_writer * x:readers_per_writer * (x + 1)]
            wt = Thread(target=self.writerThread, args=(self.d, a, b), name='writer %d' % x)
            writers.append(wt)

        dt = Thread(target=self.deadlockThread)
        import sys
        if sys.version_info[0] < 3:
            dt.setDaemon(True)
        else:
            dt.daemon = True
        dt.start()
        for t in writers:
            import sys
            if sys.version_info[0] < 3:
                t.setDaemon(True)
            else:
                t.daemon = True
            t.start()

        for t in writers:
            t.join()

        for t in readers:
            t.join()

        self.doLockDetect = False
        dt.join()

    def writerThread--- This code section failed: ---

 406       0	LOAD_CONST        -1
           3	LOAD_CONST        ''
           6	IMPORT_NAME       'sys'
           9	STORE_FAST        'sys'

 407      12	LOAD_FAST         'sys'
          15	LOAD_ATTR         'version_info'
          18	LOAD_CONST        0
          21	BINARY_SUBSCR     ''
          22	LOAD_CONST        3
          25	COMPARE_OP        '<'
          28	JUMP_IF_FALSE     '49'

 408      31	LOAD_GLOBAL       'currentThread'
          34	CALL_FUNCTION_0   ''
          37	LOAD_ATTR         'getName'
          40	CALL_FUNCTION_0   ''
          43	STORE_FAST        'name'
          46	JUMP_FORWARD      '61'

 410      49	LOAD_GLOBAL       'currentThread'
          52	CALL_FUNCTION_0   ''
          55	LOAD_ATTR         'name'
          58	STORE_FAST        'name'
        61_0	COME_FROM         '46'

 412      61	LOAD_GLOBAL       'len'
          64	LOAD_FAST         'keys'
          67	CALL_FUNCTION_1   ''
          70	LOAD_GLOBAL       'len'
          73	LOAD_FAST         'readers'
          76	CALL_FUNCTION_1   ''
          79	BINARY_FLOOR_DIVIDE ''
          80	STORE_FAST        'count'

 413      83	SETUP_LOOP        '346'
          86	LOAD_GLOBAL       'len'
          89	LOAD_FAST         'keys'
          92	CALL_FUNCTION_1   ''
          95	JUMP_IF_FALSE     '345'

 414      98	SETUP_EXCEPT      '273'

 415     101	LOAD_FAST         'self'
         104	LOAD_ATTR         'env'
         107	LOAD_ATTR         'txn_begin'
         110	LOAD_CONST        ''
         113	LOAD_FAST         'self'
         116	LOAD_ATTR         'txnFlag'
         119	CALL_FUNCTION_2   ''
         122	STORE_FAST        'txn'

 416     125	LOAD_FAST         'keys'
         128	LOAD_FAST         'count'
         131	SLICE+2           ''
         132	STORE_FAST        'keys2'

 417     135	SETUP_LOOP        '233'
         138	LOAD_FAST         'keys2'
         141	GET_ITER          ''
         142	FOR_ITER          '232'
         145	STORE_FAST        'x'

 418     148	LOAD_CONST        '%04d'
         151	LOAD_FAST         'x'
         154	BINARY_MODULO     ''
         155	STORE_FAST        'key'

 419     158	LOAD_FAST         'd'
         161	LOAD_ATTR         'put'
         164	LOAD_FAST         'key'
         167	LOAD_FAST         'self'
         170	LOAD_ATTR         'makeData'
         173	LOAD_FAST         'key'
         176	CALL_FUNCTION_1   ''
         179	LOAD_FAST         'txn'
         182	CALL_FUNCTION_3   ''
         185	POP_TOP           ''

 420     186	LOAD_GLOBAL       'verbose'
         189	JUMP_IF_FALSE     '229'
         192	LOAD_FAST         'x'
         195	LOAD_CONST        100
         198	BINARY_MODULO     ''
         199	LOAD_CONST        0
         202	COMPARE_OP        '=='
       205_0	COME_FROM         '189'
         205	JUMP_IF_FALSE     '229'

 421     208	LOAD_CONST        '%s: records %d - %d finished'
         211	LOAD_FAST         'name'
         214	LOAD_GLOBAL       'start'
         217	LOAD_FAST         'x'
         220	BUILD_TUPLE_3     ''
         223	BINARY_MODULO     ''
         224	PRINT_ITEM        ''
         225	PRINT_NEWLINE_CONT ''
         226	JUMP_BACK         '142'
         229	JUMP_BACK         '142'
         232	POP_BLOCK         ''
       233_0	COME_FROM         '135'

 422     233	LOAD_FAST         'txn'
         236	LOAD_ATTR         'commit'
         239	CALL_FUNCTION_0   ''
         242	POP_TOP           ''

 423     243	LOAD_FAST         'keys'
         246	LOAD_FAST         'count'
         249	SLICE+1           ''
         250	STORE_FAST        'keys'

 424     253	LOAD_FAST         'readers'
         256	LOAD_ATTR         'pop'
         259	CALL_FUNCTION_0   ''
         262	LOAD_ATTR         'start'
         265	CALL_FUNCTION_0   ''
         268	POP_TOP           ''
         269	POP_BLOCK         ''
         270	JUMP_BACK         '86'
       273_0	COME_FROM         '98'

 425     273	DUP_TOP           ''
         274	LOAD_GLOBAL       'db'
         277	LOAD_ATTR         'DBLockDeadlockError'
         280	LOAD_GLOBAL       'db'
         283	LOAD_ATTR         'DBLockNotGrantedError'
         286	BUILD_TUPLE_2     ''
         289	COMPARE_OP        'exception match'
         292	JUMP_IF_FALSE     '341'
         295	POP_TOP           ''
         296	STORE_FAST        'val'
         299	POP_TOP           ''

 426     300	LOAD_GLOBAL       'verbose'
         303	JUMP_IF_FALSE     '328'

 427     306	LOAD_CONST        '%s: Aborting transaction (%s)'
         309	LOAD_FAST         'name'
         312	LOAD_FAST         'val'
         315	LOAD_CONST        1
         318	BINARY_SUBSCR     ''
         319	BUILD_TUPLE_2     ''
         322	BINARY_MODULO     ''
         323	PRINT_ITEM        ''
         324	PRINT_NEWLINE_CONT ''
         325	JUMP_FORWARD      '328'
       328_0	COME_FROM         '325'

 428     328	LOAD_FAST         'txn'
         331	LOAD_ATTR         'abort'
         334	CALL_FUNCTION_0   ''
         337	POP_TOP           ''
         338	JUMP_BACK         '86'
         341	END_FINALLY       ''
       342_0	COME_FROM         '341'
         342	JUMP_BACK         '86'
         345	POP_BLOCK         ''
       346_0	COME_FROM         '83'

 430     346	LOAD_GLOBAL       'verbose'
         349	JUMP_IF_FALSE     '364'

 431     352	LOAD_CONST        '%s: thread finished'
         355	LOAD_FAST         'name'
         358	BINARY_MODULO     ''
         359	PRINT_ITEM        ''
         360	PRINT_NEWLINE_CONT ''
         361	JUMP_FORWARD      '364'
       364_0	COME_FROM         '361'
         364	LOAD_CONST        ''
         367	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 345

    def readerThread--- This code section failed: ---

 434       0	LOAD_CONST        -1
           3	LOAD_CONST        ''
           6	IMPORT_NAME       'sys'
           9	STORE_FAST        'sys'

 435      12	LOAD_FAST         'sys'
          15	LOAD_ATTR         'version_info'
          18	LOAD_CONST        0
          21	BINARY_SUBSCR     ''
          22	LOAD_CONST        3
          25	COMPARE_OP        '<'
          28	JUMP_IF_FALSE     '49'

 436      31	LOAD_GLOBAL       'currentThread'
          34	CALL_FUNCTION_0   ''
          37	LOAD_ATTR         'getName'
          40	CALL_FUNCTION_0   ''
          43	STORE_FAST        'name'
          46	JUMP_FORWARD      '61'

 438      49	LOAD_GLOBAL       'currentThread'
          52	CALL_FUNCTION_0   ''
          55	LOAD_ATTR         'name'
          58	STORE_FAST        'name'
        61_0	COME_FROM         '46'

 440      61	LOAD_GLOBAL       'False'
          64	STORE_FAST        'finished'

 441      67	SETUP_LOOP        '345'
          70	LOAD_FAST         'finished'
          73	JUMP_IF_TRUE      '344'

 442      76	SETUP_EXCEPT      '262'

 443      79	LOAD_FAST         'self'
          82	LOAD_ATTR         'env'
          85	LOAD_ATTR         'txn_begin'
          88	LOAD_CONST        ''
          91	LOAD_FAST         'self'
          94	LOAD_ATTR         'txnFlag'
          97	CALL_FUNCTION_2   ''
         100	STORE_FAST        'txn'

 444     103	LOAD_FAST         'd'
         106	LOAD_ATTR         'cursor'
         109	LOAD_FAST         'txn'
         112	CALL_FUNCTION_1   ''
         115	STORE_FAST        'c'

 445     118	LOAD_CONST        0
         121	STORE_FAST        'count'

 446     124	LOAD_FAST         'c'
         127	LOAD_ATTR         'first'
         130	CALL_FUNCTION_0   ''
         133	STORE_FAST        'rec'

 447     136	SETUP_LOOP        '208'
         139	LOAD_FAST         'rec'
         142	JUMP_IF_FALSE     '207'

 448     145	LOAD_FAST         'count'
         148	LOAD_CONST        1
         151	INPLACE_ADD       ''
         152	STORE_FAST        'count'

 449     155	LOAD_FAST         'rec'
         158	UNPACK_SEQUENCE_2 ''
         161	STORE_FAST        'key'
         164	STORE_FAST        'data'

 450     167	LOAD_FAST         'self'
         170	LOAD_ATTR         'assertEqual'
         173	LOAD_FAST         'self'
         176	LOAD_ATTR         'makeData'
         179	LOAD_FAST         'key'
         182	CALL_FUNCTION_1   ''
         185	LOAD_FAST         'data'
         188	CALL_FUNCTION_2   ''
         191	POP_TOP           ''

 451     192	LOAD_FAST         'c'
         195	LOAD_ATTR         'next'
         198	CALL_FUNCTION_0   ''
         201	STORE_FAST        'rec'
         204	JUMP_BACK         '139'
         207	POP_BLOCK         ''
       208_0	COME_FROM         '136'

 452     208	LOAD_GLOBAL       'verbose'
         211	JUMP_IF_FALSE     '232'
         214	LOAD_CONST        '%s: found %d records'
         217	LOAD_FAST         'name'
         220	LOAD_FAST         'count'
         223	BUILD_TUPLE_2     ''
         226	BINARY_MODULO     ''
         227	PRINT_ITEM        ''
         228	PRINT_NEWLINE_CONT ''
         229	JUMP_FORWARD      '232'
       232_0	COME_FROM         '229'

 453     232	LOAD_FAST         'c'
         235	LOAD_ATTR         'close'
         238	CALL_FUNCTION_0   ''
         241	POP_TOP           ''

 454     242	LOAD_FAST         'txn'
         245	LOAD_ATTR         'commit'
         248	CALL_FUNCTION_0   ''
         251	POP_TOP           ''

 455     252	LOAD_GLOBAL       'True'
         255	STORE_FAST        'finished'
         258	POP_BLOCK         ''
         259	JUMP_BACK         '70'
       262_0	COME_FROM         '76'

 456     262	DUP_TOP           ''
         263	LOAD_GLOBAL       'db'
         266	LOAD_ATTR         'DBLockDeadlockError'
         269	LOAD_GLOBAL       'db'
         272	LOAD_ATTR         'DBLockNotGrantedError'
         275	BUILD_TUPLE_2     ''
         278	COMPARE_OP        'exception match'
         281	JUMP_IF_FALSE     '340'
         284	POP_TOP           ''
         285	STORE_FAST        'val'
         288	POP_TOP           ''

 457     289	LOAD_GLOBAL       'verbose'
         292	JUMP_IF_FALSE     '317'

 458     295	LOAD_CONST        '%s: Aborting transaction (%s)'
         298	LOAD_FAST         'name'
         301	LOAD_FAST         'val'
         304	LOAD_CONST        1
         307	BINARY_SUBSCR     ''
         308	BUILD_TUPLE_2     ''
         311	BINARY_MODULO     ''
         312	PRINT_ITEM        ''
         313	PRINT_NEWLINE_CONT ''
         314	JUMP_FORWARD      '317'
       317_0	COME_FROM         '314'

 459     317	LOAD_FAST         'c'
         320	LOAD_ATTR         'close'
         323	CALL_FUNCTION_0   ''
         326	POP_TOP           ''

 460     327	LOAD_FAST         'txn'
         330	LOAD_ATTR         'abort'
         333	CALL_FUNCTION_0   ''
         336	POP_TOP           ''
         337	JUMP_BACK         '70'
         340	END_FINALLY       ''
       341_0	COME_FROM         '340'
         341	JUMP_BACK         '70'
         344	POP_BLOCK         ''
       345_0	COME_FROM         '67'

 462     345	LOAD_GLOBAL       'verbose'
         348	JUMP_IF_FALSE     '363'

 463     351	LOAD_CONST        '%s: thread finished'
         354	LOAD_FAST         'name'
         357	BINARY_MODULO     ''
         358	PRINT_ITEM        ''
         359	PRINT_NEWLINE_CONT ''
         360	JUMP_FORWARD      '363'
       363_0	COME_FROM         '360'
         363	LOAD_CONST        ''
         366	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 344

    def deadlockThread(self):
        self.doLockDetect = True
        while 1:
            self.doLockDetect and time.sleep(0.05)
            try:
                aborted = self.env.lock_detect(db.DB_LOCK_RANDOM, db.DB_LOCK_CONFLICT)
                if verbose and aborted:
                    print 'deadlock: Aborted %d deadlocked transaction(s)' % aborted
            except db.DBError:
                pass


class BTreeThreadedTransactions(ThreadedTransactionsBase):
    dbtype = db.DB_BTREE
    writers = 2
    readers = 10
    records = 1000


class HashThreadedTransactions(ThreadedTransactionsBase):
    dbtype = db.DB_HASH
    writers = 2
    readers = 10
    records = 1000


class BTreeThreadedNoWaitTransactions(ThreadedTransactionsBase):
    dbtype = db.DB_BTREE
    writers = 2
    readers = 10
    records = 1000
    txnFlag = db.DB_TXN_NOWAIT


class HashThreadedNoWaitTransactions(ThreadedTransactionsBase):
    dbtype = db.DB_HASH
    writers = 2
    readers = 10
    records = 1000
    txnFlag = db.DB_TXN_NOWAIT


def test_suite():
    suite = unittest.TestSuite()
    if have_threads:
        suite.addTest(unittest.makeSuite(BTreeConcurrentDataStore))
        suite.addTest(unittest.makeSuite(HashConcurrentDataStore))
        suite.addTest(unittest.makeSuite(BTreeSimpleThreaded))
        suite.addTest(unittest.makeSuite(HashSimpleThreaded))
        suite.addTest(unittest.makeSuite(BTreeThreadedTransactions))
        suite.addTest(unittest.makeSuite(HashThreadedTransactions))
        suite.addTest(unittest.makeSuite(BTreeThreadedNoWaitTransactions))
        suite.addTest(unittest.makeSuite(HashThreadedNoWaitTransactions))
    else:
        print 'Threads not available, skipping thread tests.'
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')