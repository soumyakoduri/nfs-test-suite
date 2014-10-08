#!/bin/bash

        function write_conf()
{
        echo "EXPORT{"
        echo " Export_Id = 77 ;"
        echo "Path=\"/$1\";"
        echo "FSAL {"
        echo "name = "GLUSTER";"
        echo "hostname=\"$2\";"
        echo  "volume=\"$1\";"
        echo "}"
        echo "Access_type = RW;"
        echo "Allow_root_access = true;"
        echo "Pseudo=\"/$1\";"
        echo "NFS_Protocols = \"3,4\" ;"
        echo "Transport_Protocols = \"UDP,TCP\" ;"
        echo "SecType = \"sys\";"
        echo "Tag = \"$1\";"
        echo "}"
}
	
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib
        if ps aux | grep "[g]anesha.nfsd"
	then
	pkill ganesha.nfsd
        sleep 10
        fi
	if [ "$1" == "ganesha-test-volume" ]
	then
	mkdir /tmp/brick98
	mkdir /tmp/brick99
	gluster volume create $1 $2:/tmp/brick98 $2:/tmp/brick99 force
	else
	mkdir /tmp/brick96
	mkdir /tmp/brick97
        gluster volume create $1 $2:/tmp/brick96 $2:/tmp/brick97 force
	fi
	gluster volume start $1
	gluster volume set $1 nfs.disable ON
	#sed -i  s/volume.*/"volume=$1,hostname=$2\";"/ $3
        #sed -i s/Pseudo.*/Pseudo="\"\/$1\";"/ $3
        #sed -i s/Path.*/Path="\"\/$1\";"/ $3
        #sed -i 's/\r//g' $3
        write_conf $1 $2  > "/tmp/export_gluster.conf"
        sed -i /conf/d/  $3
        echo "%include \"/tmp/export_gluster.conf\"" >> $3
	/usr/local/bin/ganesha.nfsd -f $3  -L  ./nfs-ganesha.log -N NIV_FULL_DEBUG -d
	echo "Started ganesha"
	#exit 0
	
	#sleep 3
	#if ! ps aux | grep ganesha
	#then
	#echo "Couldn't start ganesha, exiting"
	#exit 1
	#fi
