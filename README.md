nfs-test-framework
==================
1. How to run the tests?
==========================
main.py -s <SERVER-HOST-IP> -e <EXPORT> -f <CONFIG_FILE> -l [LOG_FILE]-v [NFS_VERSION] -b <-t [TEST] [-n|--nocleanup]

Mandatory parameters:
======================
-s :  IP of the host on which ganesha server has to set up.
-e :  Name of the export entry that has to exported via ganesha and run all the tests against the export.
-f :  Absolute path to the config file that is required b nfs-ganesha.
-b :  back end file system that is being used.
A set up file with the name of the back end file system should be present in the directory.
The script cannot run without it.
For example, to run the scripts with gluster as the back end, a scrit with the name
gluster, a script called gluster setup.py should be present in the directory.


Optional parameters:
=====================
-l : Log file to log the results of the test suite.
Default location : /tmp/ganesha.log
-v : In which version should the export be mounted to perform the tests.
Defualt : All the ( appropriate) tests will be performed on both NFSv4 and NFSv3 mounts.
-t : Run a specific test.
Default : All the tests are run.
-n : The export will remain mounted and no clean up will be done.
Default : Export will be unmounted.


There are numerous tests run as part of this framework.
The log files if each of these tests are logged as separate files
in /export directory.



