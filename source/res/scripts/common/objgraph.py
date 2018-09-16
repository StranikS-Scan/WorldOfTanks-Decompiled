# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/objgraph.py
import codecs
import gc
import re
import inspect
import types
import operator
import os
import subprocess
import tempfile
import sys
import itertools
try:
    from types import InstanceType
except ImportError:
    InstanceType = None

__author__ = 'Marius Gedminas (marius@gedmin.as)'
__copyright__ = 'Copyright (c) 2008-2015 Marius Gedminas and contributors'
__license__ = 'MIT'
__version__ = '2.0.2.dev0'
__date__ = '2015-07-28'
try:
    basestring
except NameError:
    basestring = str

try:
    iteritems = dict.iteritems
except AttributeError:
    iteritems = dict.items

def count(typename, objects=None):
    if objects is None:
        objects = gc.get_objects()
    try:
        if '.' in typename:
            return sum((1 for o in objects if _long_typename(o) == typename))
        return sum((1 for o in objects if _short_typename(o) == typename))
    finally:
        del objects

    return


def typestats(objects=None, shortnames=True):
    if objects is None:
        objects = gc.get_objects()
    try:
        if shortnames:
            typename = _short_typename
        else:
            typename = _long_typename
        stats = {}
        for o in objects:
            n = typename(o)
            stats[n] = stats.get(n, 0) + 1

        return stats
    finally:
        del objects

    return


def most_common_types(limit=10, objects=None, shortnames=True):
    stats = sorted(typestats(objects, shortnames=shortnames).items(), key=operator.itemgetter(1), reverse=True)
    if limit:
        stats = stats[:limit]
    return stats


def show_most_common_types(limit=10, objects=None, shortnames=True):
    stats = most_common_types(limit, objects, shortnames=shortnames)
    width = max((len(name) for name, count in stats))
    for name, count in stats:
        print '%-*s %i' % (width, name, count)


def show_growth(limit=10, peak_stats={}, shortnames=True):
    gc.collect()
    stats = typestats(shortnames=shortnames)
    deltas = {}
    for name, count in iteritems(stats):
        old_count = peak_stats.get(name, 0)
        if count > old_count:
            deltas[name] = count - old_count
            peak_stats[name] = count

    deltas = sorted(deltas.items(), key=operator.itemgetter(1), reverse=True)
    if limit:
        deltas = deltas[:limit]
    if deltas:
        width = max((len(name) for name, count in deltas))
        for name, delta in deltas:
            print '%-*s%9d %+9d' % (width,
             name,
             stats[name],
             delta)


def get_leaking_objects(objects=None):
    if objects is None:
        gc.collect()
        objects = gc.get_objects()
    try:
        ids = set((id(i) for i in objects))
        for i in objects:
            ids.difference_update((id(j) for j in gc.get_referents(i)))

        return [ i for i in objects if id(i) in ids ]
    finally:
        del objects
        del i

    return


def by_type(typename, objects=None):
    if objects is None:
        objects = gc.get_objects()
    try:
        if '.' in typename:
            return [ o for o in objects if _long_typename(o) == typename ]
        return [ o for o in objects if _short_typename(o) == typename ]
    finally:
        del objects

    return


def at(addr):
    for o in gc.get_objects():
        if id(o) == addr:
            return o

    return None


def find_ref_chain(obj, predicate, max_depth=20, extra_ignore=()):
    return _find_chain(obj, predicate, gc.get_referents, max_depth=max_depth, extra_ignore=extra_ignore)[::-1]


def find_backref_chain(obj, predicate, max_depth=20, extra_ignore=()):
    return _find_chain(obj, predicate, gc.get_referrers, max_depth=max_depth, extra_ignore=extra_ignore)


def show_backrefs(objs, max_depth=3, extra_ignore=(), filter=None, too_many=10, highlight=None, filename=None, extra_info=None, refcounts=False, shortnames=True, output=None):
    _show_graph(objs, max_depth=max_depth, extra_ignore=extra_ignore, filter=filter, too_many=too_many, highlight=highlight, edge_func=gc.get_referrers, swap_source_target=False, filename=filename, output=output, extra_info=extra_info, refcounts=refcounts, shortnames=shortnames, cull_func=is_proper_module)


