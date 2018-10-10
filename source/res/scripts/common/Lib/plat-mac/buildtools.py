# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/buildtools.py
import warnings
warnings.warnpy3k('the buildtools module is deprecated and is removed in 3.0', stacklevel=2)
import sys
import os
import string
import imp
import marshal
from Carbon import Res
import Carbon.Files
import Carbon.File
import MacOS
import macostools
import macresource
try:
    import EasyDialogs
except ImportError:
    EasyDialogs = None

import shutil
BuildError = 'BuildError'
MAGIC = imp.get_magic()
TEMPLATE = 'PythonInterpreter'
RESTYPE = 'PYC '
RESNAME = '__main__'
OWNERNAME = 'owner resource'
DEFAULT_APPLET_CREATOR = 'Pyta'
READ = 1
WRITE = 2
RESOURCE_FORK_NAME = Carbon.File.FSGetResourceForkName()

def findtemplate(template=None):
    if MacOS.runtimemodel == 'macho':
        return None
    else:
        if not template:
            template = TEMPLATE
        for p in sys.path:
            file = os.path.join(p, template)
            try:
                file, d1, d2 = Carbon.File.FSResolveAliasFile(file, 1)
                break
            except (Carbon.File.Error, ValueError):
                continue

        else:
            raise BuildError, 'Template %r not found on sys.path' % (template,)

        file = file.as_pathname()
        return file


def process(template, filename, destname, copy_codefragment=0, rsrcname=None, others=[], raw=0, progress='default', destroot=''):
    if progress == 'default':
        if EasyDialogs is None:
            print 'Compiling %s' % (os.path.split(filename)[1],)
            process = None
        else:
            progress = EasyDialogs.ProgressBar('Processing %s...' % os.path.split(filename)[1], 120)
            progress.label('Compiling...')
            progress.inc(0)
    if '#' in os.path.split(filename)[1]:
        raise BuildError, 'BuildApplet could destroy your sourcefile on OSX, please rename: %s' % filename
    fp = open(filename, 'rU')
    text = fp.read()
    fp.close()
    try:
        code = compile(text + '\n', filename, 'exec')
    except SyntaxError as arg:
        raise BuildError, 'Syntax error in script %s: %s' % (filename, arg)
    except EOFError:
        raise BuildError, 'End-of-file in script %s' % (filename,)

    if string.lower(filename[-3:]) == '.py':
        basename = filename[:-3]
        if MacOS.runtimemodel != 'macho' and not destname:
            destname = basename
    else:
        basename = filename
    if not destname:
        if MacOS.runtimemodel == 'macho':
            destname = basename + '.app'
        else:
            destname = basename + '.applet'
    if not rsrcname:
        rsrcname = basename + '.rsrc'
    try:
        os.remove(destname)
    except os.error:
        pass

    process_common(template, progress, code, rsrcname, destname, 0, copy_codefragment, raw, others, filename, destroot)
    return


def update(template, filename, output):
    if MacOS.runtimemodel == 'macho':
        raise BuildError, 'No updating yet for MachO applets'
    if progress:
        if EasyDialogs is None:
            print 'Updating %s' % (os.path.split(filename)[1],)
            progress = None
        else:
            progress = EasyDialogs.ProgressBar('Updating %s...' % os.path.split(filename)[1], 120)
    else:
        progress = None
    if not output:
        output = filename + ' (updated)'
    try:
        os.remove(output)
    except os.error:
        pass

    process_common(template, progress, None, filename, output, 1, 1)
    return


