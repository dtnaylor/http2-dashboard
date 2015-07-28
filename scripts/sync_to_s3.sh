#!/bin/bash

rm -r ../www/_site/data
aws s3 sync ../www/_site/ s3://isthewebhttp2yet.com

# --exclude doesn't seem to be working
# aws s3 sync ../www/_site/ s3://isthewebhttp2yet.com --exclude "../www/_site/data/*"