def show_refs(objs, max_depth=3, extra_ignore=(), filter=None, too_many=10, highlight=None, filename=None, extra_info=None, refcounts=False, shortnames=True, output=None):
    _show_graph(objs, max_depth=max_depth, extra_ignore=extra_ignore, filter=filter, too_many=too_many, highlight=highlight, edge_func=gc.get_referents, swap_source_target=True, filename=filename, extra_info=extra_info, refcounts=refcounts, shortnames=shortnames, output=output)


def show_chain(*chains, **kw):
    backrefs = kw.pop('backrefs', True)
    chains = [ chain for chain in chains if chain ]

    def in_chains(x, ids=set(map(id, itertools.chain(*chains)))):
        return id(x) in ids

    max_depth = max(map(len, chains)) - 1
    if backrefs:
        show_backrefs([ chain[-1] for chain in chains ], max_depth=max_depth, filter=in_chains, **kw)
    else:
        show_refs([ chain[0] for chain in chains ], max_depth=max_depth, filter=in_chains, **kw)


def is_proper_module(obj):
    return inspect.ismodule(obj) and obj is sys.modules.get(getattr(obj, '__name__', None))


def _find_chain(obj, predicate, edge_func, max_depth=20, extra_ignore=()):
    queue = [obj]
    depth = {id(obj): 0}
    parent = {id(obj): None}
    ignore = set(extra_ignore)
    ignore.add(id(extra_ignore))
    ignore.add(id(queue))
    ignore.add(id(depth))
    ignore.add(id(parent))
    ignore.add(id(ignore))
    ignore.add(id(sys._getframe()))
    ignore.add(id(sys._getframe(1)))
    gc.collect()
    while queue:
        target = queue.pop(0)
        if predicate(target):
            chain = [target]
            while parent[id(target)] is not None:
                target = parent[id(target)]
                chain.append(target)

            return chain
        tdepth = depth[id(target)]
        if tdepth < max_depth:
            referrers = edge_func(target)
            ignore.add(id(referrers))
            for source in referrers:
                if id(source) in ignore:
                    continue
                if id(source) not in depth:
                    depth[id(source)] = tdepth + 1
                    parent[id(source)] = target
                    queue.append(source)

    return [obj]


