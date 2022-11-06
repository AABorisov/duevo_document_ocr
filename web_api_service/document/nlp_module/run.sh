#!/bin/bash

docker rm -f dueva-utm-doc

docker rmi dueva-utm-doc-img:latest

docker build . -t dueva-utm-doc-img:latest

docker run -d --name dueva-utm-doc -v /home/neurus/storage:/storage dueva-utm-doc-img:latest
