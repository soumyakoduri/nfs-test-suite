#/bin/bash

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






write_conf $@




