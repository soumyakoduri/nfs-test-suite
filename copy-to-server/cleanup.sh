#!/bin/bash
yes | gluster volume stop ganesha-test-volume >/dev/null 2>/dev/null
yes | gluster volume delete ganesha-test-volume >/dev/null 2>/dev/null
yes | gluster volume stop pynfs-test-volume >/dev/null 2>/dev/null
yes | gluster volume delete pynfs-test-volume >/dev/null 2>/dev/null
rm -rf /tmp/brick9*
rm -rf /tmp/copy-to-server

