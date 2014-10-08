#!/usr/bin/python
import sys,getopt,threading
from subprocess import call
import gluster_setup,os,time,check_tests,counter
from print_results import print_results
from check_setup import check_setup
from usage import usage
import header
from mount import mount

server_ip=""
client_ip=""
lfile=""
cleanup=""
confile=""
fs=""
total=11
nfs4_total=0
nfs3_total=0
known_failures=13
version=""
test_list=list()


argv=sys.argv[1:]
try:
        opts, args = getopt.getopt(argv,"hl:ns:v:t:f:b:e:",["nocleanup"])
except getopt.GetoptError:
        print 'main.py -s <SERVER-HOST-IP> -e <EXPORT> -b <BACK-END-FILE-SYSTEM> -f <CONFIG_FILE> -l [LOG_FILE] -t [TESTS] -v [NFS_VERSION][-n|--nocleanup]'
        sys.exit(2)
for opt, arg in opts:
        if opt == '-h':
                print 'main.py -i <logfile> -n|--nocleanup'
                sys.exit()
        elif  opt in ("-n", "--nocleanup"):
                cleanup =  "yes"
                print "Tests to be run in no cleanup mode"
        elif opt == '-l':
                lfile = arg
        elif opt == '-s':
                server_ip = arg
	elif opt == '-f':
		confile = arg
        elif opt == '-t':
		test_list.append(arg)
        elif opt == '-v':
                version = arg
	elif opt == '-b':
		fs = arg
	elif opt == '-e':
		export = arg
		


class  Logger(object):
        def __init__(self):
                self.terminal = sys.stdout
                self.log = open(lfile, "a")
        def write(self, message):
                self.terminal.write(message)
                self.log.write(message)




class myThread (threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		#self.test = test
	def run(self):
		os.system(self.name)

usage(server_ip)
usage(confile)
usage(fs)
usage(export)
check_setup(fs)

if lfile == "":
	lfile="/tmp/ganesha.log"
	if os.path.isfile(lfile) == True :
		os.remove(lfile)

sys.stdout = Logger()
header.header_1(lfile)

test_list = check_tests.check_list(test_list, version);

if not test_list:
        print "Nothing to be tested."
        sys.exit(0)


original = os.getcwd()
#gluster_setup.setup(export,server_ip,client_ip,confile)

def run_tests(list):
#        os.chdir("./test-dir")
        for test in list:
	        if test == "pynfs_tests.py":
		        thread1 = myThread("python %s %s %s %d %s " %('test-dir/'+test,server_ip,export,known_failures,lfile))
	        else:
		        thread1 = myThread("python %s %s %s " %('test-dir/'+test,lfile,server_ip))
                thread1.start()
                thread1.join()


if (version == "4" or version==""):
        call('umount /mnt/ganesha-mnt',shell=True)
        mount(export,server_ip,"4")
        if os.path.ismount('/mnt/ganesha-mnt') == False:
                if version == "4":
                        print "v4 mount failed,exiting."
                        sys.exit(1)
                else:
                        print "v4 mount failed, skipping v4 tests"
        else:
                nfs4_total = len(test_list)
                print "==============================Running v4 tests=============================="
                counter.reset();
                run_tests(test_list)
                print_results(nfs4_total);
if (version == "3" or version==""):
        call('umount /mnt/ganesha-mnt',shell=True)
        mount(export,server_ip,"3")
        if os.path.ismount('/mnt/ganesha-mnt') == False:
                print "v3 mount failed,exiting."
                sys.exit(1)
        if "pynfs_tests.py" in test_list:
                test_list.remove("pynfs_tests.py")
        nfs3_total = len(test_list)
        print "==============================Running v3 tests=============================="
        counter.reset();
        run_tests(test_list)
        print_results(nfs3_total);



#passed=counter(0)
os.chdir(original)
os.environ['server_ip']=server_ip
if cleanup == "":
	gluster_setup.clean()
#	os.system('ssh -t $server_ip "yes | /tmp/copy-to-server/cleanup.sh" ')

os.system('rm -rf /tmp/counter.txt')

#failed = total - passed

#print ""
#print "==============================Results===================================="
#print " Total tests run : %d  " %total
#print " Tests passed    : %d  " %passed
#print " Tests failed    : %d  " %failed
#print "========================================================================="