def process_common(template, progress, code, rsrcname, destname, is_update, copy_codefragment, raw=0, others=[], filename=None, destroot=''):
    if MacOS.runtimemodel == 'macho':
        return process_common_macho(template, progress, code, rsrcname, destname, is_update, raw, others, filename, destroot)
    else:
        if others:
            raise BuildError, 'Extra files only allowed for MachoPython applets'
        template_fsr, d1, d2 = Carbon.File.FSResolveAliasFile(template, 1)
        template = template_fsr.as_pathname()
        if progress:
            progress.label('Copy data fork...')
            progress.set(10)
        if copy_codefragment:
            tmpl = open(template, 'rb')
            dest = open(destname, 'wb')
            data = tmpl.read()
            if data:
                dest.write(data)
            dest.close()
            tmpl.close()
            del dest
            del tmpl
        if progress:
            progress.label('Copy resources...')
            progress.set(20)
        try:
            output = Res.FSOpenResourceFile(destname, RESOURCE_FORK_NAME, WRITE)
        except MacOS.Error:
            destdir, destfile = os.path.split(destname)
            Res.FSCreateResourceFile(destdir, unicode(destfile), RESOURCE_FORK_NAME)
            output = Res.FSOpenResourceFile(destname, RESOURCE_FORK_NAME, WRITE)

        typesfound, ownertype = [], None
        try:
            input = Res.FSOpenResourceFile(rsrcname, RESOURCE_FORK_NAME, READ)
        except (MacOS.Error, ValueError):
            if progress:
                progress.inc(50)
        else:
            if is_update:
                skip_oldfile = ['cfrg']
            else:
                skip_oldfile = []
            typesfound, ownertype = copyres(input, output, skip_oldfile, 0, progress)
            Res.CloseResFile(input)

        skiptypes = []
        if 'vers' in typesfound:
            skiptypes.append('vers')
        if 'SIZE' in typesfound:
            skiptypes.append('SIZE')
        if 'BNDL' in typesfound:
            skiptypes = skiptypes + ['BNDL',
             'FREF',
             'icl4',
             'icl8',
             'ics4',
             'ics8',
             'ICN#',
             'ics#']
        if not copy_codefragment:
            skiptypes.append('cfrg')
        input = Res.FSOpenResourceFile(template, RESOURCE_FORK_NAME, READ)
        dummy, tmplowner = copyres(input, output, skiptypes, 1, progress)
        Res.CloseResFile(input)
        Res.UseResFile(output)
        if ownertype is None:
            newres = Res.Resource('\x00')
            newres.AddResource(DEFAULT_APPLET_CREATOR, 0, 'Owner resource')
            ownertype = DEFAULT_APPLET_CREATOR
        if code:
            try:
                res = Res.Get1NamedResource(RESTYPE, RESNAME)
                res.RemoveResource()
            except Res.Error:
                pass

            if progress:
                progress.label('Write PYC resource...')
                progress.set(120)
            data = marshal.dumps(code)
            del code
            data = MAGIC + '\x00\x00\x00\x00' + data
            id = 0
            while id < 128:
                id = Res.Unique1ID(RESTYPE)

            res = Res.Resource(data)
            res.AddResource(RESTYPE, id, RESNAME)
            attrs = res.GetResAttrs()
            attrs = attrs | 4
            res.SetResAttrs(attrs)
            res.WriteResource()
            res.ReleaseResource()
        Res.CloseResFile(output)
        dest_fss = Carbon.File.FSSpec(destname)
        dest_finfo = dest_fss.FSpGetFInfo()
        dest_finfo.Creator = ownertype
        dest_finfo.Type = 'APPL'
        dest_finfo.Flags = dest_finfo.Flags | Carbon.Files.kHasBundle | Carbon.Files.kIsShared
        dest_finfo.Flags = dest_finfo.Flags & ~Carbon.Files.kHasBeenInited
        dest_fss.FSpSetFInfo(dest_finfo)
        macostools.touched(destname)
        if progress:
            progress.label('Done.')
            progress.inc(0)
        return


