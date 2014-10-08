from nfs4_const import *
from nfs4_type import *
from environment import check, checklist, compareTimes, makeBadID, makeBadIDganesha, makeStaleId
import struct

_text = 'write data' # len=10

def _compare(t, res, expect, eof=True):
    check(res, msg="READ after WRITE")
    count = len(res.data)
    if res.data != expect[:count]:
        t.fail("READ returned %s, expected %s" %
               (repr(res.data), repr(expect)))
    if count < len(expect):
        if res.eof:
             t.fail("READ returned EOF after getting %s, expected %s" %
                   (repr(res.data), repr(expect)))
        else:
             t.pass_warn("READ returned %i characters, expected %i" %
                        (count, len(expect)))
    if res.eof != eof:
        if eof:
            t.fail("READ to file end returned without EOF set")
        else:
            t.fail("READ unexpectedly returned EOF")

#############################################

def testSimpleWrite(t, env):
    """WRITE with stateid=zeros and UNSTABLE4

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT1
    """
    c = env.c1
    c.init_connection()
    attrs = {FATTR4_SIZE: 32, FATTR4_MODE: 0644}
    fh, stateid = c.create_confirm(t.code, attrs=attrs,
                                   deny=OPEN4_SHARE_DENY_NONE)
    res = c.write_file(fh, _text, how=UNSTABLE4)
    check(res, msg="WRITE with stateid=zeros and UNSTABLE4")
    res = c.read_file(fh, 0, 20)
    _compare(t, res, _text + '\0'*(20-len(_text)), False)

def testSimpleWrite2(t, env):
    """WRITE with stateid=zeros changing size

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT1b
    """
    c = env.c1
    c.init_connection()
    attrs = {FATTR4_SIZE: 32, FATTR4_MODE: 0644}
    fh, stateid = c.create_confirm(t.code, attrs=attrs,
                                   deny=OPEN4_SHARE_DENY_NONE)
    res = c.write_file(fh, _text, 30)
    check(res, msg="WRITE with stateid=zeros changing size")
    res = c.read_file(fh, 25, 20)
    _compare(t, res, '\0'*5 + _text, True)

def testStateidOne(t, env):
    """WRITE with stateid=ones and DATA_SYNC4

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT2
    """
    c = env.c1
    c.init_connection()
    attrs = {FATTR4_SIZE: 32, FATTR4_MODE: 0644}
    fh, stateid = c.create_confirm(t.code, attrs=attrs,
                                   deny=OPEN4_SHARE_DENY_NONE)
    res = c.write_file(fh, _text, 5, env.stateid1, DATA_SYNC4)
    check(res, msg="WRITE with stateid=ones and DATA_SYNC4")
    if res.committed == UNSTABLE4:
        t.fail("WRITE asked for DATA_SYNC4, got UNSTABLE4")
    res = c.read_file(fh, 0, 20)
    _compare(t, res, '\0'*5 + _text + '\0'*(20-5-len(_text)), False)
    
def testWithOpen(t, env):
    """WRITE with openstateid and FILE_SYNC4

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT3
    """
    c = env.c1
    c.init_connection()
    attrs = {FATTR4_SIZE: 32, FATTR4_MODE: 0644}
    fh, stateid = c.create_confirm(t.code, attrs=attrs)
    res = c.write_file(fh, _text, 50, stateid, FILE_SYNC4)
    check(res, msg="WRITE with openstateid and FILE_SYNC4")
    if res.committed != FILE_SYNC4:
        t.fail("WRITE asked for FILE_SYNC4, did not get it")
    res = c.read_file(fh, 0, 100)
    _compare(t, res, '\0'*50 + _text, True)
    
def testNoData(t, env):
    """WRITE with no data

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT4
    """
    c = env.c1
    c.init_connection()
    attrs = {FATTR4_SIZE: 32, FATTR4_MODE: 0644}
    fh, stateid = c.create_confirm(t.code, attrs=attrs)
    time_prior = c.do_getattr(FATTR4_TIME_MODIFY, fh)
    env.sleep(1)
    res = c.write_file(fh, '', 5, stateid)
    check(res, msg="WRITE with no data")
    if res.count:
        t.fail("WRITE with no data returned count=%i" % res.count)
    # Now ensure time_modify was unchanged
    time_after = c.do_getattr(FATTR4_TIME_MODIFY, fh)
    if compareTimes(time_prior,time_after) != 0:
        t.fail("WRITE with no data affected time_modify")

