#!/usr/bin/python
import os,time
def mount(export,server_ip,version):

         os.environ['server_ip']=server_ip
         os.environ['export']=export
         os.environ['version']=version
         if os.path.isdir('/mnt/ganesha-mnt')==False:
                        os.mkdir('/mnt/ganesha-mnt')
         print "=================Mount %s on the client in version %s===============" %(export,version)
         os.system('mount -t nfs -o vers=$version $server_ip:/$export  /mnt/ganesha-mnt')


