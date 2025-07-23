#!/bin/bash

mkdir -p data/{empiar,epfl,hemibrain,idr,openorganelle} reference_metadata
docker build -t image_harvest .
