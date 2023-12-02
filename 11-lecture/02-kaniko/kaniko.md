# Шаблон kaniko

## Введение

Данный шаблон автоматизирует сборку образов контейнеров с использованием [kaniko](https://github.com/GoogleContainerTools/kaniko).

## Применение

Добавьте в файл `.gitlab-ci.yml` (или иной файл, в котором определяются пайплайны, если дефолты переопределены) блок

```yaml
include:
- project: edu/ci-cd/cicd
  ref: master
  file: /08-lecture/02-kaniko/kaniko.yml
```

Чтобы создать в пайплайне задачу на сборку, опишите её следующим образом:

```yaml
include:
- project: edu/ci-cd/cicd
  ref: master
  file: /08-lecture/02-kaniko/kaniko.yml

stages:
- compile
- build
- deploy

Compile binary:
  stage: compile
  ...

Build docker image:            #  
  stage: build                 # Этих трёх строчек вполне достаточно для простых случаев  
  extends: .build_docker_image #  

Deploy to k8s:
  stage: deploy
  ...
```

Такой вариант использования, запущенный из репозитория `gitlab.slurm.io/group/repo` соберёт образ по `Dockerfile` расположенному в корне репозитория и сохранить его в репозитории образов под тегами `registry.slurm.io/group/repo:latest` и `registry.slurm.io/group/repo:xxxxxxx` где либо `xxxxxxx == ${CI_COMMIT_SHORT_SHA}`, либо `xxxxxxx == ${CI_COMMIT_TAG}` если у коммита задан тег. Фактически, это эквивалентно выполнению команд

```bash
docker build \
  -t ${CI_REGISTRY_IMAGE}:latest \
  -t ${CI_REGISTRY_IMAGE}:${CI_COMMIT_TAG:-${CI_COMMIT_SHORT_SHA}} \
  -f ./Dockerfile \
  ./
docker push ${CI_REGISTRY_IMAGE}:latest
docker push ${CI_REGISTRY_IMAGE}:${CI_COMMIT_TAG:-${CI_COMMIT_SHORT_SHA}}
```

## Кастомизация

Шаблон допускает кастомизацию следующими способами:

```yaml
...
Build docker image:
  stage: build
  extends: .build_docker_image
  variables:
    DOCKER_DOCKERFILE: ./docker/Dockerfile # См. полный перечень используемых переменных окружения ниже
  before_script:
  - echo "В этом блоке можно сделать некоторые подготовительные действия,"
  - echo "Например, можно выполнить sed и поправить некоторые конфигурационные"
  - echo "файлы, прежде чем сборка начнётся."
  rules:
  - changes:
    - ./docker/Dockerfile
    when: manual
```

Не следует задавать ключи `image`, `services`, `tags` и `script`. Они уже заданы в шаблоне на корректные значения.

### Переменные окружения

Детальная настройка работы сборщика осуществляется, преимущественно, заданием переменных окружения:

| Имя переменной | Значение по умолчанию | Функционал | Описание |
|----------------|-----------------------|------------|----------|
| `DOCKER_CONTEXT` | `./` | Определяет build-context | Путь, относительно корня репозитория, который будет корневым в контексте сборки образа. Контекст (т.е. все файлы, по этому пути, кроме тех, что заигнорены в `.dockerignore`) отправляется целиком в собираемый контейнер, хотя ему не всегда необходимо всё содержимое репозитория. |
| `DOCKER_DOCKERFILE` | `./Dockerfile` | Задаёт путь к докерфайлу | Можно переопределить, если докерфайлов несколько или если докерфайл по какой-то причине не в корне репозитория. |
| `DOCKER_REGISTRY_MIRROR` | `mirror.gcr.io` | Адрес зеркала для базовых образов из докерхаба | В большой компании скорее всего вы захотите поменять дефолт на уровне шаблона на что-то вроде `docker-proxy.bigcorp.ru`. |
| `DOCKER_REGISTRY_IMAGE` | `${CI_REGISTRY_IMAGE}` | Определяет путь, по которому сохраняется образ. | По умолчанию, это `registry.slurm.io/group/repo`, но это можно переопределить, если используется другое хранилище для образов. |
| `DOCKER_REGISTRY_SUBPATH` | Не задан | Добавляет "подпапку" к путю к образу | Если в одном репозитории собирается несколько разных образов, их можно разделить по именам. Например, для одного образа задать `DOCKER_REGISTRY_SUBPATH="/apiserver"`, а для другого `DOCKER_REGISTRY_SUBPATH="/tls-proxy"`. Тогда будут собираться образы с именами `registry.slurm.io/group/repo/apiserver` и `registry.slurm.io/group/repo/tls-proxy`. |
| `DOCKER_RELEASE_TAG` | `${CI_COMMIT_TAG:-${CI_COMMIT_SHORT_SHA}}` | Тег, проставляемый собранному образу. | По-умолчанию, равен тегу коммита, если таковой имеется, или сокращённому SHA коммита в ином случае. Если не задавать, запушится образ вида `registry.slurm.io/group/repo:fedbca0` или `registry.slurm.io/group/repo:tagname`. Если явно определить `DOCKER_RELEASE_TAG=mytag`, будет `registry.slurm.io/group/repo:mytag`. |
| `DOCKER_IMAGE_RELEASE` | `${DOCKER_REGISTRY_IMAGE}${DOCKER_REGISTRY_SUBPATH}:${DOCKER_RELEASE_TAG}` | Путь, куда будет пушиться образ. | Если явно задать значение `DOCKER_IMAGE_RELEASE=""`, образ не будет пушиться по пути по умолчанию. Если задать собственное значение, например `DOCKER_IMAGE_RELEASE="myregistry.example.com/username/myimage:tag"`, образ будет сохранён по этому пути, однако рекомендуется переопределять для этого переменные `DOCKER_REGISTRY_IMAGE`, `DOCKER_REGISTRY_SUBPATH` и `DOCKER_RELEASE_TAG`. |
| `DOCKER_IMAGE_LATEST` | `${DOCKER_REGISTRY_IMAGE}${DOCKER_REGISTRY_SUBPATH}:latest` | Ещё один путь, куда будет пушиться образ. | Если явно задать значение `DOCKER_IMAGE_LATEST=""`, образ не будет пушиться по пути по умолчанию. Если задать собственное значение, например `DOCKER_IMAGE_LATEST="myregistry.example.com/username/myimage:tag"`, образ будет сохранён по этому пути, однако рекомендуется переопределять для этого переменные `DOCKER_REGISTRY_IMAGE` и `DOCKER_REGISTRY_SUBPATH`. |
| `DOCKER_BUILD_ARG_*` | Не задан | Значения, передаваемые в kaniko в качестве `--build-arg`. | Пользователь может объявлять любые переменные с префиксом `DOCKER_BUILD_ARG_`. Например, если будут объявлены переменные `DOCKER_BUILD_ARG_1=var=myvalue` и `DOCKER_BUILD_ARG_RANDOMSTRING=baseimage`, kaniko будет запущен с дополнительными параметрами командной строки `--build-arg=var=myvalue --build-arg=baseimage`. |
| `DOCKER_PARAMS` | Динамически заполняется на основании предыдущих параметров | Параметры командной строки, которые передаются в сборщик. | Эта переменная наполняется такими значениями, как `--destination=${DOCKER_LATEST} --build-arg=${DOCKER_BUILD_ARG_XXX}` и так далее. Пользователь может заранее определить туда дополнительные аргументы, если это не получается настроить через имеющиеся переменные. |