def testLargeData(t, env):
    """WRITE with a large amount of data

    FLAGS: write read all
    DEPEND: MKFILE
    CODE: WRT5
    """
    c = env.c1
    c.init_connection()
    fh, stateid = c.create_confirm(t.code)
    data = "abcdefghijklmnopq" * 0x10000
    # Write the data
    pos = 0
    while pos < len(data):
        res = c.write_file(fh, data[pos:], pos, stateid)
        check(res, msg="WRITE with a large amount of data")
        pos += res.count
        if res.count == 0:
            t.fail("WRITE with a large amount of data returned count=0")
    # Read the data back in
    eof = False
    newdata = ''
    while not eof:
        res = c.read_file(fh, len(newdata), len(data) - len(newdata), stateid)
        check(res, msg="READ with large amount of data")
        newdata += res.data
        eof = res.eof
    if data != newdata:
        t.fail("READ did not correspond to WRITE with large dataset")

def testDir(t, env):
    """WRITE to a dir should return NFS4ERR_ISDIR

    FLAGS: write dir all
    DEPEND: MKDIR
    CODE: WRT6d
    """
    c = env.c1
    path = c.homedir + [t.code]
    res = c.create_obj(path)
    check(res)
    res = c.write_file(path, _text)
    check(res, NFS4ERR_ISDIR, "WRITE to a dir")

def testLink(t, env):
    """WRITE to a non-file should return NFS4ERR_INVAL

    FLAGS: write symlink all
    DEPEND: MKLINK
    CODE: WRT6a
    """
    c = env.c1
    path = c.homedir + [t.code]
    res = c.create_obj(path, NF4LNK)
    check(res)
    res = c.write_file(path, _text)
    checklist(res, [NFS4ERR_INVAL, NFS4ERR_SYMLINK], "WRITE to a symlink")

def testBlock(t, env):
    """WRITE to a non-file should return NFS4ERR_INVAL

    FLAGS: write block all
    DEPEND: MKBLK
    CODE: WRT6b
    """
    c = env.c1
    path = c.homedir + [t.code]
    res = c.create_obj(path, NF4BLK)
    check(res)
    res = c.write_file(path, _text)
    check(res, NFS4ERR_INVAL, "WRITE to a block device")

def testChar(t, env):
    """WRITE to a non-file should return NFS4ERR_INVAL

    FLAGS: write char all
    DEPEND: MKCHAR
    CODE: WRT6c
    """
    c = env.c1
    path = c.homedir + [t.code]
    res = c.create_obj(path, NF4CHR)
    check(res)
    res = c.write_file(path, _text)
    check(res, NFS4ERR_INVAL, "WRITE to a character device")

def testFifo(t, env):
    """WRITE to a non-file should return NFS4ERR_INVAL

    FLAGS: write fifo all
    DEPEND: MKFIFO
    CODE: WRT6f
    """
    c = env.c1
    path = c.homedir + [t.code]
    res = c.create_obj(path, NF4FIFO)
    check(res)
    res = c.write_file(path, _text)
    check(res, NFS4ERR_INVAL, "WRITE to a fifo")

def testSocket(t, env):
    """WRITE to a non-file should return NFS4ERR_INVAL

    FLAGS: write socket all
    DEPEND: MKSOCK
    CODE: WRT6s
    """
    c = env.c1
    path = c.homedir + [t.code]
    res = c.create_obj(path, NF4SOCK)
    check(res)
    res = c.write_file(path, _text)
    check(res, NFS4ERR_INVAL, "WRITE to a socket")

def testNoFh(t, env):
    """WRITE with no (cfh) should return NFS4ERR_NOFILEHANDLE

    FLAGS: write emptyfh all
    CODE: WRT7
    """
    c = env.c1
    res = c.write_file(None, _text)
    check(res, NFS4ERR_NOFILEHANDLE, "WRITE with no <cfh>")

