# Embedded file name: scripts/common/GarbageCollectionDebug.py
"""
This is an example of how to disable/enable garbage collection, and how to
activate debugging. Debugging output is sent to stdout.

By default, all components that use Python have its garbage collection disabled.
However, script developers may find garbage collection to be useful to identify
leaks due to cyclical memory references.

More information about how the Python garbage collection facility works can be
found in the Python documentation for the gc module.
http://docs.python.org/library/gc.html

More information about BigWorld Technology's use of Python and C can be found
in bigworld/doc/python_and_c.pdf.

This script can be used in the personality script (BaseApp, CellApp or client)
to activate the functions on BigWorld component shutdown.

It also imports things on demand instead of at the top of the file to try and
minimise the number of imported modules (which may then import more modules)
which would give false results when testing memory allocations.
"""
DUMP_PATH = 'gcDump.log'
LIMIT_LEN = False
MAX_LEN = 5
MAX_DEPTH = 1
TEST_SIMPLE_LEAK = False
TEST_COMPLEX_LEAK = False
try:
    import gc
    GC_DEBUG_FLAGS = gc.DEBUG_SAVEALL
except ImportError:
    GC_DEBUG_FLAGS = 0

def gcEnable():
    """
    Enable garbage collection. Raises a SystemError if garbage collection is
    not supported.
    """
    try:
        import gc
        gc.enable()
    except ImportError:
        raise RuntimeError, 'Garbage collection is not supported'


def gcDisable():
    """
    Disable garbage collection.
    """
    try:
        import gc
        gc.disable()
    except ImportError:
        return


def gcDebugEnable():
    """
    Call this function to enable garbage collection debugging. Prints a warning
    message if there is no support for garbage collection.
    """
    try:
        import gc
        gc.set_debug(GC_DEBUG_FLAGS)
    except ImportError:
        from bwdebug import ERROR_MSG
        ERROR_MSG('Could not import gc module; ' + 'garbage collection support is not compiled in')


def gcIsLeakDetect():
    """
    Check if leak detection is on.
    """
    try:
        import gc
        if (gc.isenabled() and gc.get_debug() & gc.DEBUG_LEAK) > 0:
            return True
    except ImportError:
        from bwdebug import ERROR_MSG
        ERROR_MSG('Could not import gc module; garbage collection support is not compiled in')

    return False


def gcDump(doFullCheck = False, logName = DUMP_PATH):
    """
    Performs a garbage collect and then print a dump of what has been
    collected.
    
    doFullCheck if True, do a collect and iterate over collected garbage
    and print info.
    Otherwise, do a collect and just print the number of objects collected.
    logName the name of the file to log to.
    """
    from bwdebug import DEBUG_MSG
    from bwdebug import ERROR_MSG
    try:
        import gc
    except ImportError:
        ERROR_MSG('Could not import gc module; ' + 'garbage collection support is not compiled in')
        return

    createTestLeaks()
    leakCount = 0
    gcDebugEnable()
    DEBUG_MSG('Forcing a garbage collection...')
    leakCount = gc.collect()
    if doFullCheck:
        copy = gc.garbage[:]
        del gc.garbage[:]
        try:
            file = open(logName, 'w')
            s = 'Total garbage: %u' % (leakCount,)
            DEBUG_MSG(s)
            file.write(s + '\n')
            if len(copy) > 0:
                DEBUG_MSG('Writing objects in garbage to file: "%s"' % (logName,))
                file.write('Objects in garbage:\n')
            i = 0
            for g in copy:
                try:
                    s = 'Garbage item %u\n' % (i,)
                    s += getObjectData(g)
                    s += getObjectReferrers(g, [gc.garbage, copy])
                    file.write('\n' + s)
                    file.flush()
                except ReferenceError as e:
                    s = 'Error: Object referenced in garbage list no longer exists: %s' % (e,)
                    file.write('\n' + s)
                    ERROR_MSG(s)

                i += 1

            file.flush()
            file.close()
        except IOError as e:
            ERROR_MSG(e)
        except:
            file.write('Error printing garbage dump, see console.\n')
            ERROR_MSG('Error printing garbage dump.')
            file.flush()
            file.close()
            raise

    else:
        del gc.garbage[:]
    return leakCount


