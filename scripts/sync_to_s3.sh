#!/bin/bash

aws s3 sync --exclude ../www/_site/data ../www/_site/ s3://isthewebhttp2yet.com