def _show_graph(objs, edge_func, swap_source_target, max_depth=3, extra_ignore=(), filter=None, too_many=10, highlight=None, filename=None, extra_info=None, refcounts=False, shortnames=True, output=None, cull_func=None):
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    if filename and output:
        raise ValueError('Cannot specify both output and filename.')
    elif output:
        f = output
    elif filename and filename.endswith('.dot'):
        f = codecs.open(filename, 'w', encoding='utf-8')
        dot_filename = filename
    else:
        fd, dot_filename = tempfile.mkstemp(prefix='objgraph-', suffix='.dot', text=True)
        f = os.fdopen(fd, 'w')
        if getattr(f, 'encoding', None):
            import io
            f = io.TextIOWrapper(f.detach(), 'utf-8')
    f.write('digraph ObjectGraph {\n  node[shape=box, style=filled, fillcolor=white];\n')
    queue = []
    depth = {}
    ignore = set(extra_ignore)
    ignore.add(id(objs))
    ignore.add(id(extra_ignore))
    ignore.add(id(queue))
    ignore.add(id(depth))
    ignore.add(id(ignore))
    ignore.add(id(sys._getframe()))
    ignore.add(id(sys._getframe().f_locals))
    ignore.add(id(sys._getframe(1)))
    ignore.add(id(sys._getframe(1).f_locals))
    for obj in objs:
        f.write('  %s[fontcolor=red];\n' % _obj_node_id(obj))
        depth[id(obj)] = 0
        queue.append(obj)
        del obj

    gc.collect()
    nodes = 0
    while queue:
        nodes += 1
        target = queue.pop(0)
        tdepth = depth[id(target)]
        f.write('  %s[label="%s"];\n' % (_obj_node_id(target), _obj_label(target, extra_info, refcounts, shortnames)))
        h, s, v = _gradient((0, 0, 1), (0, 0, 0.3), tdepth, max_depth)
        if inspect.ismodule(target):
            h = 0.3
            s = 1
        if highlight and highlight(target):
            h = 0.6
            s = 0.6
            v = 0.5 + v * 0.5
        f.write('  %s[fillcolor="%g,%g,%g"];\n' % (_obj_node_id(target),
         h,
         s,
         v))
        if v < 0.5:
            f.write('  %s[fontcolor=white];\n' % _obj_node_id(target))
        try:
            if hasattr(getattr(target, '__class__', None), '__del__'):
                f.write('  %s->%s_has_a_del[color=red,style=dotted,len=0.25,weight=10];\n' % (_obj_node_id(target), _obj_node_id(target)))
                f.write('  %s_has_a_del[label="__del__",shape=doublecircle,height=0.25,color=red,fillcolor="0,.5,1",fontsize=6];\n' % _obj_node_id(target))
        except ReferenceError:
            pass

        if tdepth >= max_depth:
            continue
        if cull_func is not None and cull_func(target):
            continue
        neighbours = edge_func(target)
        ignore.add(id(neighbours))
        n = 0
        skipped = 0
        for source in neighbours:
            if id(source) in ignore:
                continue
            if filter and not filter(source):
                continue
            if n >= too_many:
                skipped += 1
                continue
            if swap_source_target:
                srcnode, tgtnode = target, source
            else:
                srcnode, tgtnode = source, target
            elabel = _edge_label(srcnode, tgtnode, shortnames)
            f.write('  %s -> %s%s;\n' % (_obj_node_id(srcnode), _obj_node_id(tgtnode), elabel))
            if id(source) not in depth:
                depth[id(source)] = tdepth + 1
                queue.append(source)
            n += 1
            del source

        del neighbours
        if skipped > 0:
            h, s, v = _gradient((0, 1, 1), (0, 1, 0.3), tdepth + 1, max_depth)
            if swap_source_target:
                label = '%d more references' % skipped
                edge = '%s->too_many_%s' % (_obj_node_id(target), _obj_node_id(target))
            else:
                label = '%d more backreferences' % skipped
                edge = 'too_many_%s->%s' % (_obj_node_id(target), _obj_node_id(target))
            f.write('  %s[color=red,style=dotted,len=0.25,weight=10];\n' % edge)
            f.write('  too_many_%s[label="%s",shape=box,height=0.25,color=red,fillcolor="%g,%g,%g",fontsize=6];\n' % (_obj_node_id(target),
             label,
             h,
             s,
             v))
            f.write('  too_many_%s[fontcolor=white];\n' % _obj_node_id(target))

    f.write('}\n')
    if output:
        return
    else:
        f.close()
        print 'Graph written to %s (%d nodes)' % (dot_filename, nodes)
        _present_graph(dot_filename, filename)
        return


def _present_graph(dot_filename, filename=None):
    if filename == dot_filename:
        return
    if not filename and _program_in_path('xdot'):
        print 'Spawning graph viewer (xdot)'
        subprocess.Popen(['xdot', dot_filename], close_fds=True)
    elif _program_in_path('dot'):
        if not filename:
            print 'Graph viewer (xdot) not found, generating a png instead'
            filename = dot_filename[:-4] + '.png'
        stem, ext = os.path.splitext(filename)
        cmd = ['dot',
         '-T' + ext[1:],
         '-o' + filename,
         dot_filename]
        dot = subprocess.Popen(cmd, close_fds=False)
        dot.wait()
        if dot.returncode != 0:
            print 'dot failed (exit code %d) while executing "%s"' % (dot.returncode, ' '.join(cmd))
        else:
            print 'Image generated as %s' % filename
    elif not filename:
        print 'Graph viewer (xdot) and image renderer (dot) not found, not doing anything else'
    else:
        print 'Image renderer (dot) not found, not doing anything else'


