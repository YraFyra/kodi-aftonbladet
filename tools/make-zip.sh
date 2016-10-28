#!/bin/bash

if [ -d plugin.video.aftonbladet ] ; then
    zip -r addon-aftonbladet.zip plugin.video.aftonbladet
else
    echo Must be executed in root of git
fi
