#!/bin/bash

docker run \
    -it \
    -w /srv \
    -p 4001:4000 \
    -v `pwd`:/srv ruby:latest \
    /bin/bash