def testOpenMode(t, env):
    """WRITE with file opened in READ mode should return NFS4ERR_OPENMODE

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT8
    """
    c = env.c1
    c.init_connection()
    attrs = {FATTR4_SIZE: 32, FATTR4_MODE: 0644}
    fh, stateid = c.create_confirm(t.code, attrs=attrs,
                                   access=OPEN4_SHARE_ACCESS_READ)
    res = c.write_file(fh, _text, 0, stateid)
    check(res, NFS4ERR_OPENMODE, "WRITE with file opened in READ mode")
    
def testShareDeny(t, env):
    """WRITE to file with DENY set should return NFS4ERR_LOCKED

    See 8.1.4, top of third paragraph

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT9
    """
    c = env.c1
    c.init_connection()
    attrs = {FATTR4_SIZE: 32, FATTR4_MODE: 0644}
    fh, stateid = c.create_confirm(t.code, attrs=attrs,
                                   deny=OPEN4_SHARE_DENY_WRITE)
    res = c.write_file(fh, _text)
    check(res, NFS4ERR_LOCKED, "WRITE to file with DENY set")
    
# WRT10 requires a server specific manipulation of the stateid
#       each server will have it's own implementation, there is
#       no general version.
def testBadStateidGanesha(t, env):
    """WRITE with bad stateid should return NFS4ERR_BAD_STATEID

    FLAGS: ganesha
    DEPEND: MKFILE
    CODE: WRT10g
    """
    c = env.c1
    c.init_connection()
    fh, stateid = c.create_confirm(t.code)
    res = c.write_file(fh, _text, 0, makeBadIDganesha(stateid))
    check(res, NFS4ERR_BAD_STATEID, "WRITE with bad stateid")
    
def testStaleStateid(t, env):
    """WRITE with stale stateid should return NFS4ERR_STALE_STATEID

    FLAGS: write staleid all
    DEPEND: MKFILE
    CODE: WRT11
    """
    c = env.c1
    c.init_connection()
    fh, stateid = c.create_confirm(t.code)
    res = c.write_file(fh, _text, 0, makeStaleId(stateid))
    check(res, NFS4ERR_STALE_STATEID, "WRITE with stale stateid")

def testOldStateid(t, env):
    """WRITE with old stateid should return NFS4ERR_OLD_STATEID

    FLAGS: write oldid all
    DEPEND: MKFILE
    CODE: WRT12
    """
    c = env.c1
    c.init_connection()
    res = c.create_file(t.code)
    check(res, msg="Creating file %s" % t.code)
    oldstateid = res.resarray[-2].switch.switch.stateid
    fh, stateid = c.confirm(t.code, res)
    res = c.write_file(fh, _text, 0, oldstateid)
    check(res, NFS4ERR_OLD_STATEID, "WRITE with old stateid")

def testDoubleWrite(t, env):
    """Two WRITEs in a compound

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT13
    """
    c = env.c1
    c.init_connection()
    fh, stateid = c.create_confirm(t.code, deny=OPEN4_SHARE_DENY_NONE)
    ops = c.use_obj(fh)
    ops += [c.write_op(stateid4(0, ''), 0, UNSTABLE4, 'one')]
    ops += [c.write_op(stateid4(0, ''), 3, UNSTABLE4, 'two')]
    res = c.compound(ops)
    res = c.read_file(fh, 0, 6)
    _compare(t, res, 'onetwo', True)

def _get_iosize(t, c, path):
    d = c.do_getattrdict(path, [FATTR4_MAXREAD, FATTR4_MAXWRITE])
    # I can't find any official minimums, so these are arbitrary:
    if FATTR4_MAXREAD not in d:
        d[FATTR4_MAXREAD] = 128
    if FATTR4_MAXWRITE not in d:
        d[FATTR4_MAXWRITE] = 128
    return d[FATTR4_MAXREAD], d[FATTR4_MAXWRITE]

