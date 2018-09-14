# Embedded file name: scripts/common/Lib/sqlite3/test/hooks.py
import os, unittest
import sqlite3 as sqlite

class CollationTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def CheckCreateCollationNotCallable(self):
        con = sqlite.connect(':memory:')
        try:
            con.create_collation('X', 42)
            self.fail('should have raised a TypeError')
        except TypeError as e:
            self.assertEqual(e.args[0], 'parameter must be callable')

    def CheckCreateCollationNotAscii(self):
        con = sqlite.connect(':memory:')
        try:
            con.create_collation('coll\xe4', cmp)
            self.fail('should have raised a ProgrammingError')
        except sqlite.ProgrammingError as e:
            pass

    def CheckCollationIsUsed(self):
        if sqlite.version_info < (3, 2, 1):
            return
        else:

            def mycoll(x, y):
                return -cmp(x, y)

            con = sqlite.connect(':memory:')
            con.create_collation('mycoll', mycoll)
            sql = "\n            select x from (\n            select 'a' as x\n            union\n            select 'b' as x\n            union\n            select 'c' as x\n            ) order by x collate mycoll\n            "
            result = con.execute(sql).fetchall()
            if result[0][0] != 'c' or result[1][0] != 'b' or result[2][0] != 'a':
                self.fail('the expected order was not returned')
            con.create_collation('mycoll', None)
            try:
                result = con.execute(sql).fetchall()
                self.fail('should have raised an OperationalError')
            except sqlite.OperationalError as e:
                self.assertEqual(e.args[0].lower(), 'no such collation sequence: mycoll')

            return

    def CheckCollationReturnsLargeInteger(self):

        def mycoll(x, y):
            return -((x > y) - (x < y)) * 4294967296L

        con = sqlite.connect(':memory:')
        con.create_collation('mycoll', mycoll)
        sql = "\n            select x from (\n            select 'a' as x\n            union\n            select 'b' as x\n            union\n            select 'c' as x\n            ) order by x collate mycoll\n            "
        result = con.execute(sql).fetchall()
        self.assertEqual(result, [('c',), ('b',), ('a',)], msg='the expected order was not returned')

    def CheckCollationRegisterTwice(self):
        """
        Register two different collation functions under the same name.
        Verify that the last one is actually used.
        """
        con = sqlite.connect(':memory:')
        con.create_collation('mycoll', cmp)
        con.create_collation('mycoll', lambda x, y: -cmp(x, y))
        result = con.execute("\n            select x from (select 'a' as x union select 'b' as x) order by x collate mycoll\n            ").fetchall()
        if result[0][0] != 'b' or result[1][0] != 'a':
            self.fail('wrong collation function is used')

    def CheckDeregisterCollation(self):
        """
        Register a collation, then deregister it. Make sure an error is raised if we try
        to use it.
        """
        con = sqlite.connect(':memory:')
        con.create_collation('mycoll', cmp)
        con.create_collation('mycoll', None)
        try:
            con.execute("select 'a' as x union select 'b' as x order by x collate mycoll")
            self.fail('should have raised an OperationalError')
        except sqlite.OperationalError as e:
            if not e.args[0].startswith('no such collation sequence'):
                self.fail('wrong OperationalError raised')

        return


class ProgressTests(unittest.TestCase):

    def CheckProgressHandlerUsed(self):
        """
        Test that the progress handler is invoked once it is set.
        """
        con = sqlite.connect(':memory:')
        progress_calls = []

        def progress():
            progress_calls.append(None)
            return 0

        con.set_progress_handler(progress, 1)
        con.execute('\n            create table foo(a, b)\n            ')
        self.assertTrue(progress_calls)

    def CheckOpcodeCount(self):
        """
        Test that the opcode argument is respected.
        """
        con = sqlite.connect(':memory:')
        progress_calls = []

        def progress():
            progress_calls.append(None)
            return 0

        con.set_progress_handler(progress, 1)
        curs = con.cursor()
        curs.execute('\n            create table foo (a, b)\n            ')
        first_count = len(progress_calls)
        progress_calls = []
        con.set_progress_handler(progress, 2)
        curs.execute('\n            create table bar (a, b)\n            ')
        second_count = len(progress_calls)
        self.assertGreaterEqual(first_count, second_count)

    def CheckCancelOperation(self):
        """
        Test that returning a non-zero value stops the operation in progress.
        """
        con = sqlite.connect(':memory:')
        progress_calls = []

        def progress():
            progress_calls.append(None)
            return 1

        con.set_progress_handler(progress, 1)
        curs = con.cursor()
        self.assertRaises(sqlite.OperationalError, curs.execute, 'create table bar (a, b)')

    def CheckClearHandler(self):
        """
        Test that setting the progress handler to None clears the previously set handler.
        """
        con = sqlite.connect(':memory:')
        action = []

        def progress():
            action.append(1)
            return 0

        con.set_progress_handler(progress, 1)
        con.set_progress_handler(None, 1)
        con.execute('select 1 union select 2 union select 3').fetchall()
        self.assertEqual(len(action), 0, 'progress handler was not cleared')
        return


def suite():
    collation_suite = unittest.makeSuite(CollationTests, 'Check')
    progress_suite = unittest.makeSuite(ProgressTests, 'Check')
    return unittest.TestSuite((collation_suite, progress_suite))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    test()
