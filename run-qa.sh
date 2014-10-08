#/bin/bash
if [ ! -d "/export" ];
then
mkdir /export
fi

if ! mount | grep -q "/opt"
then
        mount -t nfs rhsqe-repo.lab.eng.blr.redhat.com:/opt /opt
        #time /opt/qa/tools/system_light/run.sh -w /mnt/nfsdir -l /export/sanity.log
fi

