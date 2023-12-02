# Шпаргалка для работы с GitLab CI

## **Pipeline Archit­ecture**

### **Global Defaults**

| default   | after_script  artifacts  before_script  cache  image  interruptible  retry  services  tags  timeout |
| --- | --- |
| variables | Нельзя указать, но можно указать на глобальном уровне |

Значения `jobs` всегда переопределяют global defaults.

Пример:

```yaml
default:
  image: python:3.8
  retry: 1
  tags: [test]

variables:
	FOO: barу
```

### **Include**

[https://docs.gitlab.com/ee/ci/yaml/includes.html](https://docs.gitlab.com/ee/ci/yaml/includes.html)

```yaml
include:
	# Напрямую ссылку на файл (URL)
  - remote: 'https://gitlab.com/awesome-project/raw/master/.before-script-template.yml'
  # Файл в репозитории
  - local: '/templates/.after-script-template.yml'
  # Шаблон с GitLab сервера
  - template: Auto-DevOps.gitlab-ci.yml
  # Ссылка на конкретный файл в другом репозитории GitLab
  - project: 'my-group/my-project'
    ref: master
    file: '/templates/.gitlab-ci-template.yml'
```

### **Before and After Scripts**

```yaml
default:
  before_script:
    - echo "global before script"

job:
  before_script:
    - echo "execute this instead of global version"
  script:
    - echo "my command"
  after_script:
    - echo "execute this after my script"
```

### **Extends**

[https://docs.gitlab.com/ee/ci/yaml/yaml_optimization.html#use-extends-to-reuse-configuration-sections](https://docs.gitlab.com/ee/ci/yaml/yaml_optimization.html#use-extends-to-reuse-configuration-sections)

```yaml
# Запускать только для веток main и stable на раннерах с тегом production
.only-important:
  only:
    - main
    - stable
  tags:
    - production
# Запускать в докере image alpine на раннерах с тегом docker
.in-docker:
  tags: [docker]
  image: alpine
# Сочетаем настройки двух extends
# В итоге получаем: запуск веток main и stable в докере image alpine 
#   на раннерах с тегом docker
rspec:
  extends:
    - .only-important
    - .in-docker
  script:
    - rake rspec
# Docker extends: Запускать в докере image alpine на раннерах с тегом docker
spinach:
  extends: .in-docker
  script: rake spinach
```

### YAML Anchors

[https://yaml.org/spec/1.2.2/#3222-anchors-and-aliases](https://yaml.org/spec/1.2.2/#3222-anchors-and-aliases)

```yaml
# Extends для всех Python задач
.python:
  image: python
  tags: [python]
	before_script: &beforeScript
    - echo "command 0"
    - pip install -r requirements.txt
    - echo "command 1"
# Build (просто запуск extends)
build:
  extends: .python
# test extends, который включает дополнительный шаг установки еще набора зависимостей
# но основные зависимости тоже надо ставить
.test:
	before_script:
    - *beforeScript
		- pip install -r requirements-test.txt
# Tests
test1:
	extends: .test
	script: echo "test1"
test2:
	extends: .test
	script: echo "test2"
```

## **Jobs Management**

### Stages

```yaml
# .pre and .post stages are guaranteed to be 
# the first (.pre) or last (.post) stage in a pipeline
stages:
  - .pre
  - build
  - test
  - deploy
  - .post
```

### **Disabling Jobs by Hiding Them**

```yaml
# Точка вначале (по аналогии с файловыми системами) временно выключает Job
# (иными словами делает его невидимым для GitLab CI)
.hidden_job:
  script:
    - run test
```

### Variables

[https://docs.gitlab.com/ee/ci/variables/](https://docs.gitlab.com/ee/ci/variables/)

```yaml
variables:
  # Значение по умолчанию
  ENVIRONMENT: "staging"
  DB_URL: "postgres://postgres@postgres/db

build:
  script: mvn build
  variables:
		# Мы переопределяем значение на уровне Job
    ENVIRONMENT: "production"
```

### **Enviro­nment**

[https://docs.gitlab.com/ee/ci/environments/](https://docs.gitlab.com/ee/ci/environments/)

```yaml
# Разворачиваем приложение в окружение с названием review (часто используется
# для проверки кода на реальном окружении во время тестирования)
# При нажатии кнопки Stop для этого окружения - запустить задачу stop_review_app
review_app:
  stage: deploy
  script: make deploy-app
  environment:
    name: review
    on_stop: stop_review_app
# stop_review_app для удаления окружения (action - stop)
stop_review_app:
  stage: deploy
  variables:
    GIT_STRATEGY: none
  script: make delete-app
  when: manual
  environment:
    name: review
    action: stop
# Развернуть приложение в окружение с именем и URL основанном 
# на переменных GitLab
deploy as review app:
  stage: deploy
  script: make deploy
  environment:
    name: review/$CI_COMMIT_REF_NAME
    url: https://$CI_ENVIRONMENT_SLUG.example.com/
```

### Services

[https://docs.gitlab.com/ee/ci/services/](https://docs.gitlab.com/ee/ci/services/)

```yaml
services:
  - name: postgres:9.4
    alias: db
    entrypoint: ["docker-entrypoint.sh"]
    command: ["postgres"]
```

### Pages

[https://docs.gitlab.com/ee/user/project/pages/](https://docs.gitlab.com/ee/user/project/pages/)

```yaml
pages:
  stage: deploy
  script:
    - mkdir .public
    - cp -r * .public
    - mv .public public
  artifacts:
    paths:
      - public
  only:
    - master
```

### **Depend­encies**

> По умолчанию все артефакты от всех предыдущих стадий автоматически передаются в текущую задачу, но вы можете указать явно, от каких задач Вам нужно получать артефакты.
> 

[https://docs.gitlab.com/ee/ci/yaml/#dependencies](https://docs.gitlab.com/ee/ci/yaml/#dependencies)

```yaml
build:osx:
  stage: build
  script: make build:osx
  artifacts:
    paths:
      - binaries/

build:linux:
  stage: build
  script: make build:linux
  artifacts:
    paths:
      - binaries/

test:osx:
  stage: test
  script: make test:osx
  dependencies:
    - build:osx

test:linux:
  stage: test
  script: make test:linux
  dependencies:
    - build:linux

deploy:
  stage: deploy
  script: make deploy
```

### **Needs**

> По умолчанию все задачи выполняются в соответствии с очередностью описания стадий в `stages` списке. `Needs` позволяет при необходимости изменить этот порядок и запустить какую-то задачу сразу после выполнения задачи, которые ей нужны.
> 

[https://docs.gitlab.com/ee/ci/yaml/#needs](https://docs.gitlab.com/ee/ci/yaml/#needs)

```yaml
stages:
  - build
  - test
  - deploy

linux:build:
  stage: build

mac:build:
  stage: build

linux:rspec:
  stage: test
  needs: ["linux:build"]

linux:rubocop:
  stage: test
  needs: ["linux:build"]

mac:rspec:
  stage: test
  needs: ["mac:build"]

mac:rubocop:
  stage: test
  needs: ["mac:build"]

production:
  stage: deploy
```

### Tags

[https://docs.gitlab.com/ee/ci/yaml/#tags](https://docs.gitlab.com/ee/ci/yaml/#tags)

```yaml
job:
  tags:
    - ruby
    - postgres

osx job:
  stage:
    - build
  tags:
    - osx
  script:
    - echo "Hello, $USER!"
```

### Parallel

[https://docs.gitlab.com/ee/ci/yaml/#parallel](https://docs.gitlab.com/ee/ci/yaml/#parallel)

```yaml
deploystacks:
  script:
    - echo "Executing $STACK on $PROVIDER"
  parallel:
    matrix:
      - PROVIDER: aws
        STACK:
          - monitoring
          - app1
          - app2
      - PROVIDER: ovh
        STACK: [monitoring, backup, app]
      - PROVIDER: [gcp, vultr]
        STACK: [data, processing]
```

## Flow control

### Rules

[https://docs.gitlab.com/ee/ci/yaml/#rules](https://docs.gitlab.com/ee/ci/yaml/#rules)

```yaml
docker build:
  script: docker build -t my-image:$SLUG .
  rules:
    # Мы будем запускать джобу вручную если будут изменения в Dockerfile
    - changes:
      - Dockerfile
      when: manual
    # Мы будем запускать джобу вручную если переменная $VAR равна значению
    - if: '$VAR == "string value"'
      when: manual 
    # В иных случаях мы будем запускать автоматически задачу если все задачи
    # выше завершились успехом
    - when: on_success

docker build:
  script: docker build -t my-image:$SLUG .
  rules:
    # Мы будем запускать джобу вручную если будут изменения в Dockerfile\Docker
    # и переменная $VAR равна значению
    - if: '$VAR == "string value"'
      changes:
      - Dockerfile
      - docker/scripts/*
      when: manual
    # А также автоматически если какая-то задача выше закончилась неуспешно
    - when: on_failure
```

### Retries

[https://docs.gitlab.com/ee/ci/yaml/#retry](https://docs.gitlab.com/ee/ci/yaml/#retry)

```yaml
test:
  script: rspec
	# Запускаем два раза (максимально в GitLab) повтор запуска задачи
  # если у нас возникли неполадки с runner (ошибка или timeout)
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure
```

### **Interr­uptible**

[https://docs.gitlab.com/ee/ci/yaml/#interruptible](https://docs.gitlab.com/ee/ci/yaml/#interruptible)

```yaml
stages:
  - stage1
  - stage2

step-1:
  stage: stage1
  script:
    - echo "Can be canceled"
  
step-2:
  stage: stage2
  script:
    - echo "Can not be canceled"
  interruptible: false
```

## Artifact and Cache management

### Artifacts

[https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html)

```yaml
job:
  # Сохранять артефакты с именем Job 
  artifacts:
    name: "$CI_JOB_NAME"
    # Включить туда:
    # - все файлы их папки binaries и файл (папку) .config
    paths:
      - binaries/
      - .config
    # - все файлы отсутствующие в коммите на этот билд
    untracked: true
    # Мы сохраняем артефакты только в случае ошибки джобы
    when: on_failure
    # И говорим что нам неинтересны они после 1 недели (можно удалять)
    expire_in: 1 week

code_quality:
  stage: test
  script: codequality /code
  artifacts:
    # Мы сохраняем в качестве артефакта отчет от систем тестирования
    reports:
      codequality: gl-code-quality-report.json
  # И извлекаем из лога выполнения тестов строку чтобы записать в отчет 
  # покрытие кода тестами (в % обычно)
  coverage: '/Code coverage: \d+\.\d+/'
```

### Cache

[https://docs.gitlab.com/ee/ci/caching/#cache](https://docs.gitlab.com/ee/ci/caching/#cache)

```yaml
build:
  script: mvn test
  cache:
    key: build
    untracked: true
    paths:
      - binaries/
    policy: pull
```

## Pipelines samples

### Docker build

```yaml
Build:Docker:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:debug
    entrypoint: [""]
  script:
    - mkdir -p /kaniko/.docker
    - echo "{\"auths\":{\"${CI_REGISTRY}\":{\"auth\":\"$(printf "%s:%s" "${CI_REGISTRY_USER}" "${CI_REGISTRY_PASSWORD}" | base64 | tr -d '\n')\"}}}" > /kaniko/.docker/config.json
    - /kaniko/executor --context "${CI_PROJECT_DIR}" --destination "${CI_REGISTRY_IMAGE}:${IMAGE_TAG}"
```

### Tags creation

```yaml
Release:Tag:
  stage: release
  image: registry.gitlab.com/juhani/go-semrel-gitlab:v0.21.1
  script: release --bump-patch tag
  rules:
    # We run release creation from main branch only
    - if: '$CI_COMMIT_BRANCH == "main"'
```

### Generate child pipeline and include it

```yaml
generate-config:
  stage: build
  script: generate-ci-config > generated-config.yml
  artifacts:
    paths:
      - generated-config.yml

child-pipeline:
  stage: test
  trigger:
    include:
      - artifact: generated-config.yml
        job: generate-config
```

#### Основано на https://cheatography.com/violaken/cheat-sheets/gitlab-ci-cd-pipeline-configuration/