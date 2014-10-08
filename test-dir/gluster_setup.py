#!/usr/bin/python
import subprocess,os,sys,time
from subprocess import call


original = sys.stdout


def setup(volume,server_ip,client_ip,confile):
	
	 os.environ['server_ip']=server_ip
	 os.environ['volume']=volume
	 os.environ['confile']=confile
	 os.environ['server_ip']=server_ip
	 #os.system('ssh -t $server_ip "/root/copy-to-server/run1.sh $volume $server_ip $confile" ')
         os.environ['client_ip'] = client_ip
	 if volume == "ganesha-test-volume" :
		call('scp -r copy-to-server $server_ip:/tmp/',shell=True)
		os.system('ssh -t $server_ip "/tmp/copy-to-server/run1.sh $volume $server_ip $confile" ')
		#if os.path.isdir('/mnt/ganesha-mnt')==False:
			#os.mkdir('/mnt/ganesha-mnt')
		#print "=================Mount ganesha-test-volume on the client==============="
         	#os.system('mount -t nfs -o vers=4 $server_ip:/ganesha-test-volume  /mnt/ganesha-mnt')
	 else:	
		#if os.path.isdir('/mnt/pynfs-mnt')==False:
			#os.mkdir('/mnt/pynfs-mnt')
		os.system('ssh -t $server_ip "/tmp/copy-to-server/run1.sh $volume $server_ip $confile" ')
		#print "=================Mount pynfs-test-volume on the client=================="
		#os.system('mount -t nfs -o vers=4 $server_ip:/pynfs-test-volume  /mnt/pynfs-mnt')
		#time.sleep(1)

def clean():
	
        call("umount /mnt/ganesha-mnt",shell=True)
        call("umount /mnt/pynfs-mnt",shell=True)
	call("rm -rf /tmp/brick98; rm -rf /tmp/brick99;rm -rf /mnt/ganesha-mnt",shell=True)
        call("rm -rf /tmp/brick90; rm -rf /tmp/brick91;rm -rf /mnt/pynfs-mnt",shell=True)
	call("rm -rf /tmp/working-scripts ;rm -rf /tmp/copy.sh",shell=True)