def testLargeWrite(t, env):
    """large WRITE

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT14
    """
    c = env.c1
    c.init_connection()
    fh, stateid = c.create_confirm(t.code, deny=OPEN4_SHARE_DENY_NONE)
    maxread, maxwrite = _get_iosize(t, c, c.homedir)
    res = c.write_file(fh, 'A'*maxwrite, how=UNSTABLE4)
    check(res, msg="WRITE with stateid=zeros and UNSTABLE4")

def testSizes(t, env):
    """bunch of various-sized writes

    FLAGS: write all
    DEPEND: MKFILE
    CODE: WRT15
    """

    min = 0;
    max = 8192;
    buf = ""
    # I've found it helpful when tracking down decoding errors to know
    # where in the packet a given word or data came from; this helps:
    for i in range(0, (max+3)/4):
        buf += struct.pack('>L', i);
    c = env.c1
    c.init_connection()
    fh, stateid = c.create_confirm(t.code, deny=OPEN4_SHARE_DENY_NONE)
    for i in range(0, max):
        ops = c.use_obj(fh)
        ops += [c.write_op(stateid4(0, ''), 0, UNSTABLE4, buf[0:i])]
        ops += [c.getattr([FATTR4_SIZE]), c.getattr([FATTR4_SIZE])]
        res = c.compound(ops)
        check(res, msg="length %d WRITE" % i)

def testLargeReadWrite(t, env):
    """Compound with large READ and large WRITE

    FLAGS: write
    DEPEND: MKFILE
    CODE: WRT16
    """
    c = env.c1
    c.init_connection()
    maxread, maxwrite = _get_iosize(t, c, c.homedir)
    # linux server really should be able to handle (maxread, maxwrite)
    # but can't:
    size = min(maxread/4, maxwrite/4)
    writedata = 'A'*size
    attrs = {FATTR4_SIZE: size}
    fh, stateid = c.create_confirm(t.code, attrs=attrs,
                                    deny=OPEN4_SHARE_DENY_NONE)
    ops = c.use_obj(fh)
    ops += [c.read_op(stateid, 0, size)]
    ops += [c.write_op(stateid, 0, UNSTABLE4, writedata)]
    res = c.compound(ops)
    check(res)
    data = res.resarray[-2].switch.switch.data
    if len(data) != len(writedata):
	    t.fail("READ returned %d bytes, expected %d" %
                                    (len(data), len(writedata)))
    if (data != '\0'*size):
        t.fail("READ returned unexpected data")
    res = c.read_file(fh, 0, size)
    _compare(t, res, writedata, True)

def testMultipleReadWrites(t,env):
    """Compound with multiple writes, then compound with multiple reads

    FLAGS: write
    DEPEND: MKFILE
    CODE: WRT17
    """
    # note: some overlapping ranges might be a good idea too.

    # random offsets, one on a 4096-byte page boundary:
    offsets = [0, 516, 3025, 7026, 8192, 15284]
    data = ""
    for i in range(0, (offsets[-1] + 3)/4):
        data += struct.pack('>L', i)
    c = env.c1
    c.init_connection()
    fh, stateid = c.create_confirm(t.code)
    ops = c.use_obj(fh)
    for i in range(0, len(offsets) - 1):
        ops += [c.write_op(stateid, offsets[i], UNSTABLE4,
					data[offsets[i]:offsets[i+1]])]
    res = c.compound(ops)
    check(res, msg="compound with multiple WRITE operations")
    ops = c.use_obj(fh)
    # read using different offsets, just for fun:
    read_offsets = [0, 9010, 9011, 12288, 15284]
    for i in range(0, len(read_offsets) - 1):
        offset = read_offsets[i]
        bytes = read_offsets[i+1] - offset;
        ops += [c.read_op(stateid, offset, bytes)]
    res = c.compound(ops)
    check(res, msg="compound with multiple READ operations")
    for i in range(0, len(read_offsets) - 2):
        resdata = res.resarray[i + 1 - len(read_offsets)].switch.switch.data
        expect = data[read_offsets[i]:read_offsets[i+1]]
        if len(resdata) != len(expect):
            t.fail("READ %d got %d bytes, expected %d" %
                    (i+1, len(resdata), len(expect)))
        if resdata != expect:
            t.fail("READ %d returned %s, expected %s" %
                    (i+1, repr(resdata), repr(expect)))
