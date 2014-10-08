from rpc_const import AUTH_NONE, AUTH_SYS, RPCSEC_GSS, SUCCESS, CALL, \
    MSG_ACCEPTED
from rpc_type import opaque_auth, authsys_parms
from rpc_pack import RPCPacker, RPCUnpacker
from gss_pack import GSSPacker, GSSUnpacker
from xdrlib import Packer, Unpacker
import rpclib
from gss_const import *
import gss_type
from gss_type import rpc_gss_init_res
try:
    import gssapi
except ImportError:
    print("Could not find gssapi module, proceeding without")
    gssapi = None
import threading
import logging

log_gss = logging.getLogger("rpc.sec.gss")
log_gss.setLevel(logging.INFO)

WINDOWSIZE = 8 # STUB, curently just a completely random number

class SecError(Exception):
    pass

class CredInfo(object):
    """Information needed to build CALL credential"""
    def _get__principle(self):
        if self.flavor == AUTH_NONE:
            return "nobody"
        elif self.flavor == AUTH_SYS:
            # STUB
            return "%s@%s" % (self.context.uid, self.context.machinename)
        elif self.flavor == RPCSEC_GSS:
            c = self.sec._get_context(self.context)
            if c is None:
                return "gss_nobody" # STUB
            else:
                return c.source_name.name
        else:
            raise
    flavor = property(lambda s: s.sec.flavor)
    principal = property(_get__principle)
    def __init__(self, sec=None, context=None,
                 service=rpc_gss_svc_none, gss_proc=RPCSEC_GSS_DATA, qop=0):
        if sec is None:
            sec = AuthNone()
        self.sec = sec # Instance of Auth*
        # For client - context is the string sent over-the-wire in the cred
        self.context = context # handle or authsys_parms
        self.service = service
        self.qop = qop
        self.gss_proc = gss_proc
        # self.triple = triple # (OID, QOP, service), only valid with GSS

class AuthNone(object):
    """Class that implements security interface, while giving no security.

    Note that we rely on fact that AuthNone has no state.
    XXX Could make this a singleton.
    """
    flavor = AUTH_NONE
    name = "AUTH_NONE"

    def get_info(self, header):
        return Info(self.flavor)

    def make_reply_verf(self, cred, stat):
        """Verifier sent by server with each MSG_ACCEPTED reply"""
        return rpclib.NULL_CRED

    def make_call_verf(self, xid, body):
        return rpclib.NULL_CRED

    def unsecure_data(self, cred, data):
        """Remove any security cruft from data"""
        return data

    def secure_data(self, msg, data):
        """Add security info/encrypttion to data"""
        # What we need from msg is: gss_seq_num (from credential) and qop
        # NOTE that for a reply, need the cred from the call
        return data

    @staticmethod
    def pack_cred(py_data):
        """Take opaque_auth.body type and pack it as opaque"""
        # For auth_none, py_data==''
        return py_data

    @staticmethod
    def unpack_cred(data):
        """Take opaque_auth.body and de-opaque it"""
        # For auth_none, data==''
        return data

    def init_cred(self):
        """Update info used for make_cred"""
        return CredInfo(self)

    def make_cred(self, credinfo):
        """Create credential"""
        return rpclib.NULL_CRED

    def check_auth(self, msg, data):
        """Server check of credentials, which can raise a RPCFlowControl"""
        # STUB
        # Check cred and verf have no XDR errors
        # Check verifier == rpclib.NULL_CRED
        return CredInfo(self)

    def check_reply_verf(self, msg, call_cred, data):
        if msg.stat == MSG_ACCEPTED and not self.is_NULL(msg.body.verf):
            raise SecError("Bad reply verifier - expected NULL verifier")

    def is_NULL(self, cred):
        return cred.flavor == AUTH_NONE and cred.body == ''

class AuthSys(AuthNone):
    """Standard UNIX based security, defined in Appendix A of RFC 1831"""
    flavor = AUTH_SYS
    name = "AUTH_SYS"

    def get_info(self, py_header):
        return Info(self.flavor, py_header.cred.body)

    @staticmethod
    def pack_cred(py_cred):
        p = RPCPacker()
        p.pack_authsys_parms(py_cred)
        return p.get_buffer()

    @staticmethod
    def unpack_cred(cred):
        p = RPCUnpacker(cred)
        py_cred = p.unpack_authsys_parms()
        p.done()
        return py_cred

    def init_cred(self, uid=None, gid=None, name=None, stamp=42, gids=None):
        # STUB - need intelligent way to set defaults
        if uid is None:
            uid = 0
        if gid is None:
            gid = 0
        if name is None:
            name = "default machinename - STUB"
        if gids is None:
            gids = [3, 17, 100]
        return CredInfo(self, authsys_parms(stamp, name, uid, gid, gids))

    def make_cred(self, credinfo):
        """Create credential"""
        if credinfo is None:
            # Create a default cred
            who = self.init_cred()
        else:
            # XXX Check credinfo.flavor?
            who = credinfo.context
        out = opaque_auth(AUTH_SYS, who)
        out.opaque = False # HACK
        return out

    def check_auth(self, msg, data):
        """Server check of credentials, which can raise a RPCFlowControl"""
        # STUB
        # Check cred and verf have no XDR errors
        # Check verifier == rpclib.NULL_CRED
        return CredInfo(self, msg.cred.body)

