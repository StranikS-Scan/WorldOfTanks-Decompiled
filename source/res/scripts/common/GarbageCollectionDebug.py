# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/GarbageCollectionDebug.py
import re
import sys
import itertools
from bwdebug import DEBUG_MSG
from bwdebug import ERROR_MSG
import BigWorld
import StringIO
import objgraph
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
    try:
        import gc
        gc.enable()
    except ImportError:
        raise RuntimeError('Garbage collection is not supported')


def gcDisable():
    try:
        import gc
        gc.disable()
    except ImportError:
        return


def gcDebugEnable():
    try:
        import gc
        gc.set_debug(GC_DEBUG_FLAGS)
    except ImportError:
        ERROR_MSG('Could not import gc module; ' + 'garbage collection support is not compiled in')


def gcIsLeakDetect():
    try:
        import gc
        if (gc.isenabled() and gc.get_debug() & gc.DEBUG_LEAK) > 0:
            return True
    except ImportError:
        ERROR_MSG('Could not import gc module; garbage collection support is not compiled in')

    return False


def gcWriteLog(file, s, isError=False):
    if isError:
        ERROR_MSG(s)
    else:
        DEBUG_MSG(s)
    if file is not None:
        file.write(s + '\n')
        file.flush()
    return


def get_all_unique_loops(edges):
    leafs = True
    while leafs:
        srcs = set()
        trgts = set()
        for src, tgt in edges:
            srcs.add(src)
            trgts.add(tgt)

        leafs = trgts - srcs
        new_edges = []
        for src, tgt in edges:
            if tgt not in leafs:
                new_edges.append((src, tgt))

        edges = new_edges

    return edges


def get_loops_graph(content):
    lines = content.split(';')
    g = re.compile('o\\d+')
    objs = [ g.findall(i) for i in lines ]
    edges = [ i for i in objs if len(i) == 2 ]
    unique_loops = get_all_unique_loops(edges)
    nodes = set((j for i in unique_loops for j in i))
    result = []
    for line in lines:
        line_nodes = g.findall(line)
        if not line_nodes or all((i in nodes for i in line_nodes)):
            result.append(line)

    return ';'.join(result)


def gcDump():
    try:
        import gc
    except ImportError:
        ERROR_MSG('Could not import gc module; ' + 'garbage collection support is not compiled in')
        return

    leakCount = 0
    gcDebugEnable()
    DEBUG_MSG('Forcing a garbage collection...')
    leakCount = gc.collect()
    s = 'Total garbage: %u' % (leakCount,)
    gcWriteLog(None, s, isError=leakCount > 0)
    if leakCount:
        gc_dump = gc.garbage[:]
        if len(gc_dump) > 0:
            garbage_ids = {id(x):x for x in gc_dump}
            garbage_list = []
            gc_refs, _ = get_refs(gc_dump, garbage_list, garbage_ids)
            del garbage_list[:]
            graph_info = get_graph_text_repr(gc_refs, garbage_ids, shortnames=False)
            for obj in graph_info['nodes'].values():
                gcWriteLog(None, repr(obj))

            for obj in graph_info['edges']:
                gcWriteLog(None, repr(obj))

            graph_info['nodes'].clear()
            del graph_info['edges'][:]
            garbage_ids.clear()
            del gc_refs[:]
            del gc_dump[:]
    del gc.garbage[:]
    return leakCount


def get_refs(obj, source_list, known_ids, get_unknown_referents=False):
    if id(obj) in source_list:
        return ([], [])
    source_list.append(id(obj))
    res = []
    unknown_referents = []
    for i in gc.get_referents(obj):
        if id(i) in known_ids:
            res.append({'target': id(i),
             'source': id(obj)})
        if get_unknown_referents:
            unknown_referents.append(i)
            res.append({'target': id(i),
             'source': id(obj)})

    return (res, unknown_referents)


