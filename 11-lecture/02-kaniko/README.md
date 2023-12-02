# Kaniko executor image

В этой директории собирается дополненный образ [kaniko](https://github.com/GoogleContainerTools/kaniko). В него добавляется статически-линкованный bash, который нужен для скриптов упрощающих авторизацию в первую очередь в registry гитлаба, но также и в любом другом репозитории образов контейнеров. Подробности в скриптах `docker-entrypoint.sh` и `entrypoint-functions.sh`.

При запуске пайплайнов с этим образом нужно вызвать команду `docker-entrypoint.sh`, которая на основе значений переменных окружения

```
CI_REGISTRY
CI_REGISTRY_USER
CI_REGISTRY_PASSWORD
```

а также на основе любых групп переменных вида

```
CI_REGISTRY_X_<что_угодно>
CI_REGISTRY_USER_X_<что_угодно>
CI_REGISTRY_PASSWORD_X_<что_угодно>
```

заполнит файл `/kaniko/.docker/config.json` правильным образом, например

```json
{"auths": {
    "registry.slurm.io":{"username":"s123456","password":"<содержимое CI_REGISTRY_PASSWORD>"},
    "otherregistry.example.com":{"username":"example_user","password":"s3cr3tpassw0rd"}
} }
```

Сборка образа осуществляется так (выполнять не нужно, образ уже загружен):

```bash
wget https://github.com/robxu9/bash-static/releases/download/5.0/bash-linux -O bash
chmod 755 bash
docker build -t registry.slurm.io/edu/ci-cd/cicd/kaniko:latest .
docker push registry.slurm.io/edu/ci-cd/cicd/kaniko:latest
```

[`./kaniko.yml`](./kaniko.yml) содержит шаблон для сборки докер-образа с помощью kaniko. Для наглядности примера он составлен таким образом, чтобы можно было заменить

```
include:
- local: /docker.yml
```

на

```yaml
include:
- project: edu/ci-cd/cicd
  ref: master
  file: /08-lecture/02-kaniko/kaniko.yml
```

и получить такой же результат, как раньше, но при этом сборка осущесвлялась бы с помощью kaniko.

В истории из лекции разработчики в компании Пети и Васи скорее всего имели бы в своих пайплайнах конструкцию вида

```yaml
include:
- project: shared/gitlab-templates
  file: /docker.yml
```

с содержимым вида [`../01-vasya-and-his-pipeline/docker.v2.yml`](../01-vasya-and-his-pipeline/docker.v2.yml). В этом сценарии репозиторий `shared/gitlab-templates` поддерживается платформенной командой. Когда безопасник Боря пришёл к Пете и предостерёг его от использования привилигерованных контейнеров, Петя, заменив старое содержимое `docker.yml` на содержимое `kaniko.yml` мог одномоментно перевести всех разработчиков с docker-in-docker на kaniko. Хотя нет гарантий, что смена шаблона ничего не сломает при любом сценарии, при его умелом изготовлении можно свести количество поломок к терпимому минимуму.

Документация по использованию шаблона `kaniko.yml` лежит [здесь](./kaniko.md).
