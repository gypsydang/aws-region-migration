#!/bin/bash

PROFILE=$1
[ "_$PROFILE" = "_" ] && PROFILE=default

aws --profile $PROFILE iam get-account-authorization-details --output json > iam_export.json
