#!/usr/local/bin/bash

set -e

. /usr/local/bin/entrypoint-functions.sh

mkdir -p /kaniko/.docker

hosts=(CI_REGISTRY ${!CI_REGISTRY_X_*})
users=(CI_REGISTRY_USER ${!CI_REGISTRY_USER_X_*})
passs=(CI_REGISTRY_PASSWORD ${!CI_REGISTRY_PASSWORD_X_*})
generate_auth_string $(riffle_indirect hosts users passs) > /kaniko/.docker/config.json

exec "$@"
