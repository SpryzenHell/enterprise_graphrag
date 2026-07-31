#!/bin/bash

args=$*

docker gragBuild ./src/gragAce/app -t gragAce-base:latest ${args} -f ./src/gragAce/app/base.Dockerfile


