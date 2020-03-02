#!/bin/bash

docker run \
    -it \
    -w /srv \
    -p 4001:4000 \
    -v /Users/sasha/Github/python-serverside/docs:/srv ruby:latest \
    /bin/bash
