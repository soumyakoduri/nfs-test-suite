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
        echo "Squash = No_root_squash;"
        echo "Pseudo=\"/$1\";"
        echo "Protocols = \"3,4\" ;"
        echo "Transports = \"UDP,TCP\" ;"
        echo "SecType = \"sys\";"
        echo "Tag = \"$1\";"
        echo "}"
}

	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib
	if ps aux | grep -q "[g]anesha.nfsd"
	then
	kill -9 `cat /var/run/ganesha.pid`
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

	#sed -i s/volume.*/"volume=\"$1\";"/ $3

     	#sed -i s/Path*/Path="\"\/$1\";"/ $3
	#sed -i s/volume=/"volume=\"$1\";"/ $3
	 #sed -i /^[[:space:]]*volume/s/volume.*/volume="\"\"$1\";" / $3
# sed -i /^[[:space:]]*volume/s/volume.*/"volume=\"testvol\";"/  export_gluster.conf
	#sed -i /^[[:space:]]*volume/s/volume.*/volume="\"$1\";"/ $3

	#sed -i s/Path*/Path="\"\/$1\";"/ $3
	#sed -i s/Psedo*/Pseudo="\"\/$1\";"/ $3
	#sed -i s/Pseudo.*/Pseudo="\"\/$1\";"/ $3
        #sed -i s/Path.*/Path="\"\/$1\";"/ $3


	#sed -i /^[[:space:]]*\#/!s/hostname.*/"hostname=\"$2\";"/ $3

 	#sed -i 's/\r//g' $3
        write_conf $@ > /tmp/export_gluster.conf
        sed -i /conf/d  $3
        echo "%include \"/tmp/export_gluster.conf\"" >> $3

	/usr/local/bin/ganesha.nfsd -f $3  -L  ./nfs-ganesha.log -N NIV_NULL -d 
	sleep 3