def _obj_node_id(obj):
    return ('o%d' % id(obj)).replace('-', '_')


def _obj_label(obj, extra_info=None, refcounts=False, shortnames=True):
    if shortnames:
        label = [_short_typename(obj)]
    else:
        label = [_long_typename(obj)]
    if refcounts:
        label[0] += ' [%d]' % (sys.getrefcount(obj) - 4)
    label.append(_safe_repr(obj))
    if extra_info:
        label.append(str(extra_info(obj)))
    return _quote('\n'.join(label))


def _quote(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\x00', '\\\\0')


def _get_obj_type(obj):
    objtype = type(obj)
    if isinstance(obj, InstanceType):
        objtype = obj.__class__
    return objtype


def _short_typename(obj):
    return _get_obj_type(obj).__name__


def _long_typename(obj):
    objtype = _get_obj_type(obj)
    name = objtype.__name__
    module = getattr(objtype, '__module__', None)
    if module:
        return '%s.%s' % (module, name)
    else:
        return name
        return


def _safe_repr(obj):
    try:
        return _short_repr(obj)
    except:
        return '(unrepresentable)'


def _short_repr(obj):
    if isinstance(obj, (type,
     types.ModuleType,
     types.BuiltinMethodType,
     types.BuiltinFunctionType)):
        return obj.__name__
    else:
        if isinstance(obj, types.MethodType):
            try:
                if obj.__self__ is not None:
                    return obj.__func__.__name__ + ' (bound)'
                return obj.__func__.__name__
            except AttributeError:
                if obj.im_self is not None:
                    return obj.im_func.__name__ + ' (bound)'
                else:
                    return obj.im_func.__name__

        if isinstance(obj, types.FrameType):
            return '%s:%s' % (obj.f_code.co_filename, obj.f_lineno)
        return '%d items' % len(obj) if isinstance(obj, (tuple,
         list,
         dict,
         set)) else repr(obj)[:40]


def _gradient(start_color, end_color, depth, max_depth):
    if max_depth == 0:
        return start_color
    h1, s1, v1 = start_color
    h2, s2, v2 = end_color
    f = float(depth) / max_depth
    h = h1 * (1 - f) + h2 * f
    s = s1 * (1 - f) + s2 * f
    v = v1 * (1 - f) + v2 * f
    return (h, s, v)


def _edge_label(source, target, shortnames=True):
    if isinstance(target, dict) and target is getattr(source, '__dict__', None):
        return ' [label="__dict__",weight=10]'
    else:
        if isinstance(source, types.FrameType):
            if target is source.f_locals:
                return ' [label="f_locals",weight=10]'
            if target is source.f_globals:
                return ' [label="f_globals",weight=10]'
        if isinstance(source, types.MethodType):
            try:
                if target is source.__self__:
                    return ' [label="__self__",weight=10]'
                if target is source.__func__:
                    return ' [label="__func__",weight=10]'
            except AttributeError:
                if target is source.im_self:
                    return ' [label="im_self",weight=10]'
                if target is source.im_func:
                    return ' [label="im_func",weight=10]'

        if isinstance(source, types.FunctionType):
            for k in dir(source):
                if target is getattr(source, k):
                    return ' [label="%s",weight=10]' % _quote(k)

        if isinstance(source, dict):
            for k, v in iteritems(source):
                if v is target:
                    if isinstance(k, basestring) and _is_identifier(k):
                        return ' [label="%s",weight=2]' % _quote(k)
                    else:
                        if shortnames:
                            tn = _short_typename(k)
                        else:
                            tn = _long_typename(k)
                        return ' [label="%s"]' % _quote(tn + '\n' + _safe_repr(k))

        return ''


_is_identifier = re.compile('[a-zA-Z_][a-zA-Z_0-9]*$').match

def _program_in_path(program):
    path = os.environ.get('PATH', os.defpath).split(os.pathsep)
    path = [ os.path.join(dir, program) for dir in path ]
    path = [ True for file in path if os.path.isfile(file) or os.path.isfile(file + '.exe') ]
    return bool(path)