def get_graph_text_repr(graph, garbage_ids, extra_info=False, refcounts=False, shortnames=True):
    node_names = {}
    for edge_data in graph:
        if edge_data['target'] not in garbage_ids or edge_data['source'] not in garbage_ids:
            continue
        obj_id = edge_data['source']
        target = garbage_ids[obj_id]
        for obj_id in (edge_data['source'], edge_data['target']):
            obj = garbage_ids[obj_id]
            node_names[obj_id] = {'id': obj_id,
             'label': objgraph._obj_label(obj, extra_info, refcounts, shortnames)}

        source = garbage_ids[edge_data['target']]
        edge_data['label'] = objgraph._edge_label(target, source)

    return {'nodes': node_names,
     'edges': graph}


def getGarbageGraph(depth=0):
    try:
        import gc
    except ImportError:
        message = 'Could not import gc module; garbage collection support is not compiled in'
        return message

    leakCount = 0
    gcDebugEnable()
    leakCount = gc.collect()
    gc_dump = gc.garbage[:]
    del gc.garbage[:]
    if len(gc_dump) > 0:
        garbage_ids = {id(x):x for x in gc_dump}
        garbage_list = []
        gc_refs = []
        new_objects = gc_dump
        for d in range(depth + 1):
            added_objects = []
            for obj in new_objects:
                graph_part, new_objects = get_refs(obj, garbage_list, garbage_ids, get_unknown_referents=d < depth)
                gc_refs.extend(graph_part)
                garbage_ids.update({id(obj):obj for obj in new_objects})
                added_objects.extend(new_objects)

            new_objects = added_objects

        del garbage_list[:]
        graph_info = get_graph_text_repr(gc_refs, garbage_ids, shortnames=False)
        result = 'digraph ObjectGraph { node[shape=box, style=filled, fillcolor=white];  %s }'
        node_items = [ 'o%s[label="%s"]' % (i['id'], i['label']) for i in graph_info['nodes'].values() ]
        edge_items = [ 'o%s -> o%s %s' % (i['source'], i['target'], i.get('label', '')) for i in graph_info['edges'] ]
        garbage_ids.clear()
        graph_info['nodes'].clear()
        del graph_info['edges'][:]
        del gc_refs[:]
        del gc_dump[:]
        return result % '; '.join(itertools.chain(node_items, edge_items))


class TestLeak:
    pass


def createTestLeaks():
    if TEST_SIMPLE_LEAK:
        createBasicLeak()
    if TEST_COMPLEX_LEAK:
        createComplexLeak()


def createBasicLeak():
    DEBUG_MSG('Creating a simple test leak..')
    ref = TestLeak()
    ref.selfRef = ref
    ref = None
    return


def createComplexLeak():
    DEBUG_MSG('Creating a complex test leak..')
    refChain = TestLeak()
    refLink1 = TestLeak()
    refLink2 = TestLeak()
    saltLink = TestLeak()
    refChain.badRefStart = refLink1
    refLink1.badRefMiddle = refLink2
    refLink2.saltValue = saltLink
    refLink2.badRefEnd = refChain
    refChain = None
    refLink1 = None
    refLink2 = None
    return


def getObjectData(obj, indent=''):
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
        result += '%s bytes: %u\n' % (indent, sys.getsizeof(obj))
    except ImportError:
        result += '%s bytes: could not get size\n' % (indent,)

    return result


def getContents(obj, indent=''):
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
        ERROR_MSG('Error: could not import pprint: %s' % (e,))
        raise
    except AttributeError:
        result += '%s str : %s\n' % (indent, pp.pformat(obj))
    except TypeError:
        result += '%s str : %s\n' % (indent, pp.pformat(obj))

    return result


def getObjectReferrers(obj, ignore):
    result = ''
    try:
        refCount = sys.getrefcount(obj)
        result += ' sys.getrefcount: %u\n' % (refCount,)
    except:
        pass

    referrers = None
    try:
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

    finally:
        del referrers

    return result
