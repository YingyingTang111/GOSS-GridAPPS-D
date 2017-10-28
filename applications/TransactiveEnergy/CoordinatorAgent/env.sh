#!/bin/sh

export GAMS_PYTHON_API="/opt/gams/gams24.9_linux_x64_64_sfx"

if test "x$LD_LIBRARY_PATH" = x
then
    export LD_LIBRARY_PATH="$GAMS_PYTHON_API"
else
    export LD_LIBRARY_PATH="$GAMS_PYTHON_API:$LD_LIBRARY_PATH"
fi