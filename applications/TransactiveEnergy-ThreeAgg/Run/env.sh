#!/bin/sh

[ -d "/opt/gams/gams24.9_linux_x64_64_sfx" ] && echo "Directory of gams exists." || export PATH=$PATH:/opt/gams/gams24.3_linux_x64_64_sfx && echo "Added PATH for gams"

export GAMS_INSTALL="/opt/gams/gams24.9_linux_x64_64_sfx"
export LD_LIBRARY_PATH=$GAMS_INSTALL:$LD_LIBRARY_PATH
echo "Added LD_LIBRARY_PATH for gams"


export PYTHONPATH="/opt/gams/gams24.9_linux_x64_64_sfx/apifiles/Python/api"
echo "Added PYTHONPATH for gams PYTHON api"