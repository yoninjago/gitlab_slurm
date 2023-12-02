docker run -it --name gitlab-runner --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/config:/etc/gitlab-runner \
  gitlab/gitlab-runner:alpine3.14-v14.10.0 register