class TestLeak:
    pass


def createTestLeaks():
    if TEST_SIMPLE_LEAK:
        createBasicLeak()
    if TEST_COMPLEX_LEAK:
        createComplexLeak()


def createBasicLeak():
    """
    For testing if the garabage collection log works.
    
    Creates a circular reference with a self-referencing object.
    
    So there should be two items found in gc.garbage:
    - the "ref" instance object
    - the dictionary of "ref", which contains "selfref"
    """
    from bwdebug import DEBUG_MSG
    DEBUG_MSG('Creating a simple test leak..')
    ref = TestLeak()
    ref.selfRef = ref
    ref = None
    return


def createComplexLeak():
    """
    For testing if the garabage collection log works.
    
    Creates a reference cycle with three objects.
    
    There should be six items found in gc.garbage:
    - the "refChain" instance object
    - the dictionary of "refChain", which contains "badRefStart"
    - the "refLink1" instance object
    - the dictionary of "refLink1", which contains "badRefMiddle"
    - the "refLink2" instance object
    - the dictionary of "refLink2", which contains "badRefEnd"
    """
    from bwdebug import DEBUG_MSG
    DEBUG_MSG('Creating a complex test leak..')
    refChain = TestLeak()
    refLink1 = TestLeak()
    refLink2 = TestLeak()
    refChain.badRefStart = refLink1
    refLink1.badRefMiddle = refLink2
    refLink2.badRefEnd = refChain
    refChain = None
    refLink1 = None
    refLink2 = None
    return


def getObjectData(obj, indent = ''):
    """
    Get info about a given object.
    Name, type etc.
    Return as a string.
    """
    result = ''
    result += '%sObject id %u\n' % (indent, id(obj))
    try:
        result += '%s name: %s\n' % (indent, obj.__class__.__name__)
    except AttributeError:
        result += '%s name: no name\n' % (indent,)

    result += '%s type: %s\n' % (indent, type(obj))
    try:
        result += '%s len : %u\n' % (indent, len(obj))
    except AttributeError:
        result += '%s len : no length\n' % (indent,)
    except TypeError:
        result += '%s len : no length\n' % (indent,)

    result += getContents(obj, indent)
    try:
        import sys
        result += '%s bytes: %u\n' % (indent, sys.getsizeof(obj))
    except ImportError:
        result += '%s bytes: could not get size\n' % (indent,)

    return result


def getContents(obj, indent = ''):
    """
    Get a string representing an object or the first few items in a sequence.
    """
    result = ''
    try:
        import pprint
        pp = pprint.PrettyPrinter(depth=MAX_DEPTH)
        if LIMIT_LEN:
            if len(obj) <= MAX_LEN:
                result += '%s contents: %s\n' % (indent, pp.pformat(obj))
            else:
                short = obj[:MAX_LEN]
                result += '%s partial contents (first %u): %s ...\n' % (indent, MAX_LEN, pp.pformat(short))
        else:
            result += '%s contents: %s\n' % (indent, pp.pformat(obj))
    except ImportError as e:
        from bwdebug import ERROR_MSG
        ERROR_MSG('Error: could not import pprint: %s' % (e,))
        raise
    except AttributeError:
        result += '%s str : %s\n' % (indent, pp.pformat(obj))
    except TypeError:
        result += '%s str : %s\n' % (indent, pp.pformat(obj))

    return result


def getObjectReferrers(obj, ignore):
    """
    Get info about what objects are referring to a given object.
    Return info as a string.
    Ignore referrers in the "ignore" list.
    """
    result = ''
    try:
        import sys
        refCount = sys.getrefcount(obj)
        result += ' sys.getrefcount: %u\n' % (refCount,)
    except:
        pass

    try:
        referrers = gc.get_referrers(obj)
        result += ' gc.get_referrers (%u):\n' % (len(referrers),)
        i = 0
        for r in referrers:
            try:
                result += ' ->(referrer %u)\n' % (i,)
                if r not in ignore:
                    result += getObjectData(r, ' -> ')
                else:
                    result += ' -> reference from gc.garbage list (ignore)\n'
            except:
                print 'Error getting referrer'

            i += 1

    except:
        result += 'Error getting referrers'

    return result