class GSSContext(object):
    def __init__(self, context_ptr):
        self.lock = threading.Lock()
        self.ptr = context_ptr
        self.seqid = 0 # client - next seqid to use
        self.highest = 0 # server - highest seqid seen
        self.seen = 0 # server - bitmask of seen requests

    def __getattr__(self, attr):
        return self.ptr.__getattribute__(attr)

    def expired(self):
        """Return True if context has expired, False otherwise"""
        # STUB
        return False

    def get_seqid(self):
        self.lock.acquire()
        out = self.seqid
        self.seqid += 1
        # BUG - check for overflow
        self.lock.release()
        return out

    def check_seqid(self, seqid):
        # Based on RFC 2203 Sect 5.3.3.1
        self.lock.acquire()
        try:
            diff = seqid - self.highest
            if diff <= -WINDOWSIZE:
                # Falls outside window
                raise rpclib.RPCDrop
            elif diff > 0:
                # New highest seqid
                self.highest += diff
                # Shift seen mask to reflect
                self.seen >>= diff
                self.seen |= (1 << (WINDOWSIZE - 1))
            else:
                # Within window, check for repeat
                if (1 << (-diff)) & self.seen:
                    raise rpclib.RPCDrop
        finally:
            self.lock.release()

class AuthGss(AuthNone):
    flavor = RPCSEC_GSS
    name = "RPCSEC_GSS"

    def __init__(self):
        self.contexts = {} # {str handle: GSSContext}

    def _add_context(self, context, handle=None):
        if handle is None:
            # Server
            handle = repr(context.handle)
        else:
            # Client uses server provided handle
            pass
        # BUG - what if already there?  Prob need some locking
        self.contexts[handle] = GSSContext(context)
        return handle

    def _get_context(self, handle):
        return self.contexts.get(handle, None)

    def init_given_context(self, context, handle=None,
                           service=rpc_gss_svc_none):
        self._add_context(context, handle)
        return CredInfo(self, context=handle, service=service)

    def init_cred(self, call, target="nfs@jupiter", source=None, oid=None):
        # STUB - need intelligent way to set defaults
        good_major = [gssapi.GSS_S_COMPLETE, gssapi.GSS_S_CONTINUE_NEEDED]
        p = Packer()
        up = GSSUnpacker('')
        # Set target (of form nfs@SERVER)
        target = gssapi.Name(target, gssapi.NT_HOSTBASED_SERVICE)
        # Set source (of form USERNAME)
        if source is not None:
            source = gssapi.Name(source, gssapi.NT_USER_NAME)
            gss_cred = gssapi.Credential(gssapi.INITIATE, source.ptr) # XXX
        else:
            # Just use default cred
            gss_cred = None
        context = gssapi.Context()
        token = None
        handle = ''
        proc = RPCSEC_GSS_INIT
        while True:
            # Call initSecContext.  If it returns COMPLETE, we are done.
            # If it returns CONTINUE_NEEDED, we must send d['token']
            # to the target, which will run it through acceptSecContext,
            # and give us back a token we need to send through initSecContext.
            # Repeat as necessary.
            token = context.init(target, token, gss_cred)
            if context.open:
                # XXX if res.major == CONTINUE there is a bug in library code
                # STUB - now what? Just use context?
                # XXX need to use res.seq_window
                # XXX - what if handle still '' ?
                self._add_context(context, handle)
                break
            # Send token to target using protocol of RFC 2203 sect 5.2.2
            credinfo = CredInfo(self, context=handle,
                                gss_proc=proc)
            proc = RPCSEC_GSS_CONTINUE_INIT
            p.reset()
            p.pack_opaque(token)
            header, reply = call(p.get_buffer(), credinfo)
            up.reset(reply)
            res = up.unpack_rpc_gss_init_res()
            up.done()
            # res now holds relevent output from target's acceptSecContext call
            if res.gss_major not in good_major:
                raise gssapi.Error(res.gss_major, res.gss_minor)
            handle = res.handle # Should not change between calls
            token = res.gss_token # This needs to be sent to initSecContext
        return CredInfo(self, context=handle)

    @staticmethod
    def pack_cred(py_cred):
        p = GSSPacker()
        p.pack_rpc_gss_cred_t(py_cred)
        return p.get_buffer()

    @staticmethod
    def unpack_cred(cred):
        p = GSSUnpacker(cred)
        py_cred = p.unpack_rpc_gss_cred_t()
        p.done()
        return py_cred

    def make_cred(self, credinfo):
        log_gss.debug("Calling make_cred %r" % credinfo)
        # XXX Deal with a default credinfo==None?
        if credinfo.gss_proc in (RPCSEC_GSS_INIT, RPCSEC_GSS_CONTINUE_INIT):
            context = None
            seqid = 0 # Should be ignored by server
        else:
            context = self._get_context(credinfo.context)
            seqid = context.get_seqid()
        service = credinfo.service
        data = gss_type.rpc_gss_cred_vers_1_t(credinfo.gss_proc, seqid,
                                              credinfo.service,
                                              credinfo.context) # str
        cred = gss_type.rpc_gss_cred_t(RPCSEC_GSS_VERS_1, data)
        out = opaque_auth(RPCSEC_GSS, cred)
        out.opaque = False # HACK to tell system we haven't packed cred
        out.context = context # This needs to be Context()
        out.body.qop = credinfo.qop
        log_gss.debug("make_cred = %r" % out)
        return out

    def unsecure_data(self, cred, data):
        def pull_seqnum(blob):
            """Pulls initial seq_num off of blob, checks it, then returns data.
            """
            # blob = seq_num + data
            p.reset(blob)
            try:
                seq_num = p.unpack_uint()
            except:
                log_gss.exception("unsecure_data - unpacking seq_num")
                raise rpclib.RPCUnsuccessfulReply(GARBAGE_ARGS)
            if seq_num != cred.seq_num:
                raise rpclib.RPCUnsuccessfulReply(GARBAGE_ARGS)
            return p.get_buffer()[p.get_position():]

        def check_gssapi(qop):
            if qop != cred.qop:
                # XXX Not sure what error to give here
                log_gss.warn("unsecure_data: mismatched qop %i != %i" %
                             (qop, cred.qop))
                raise rpclib.RPCUnsuccessfulReply(GARBAGE_ARGS)

        cred = cred.body
        if cred.service ==  rpc_gss_svc_none or \
           cred.gss_proc in (RPCSEC_GSS_INIT, RPCSEC_GSS_CONTINUE_INIT):
            return data
        p = GSSUnpacker(data)
        context = self._get_context(cred.handle)
        try:
            if cred.service == rpc_gss_svc_integrity:
                # data = opaque[gss_seq_num+data] + opaque[checksum]
                try:
                    data = p.unpack_opaque()
                    checksum = p.unpack_opaque()
                    p.done()
                except:
                    log_gss.exception("unsecure_data - initial unpacking")
                    raise rpclib.RPCUnsuccessfulReply(GARBAGE_ARGS)
                qop = context.verifyMIC(data, checksum)
                check_gssapi(qop)
                data = pull_seqnum(data)
            elif cred.service == rpc_gss_svc_privacy:
                # data = opaque[wrap([gss_seq_num+data])]
                try:
                    data = p.unpack_opaque()
                    p.done()
                except:
                    log_gss.exception("unsecure_data - initial unpacking")
                    raise rpclib.RPCUnsuccessfulReply(GARBAGE_ARGS)
                # data, qop, conf = context.unwrap(data)
                data, qop = context.unwrap(data)
                check_gssapi(qop)
                data = pull_seqnum(data)
            else:
                # Can't get here, but doesn't hurt
                log_gss.error("Unknown service %i for RPCSEC_GSS" % cred.service)
        except gssapi.Error, e:
            log_gss.warn("unsecure_data: gssapi call returned %s" % e.name)
            raise rpclib.RPCUnsuccessfulReply(GARBAGE_ARGS)
        return data

    def secure_data(self, cred, data):
        log_gss.debug("secure_data(%r)" % cred)
        cred = cred.body
        if cred.service ==  rpc_gss_svc_none or \
           cred.gss_proc in (RPCSEC_GSS_INIT, RPCSEC_GSS_CONTINUE_INIT):
            return data
        p = Packer()
        context = self._get_context(cred.handle)
        try:
            if cred.service == rpc_gss_svc_integrity:
                # data = opaque[gss_seq_num+data] + opaque[checksum]
                p.pack_uint(cred.seq_num)
                data = p.get_buffer() + data
                token = context.getMIC(data) # XXX BUG set qop
                p.reset()
                p.pack_opaque(data)
                p.pack_opaque(token)
                data = p.get_buffer()
            elif cred.service == rpc_gss_svc_privacy:
                # data = opaque[wrap([gss_seq_num+data])]
                p.pack_uint(cred.seq_num)
                data = p.get_buffer() + data
                token = context.wrap(data) # XXX BUG set qop
                p.reset()
                p.pack_opaque(token)
                data = p.get_buffer()
            else:
                # Can't get here, but doesn't hurt
                log_gss.error("Unknown service %i for RPCSEC_GSS" % cred.service)
        except gssapi.Error, e:
            # XXX What now?
            log_gss.warn("secure_data: gssapi call returned %s" % e.name)
            raise
        return data

    def partially_packed_header(self, xid, body):
        p = RPCPacker()
        p.pack_uint(xid)
        p.pack_enum(CALL)
        p.pack_uint(body.rpcvers)
        p.pack_uint(body.prog)
        p.pack_uint(body.vers)
        p.pack_uint(body.proc)
        cred = opaque_auth(RPCSEC_GSS, self.pack_cred(body.cred.body))
        p.pack_opaque_auth(cred)
        return p.get_buffer()

    def make_call_verf(self, xid, body):
        if body.cred.body.gss_proc in (RPCSEC_GSS_INIT, RPCSEC_GSS_CONTINUE_INIT):
            return rpclib.NULL_CRED
        else:
            data = self.partially_packed_header(xid, body)
            # XXX how handle gssapi.Error?
            token = self._get_context(body.cred.body.handle).getMIC(data)
            return opaque_auth(RPCSEC_GSS, token)

    def check_call_verf(self, xid, body):
        if body.cred.body.gss_proc in (RPCSEC_GSS_INIT, RPCSEC_GSS_CONTINUE_INIT):
            return self.is_NULL(body.verf)
        else:
            if body.verf.flavor != RPCSEC_GSS:
                return False
            data = self.partially_packed_header(xid, body)
            try:
                qop = self._get_context(body.cred.body.handle).verifyMIC(data, body.verf.body)
            except gssapi.Error, e:
                log_gss.warn("Verifier checksum failed verification with %s" %
                             e.name)
                return False
            body.cred.body.qop = qop # XXX Where store this?
            log_gss.debug("verifier checks out (qop=%i)" % qop)
            return True

    def check_auth(self, msg, data):
        """
        msg should be a CALL header
        """
        def auth_error(code):
            """Return (MSG_DENIED, AUTH_ERROR, code)"""
            raise rpclib.RPCDeniedReply(AUTH_ERROR, code)

        log_gss.debug("check_auth called with %r" % msg)
        # Check that cred and verf had no XDR errors
        if getattr(msg.cred, "opaque", True):
            log_gss.warn("XDR problem unpacking cred")
            log_gss.info("DENYing msg with AUTH_BADCRED")
            auth_error(AUTH_BADCRED)
        cred = msg.cred.body
        # Check gss version
        if cred.vers != RPCSEC_GSS_VERS_1:
            auth_error(AUTH_BADCRED)
        # Call handler for gss_proc if needed
        if cred.gss_proc != RPCSEC_GSS_DATA:
            if msg.proc != 0:
                auth_error(AUTH_BADCRED)
            # NOTE this will not return, instead raises an RPCFlowControl
            getattr(self, "handle_gss_proc_%i" % cred.gss_proc)(msg.cred, data)
        # Check service is permitted
        # STUB
        # Check handle
        context = self._get_context(cred.handle)
        if context is None:
            auth_error(RPCSEC_GSS_CREDPROBLEM)
        if context.expired():
            auth_error(RPCSEC_GSS_CTXPROBLEM)
        # Check header checksum
        if not self.check_call_verf(msg.xid, msg.cbody):
            auth_error(RPCSEC_GSS_CREDPROBLEM)
        # Check cred seq_num
        if cred.seq_num >= MAXSEQ:
            # RFC 2203 Sect 5.3.3.3 para 4
            auth_error(RPCSEC_GSS_CTXPROBLEM)
        context.check_seqid(cred.seq_num)
        return CredInfo(self, cred.handle, service=cred.service,
                        gss_proc=cred.gss_proc, qop=0)

    def handle_gss_proc_1(self, cred, data):
        """INIT"""
        log_gss.info("Handling RPCSEC_GSS_INIT")
        self.handle_gss_init(cred, data, first=True)

    def handle_gss_proc_2(self, cred, data):
        """CONTINUE_INIT"""
        log_gss.info("Handling RPCSEC_GSS_CONTINUE_INIT")
        # STUB - think through this more carefully
        self.handle_gss_init(cred, data, first=False)

    def handle_gss_init(self, cred, data, first):
        p = GSSUnpacker(data)
        token = p.unpack_opaque()
        p.done()
        log_gss.debug("***ACCEPTSECCONTEXT***")
        if first:
            context = gssapi.Context()
        else:
            context = self._get_context(cred.body.handle)
        try:
            token = context.accept(token)
        except gssapi.Error, e:
            log_gss.debug("RPCSEC_GSS_INIT failed (%s, %i)!" %
                          (e.name, e.minor))
            res = rpc_gss_init_res('', e.major, e.minor, 0, '')
        else:
            log_gss.debug("RPCSEC_GSS_*INIT succeeded!")
            if first:
                handle = self._add_context(context)
                # XXX HACK - this ensures make_reply_verf works, but
                # is a subtle side-effect that could introduce bugs if code
                # is ever reorganized.  Currently cred is forgotten once
                # we leave here though.
                cred.body.rpc_gss_cred_vers_1_t.handle = handle
            else:
                handle = cred.body.handle
            if context.open:
                major = gssapi.GSS_S_COMPLETE
            else:
                major = gssapi.GSS_S_CONTINUE_NEEDED
            res = rpc_gss_init_res(handle, major, 0, # XXX can't see minor
                                   WINDOWSIZE, token)
        # Prepare response
        p = GSSPacker()
        p.pack_rpc_gss_init_res(res)
        # NOTE this is an annoying case for make_reply_verf.
        # It is the only time that you need msg_data to feed into it.
        verf = self.make_reply_verf(cred, major)
        raise rpclib.RPCSuccessfulReply(verf, p.get_buffer())

    def make_reply_verf(self, cred, stat):
        log_gss.debug("CALL:make_reply_verf(%r, %i)" % (cred, stat))
        cred = cred.body
        if stat:
            # Return trivial verf on error
            # NOTE this relies on GSS_S_COMPLETE == rpc.SUCCESS == 0
            return rpclib.NULL_CRED
        elif cred.gss_proc in (RPCSEC_GSS_INIT, RPCSEC_GSS_CONTINUE_INIT):
            # init requires getMIC(seq_window)
            i = WINDOWSIZE
        else:
            # Else return getMIC(cred.seq_num)
            i = cred.seq_num
        p = Packer()
        p.pack_uint(i)
        # XXX BUG - need to set qop
        token = self._get_context(cred.handle).getMIC(p.get_buffer())
        return opaque_auth(RPCSEC_GSS, token)

    def check_reply_verf(self, msg, call_cred, data):
        if msg.stat != MSG_ACCEPTED:
            return
        verf = msg.rbody.areply.verf
        if msg.rbody.areply.reply_data.stat != SUCCESS:
            if not self.is_NULL(verf):
                raise SecError("Bad reply verifier - expected NULL verifier")
        elif call_cred.body.gss_proc in (RPCSEC_GSS_INIT, RPCSEC_GSS_CONTINUE_INIT):
            # The painful case - we need to check against reply data
            p = GSSUnpacker(data)
            try:
                res = p.unpack_rpc_gss_init_res()
                p.done()
            except:
                log_gss.warn("Failure unpacking gss_init_res")
                raise SecError("Failure unpacking gss_init_res")
            if self.is_NULL(verf):
                if res.gss_major == GSS_S_COMPLETE:
                    raise SecError("Expected seq_window, got NULL")
            else:
                if res.gss_major != GSS_S_COMPLETE:
                    raise SecError("Expected NULL")
                # BUG - context establishment is not finished on client
                # - so how get context?  How run verifyMIC?
                # - This seems to be a protocol problem.  Just ignore for now
        else:
            p = Packer()
            p.pack_uint(call_cred.body.seq_num)
            qop = call_cred.context.verifyMIC(p.get_buffer(), verf.body)
            if qop != call_cred.body.qop:
                raise SecError("Mismatched qop")

##############################################

supported = {AUTH_NONE:  AuthNone,
             AUTH_SYS:   AuthSys,
             }

if gssapi is not None:
    supported[RPCSEC_GSS] = AuthGss

def klass(flavor):
    """Importers should only refer to the classes via flavor.

    They get the actual clas via this function.
    """
    return supported[flavor]

def instances():
    out = {}
    for flavor, auth in supported.items():
        out[flavor] = auth()
    return out

def instance(flavor, *args, **kwargs):
    return klass(flavor)(*args, **kwargs)
