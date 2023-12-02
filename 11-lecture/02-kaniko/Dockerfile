FROM gcr.io/kaniko-project/executor:debug
SHELL ["/busybox/sh", "-c"]
ADD ./bash /usr/local/bin/bash
ADD ./*.sh /usr/local/bin/
ENTRYPOINT [ "docker-entrypoint.sh" ]