def process_common_macho(template, progress, code, rsrcname, destname, is_update, raw=0, others=[], filename=None, destroot=''):
    if filename is None:
        raise BuildError, 'Need source filename on MacOSX'
    if destname[-4:] != '.app':
        destname = destname + '.app'
    destdir, shortname = os.path.split(destname)
    if shortname[-4:] == '.app':
        shortname = shortname[:-4]
    plistname = None
    icnsname = None
    if rsrcname and rsrcname[-5:] == '.rsrc':
        tmp = rsrcname[:-5]
        plistname = tmp + '.plist'
        if os.path.exists(plistname):
            icnsname = tmp + '.icns'
            if not os.path.exists(icnsname):
                icnsname = None
        else:
            plistname = None
    if not icnsname:
        dft_icnsname = os.path.join(sys.prefix, 'Resources/Python.app/Contents/Resources/PythonApplet.icns')
        if os.path.exists(dft_icnsname):
            icnsname = dft_icnsname
    if not os.path.exists(rsrcname):
        rsrcname = None
    if progress:
        progress.label('Creating bundle...')
    import bundlebuilder
    builder = bundlebuilder.AppBuilder(verbosity=0)
    builder.mainprogram = filename
    builder.builddir = destdir
    builder.name = shortname
    builder.destroot = destroot
    if rsrcname:
        realrsrcname = macresource.resource_pathname(rsrcname)
        builder.files.append((realrsrcname, os.path.join('Contents/Resources', os.path.basename(rsrcname))))
    for o in others:
        if type(o) == str:
            builder.resources.append(o)
        builder.files.append(o)

    if plistname:
        import plistlib
        builder.plist = plistlib.Plist.fromFile(plistname)
    if icnsname:
        builder.iconfile = icnsname
    if not raw:
        builder.argv_emulation = 1
    builder.setup()
    builder.build()
    if progress:
        progress.label('Done.')
        progress.inc(0)
    return


def copyres(input, output, skiptypes, skipowner, progress=None):
    ctor = None
    alltypes = []
    Res.UseResFile(input)
    ntypes = Res.Count1Types()
    progress_type_inc = 50 / ntypes
    for itype in range(1, 1 + ntypes):
        type = Res.Get1IndType(itype)
        if type in skiptypes:
            continue
        alltypes.append(type)
        nresources = Res.Count1Resources(type)
        progress_cur_inc = progress_type_inc / nresources
        for ires in range(1, 1 + nresources):
            res = Res.Get1IndResource(type, ires)
            id, type, name = res.GetResInfo()
            lcname = string.lower(name)
            if lcname == OWNERNAME and id == 0:
                if skipowner:
                    continue
                else:
                    ctor = type
            size = res.size
            attrs = res.GetResAttrs()
            if progress:
                progress.label('Copy %s %d %s' % (type, id, name))
                progress.inc(progress_cur_inc)
            res.LoadResource()
            res.DetachResource()
            Res.UseResFile(output)
            try:
                res2 = Res.Get1Resource(type, id)
            except MacOS.Error:
                res2 = None

            if res2:
                if progress:
                    progress.label('Overwrite %s %d %s' % (type, id, name))
                    progress.inc(0)
                res2.RemoveResource()
            res.AddResource(type, id, name)
            res.WriteResource()
            attrs = attrs | res.GetResAttrs()
            res.SetResAttrs(attrs)
            Res.UseResFile(input)

    return (alltypes, ctor)


def copyapptree(srctree, dsttree, exceptlist=[], progress=None):
    names = []
    if os.path.exists(dsttree):
        shutil.rmtree(dsttree)
    os.mkdir(dsttree)
    todo = os.listdir(srctree)
    while todo:
        this, todo = todo[0], todo[1:]
        if this in exceptlist:
            continue
        thispath = os.path.join(srctree, this)
        if os.path.isdir(thispath):
            thiscontent = os.listdir(thispath)
            for t in thiscontent:
                todo.append(os.path.join(this, t))

        names.append(this)

    for this in names:
        srcpath = os.path.join(srctree, this)
        dstpath = os.path.join(dsttree, this)
        if os.path.isdir(srcpath):
            os.mkdir(dstpath)
        if os.path.islink(srcpath):
            endpoint = os.readlink(srcpath)
            os.symlink(endpoint, dstpath)
        if progress:
            progress.label('Copy ' + this)
            progress.inc(0)
        shutil.copy2(srcpath, dstpath)


def writepycfile(codeobject, cfile):
    import marshal
    fc = open(cfile, 'wb')
    fc.write('\x00\x00\x00\x00')
    fc.write('\x00\x00\x00\x00')
    marshal.dump(codeobject, fc)
    fc.flush()
    fc.seek(0, 0)
    fc.write(MAGIC)
    fc.close()
