FROM python:3.9-slim AS build-env
COPY requirements.txt ./
RUN pip3 install --upgrade -r requirements.txt --disable-pip-version-check --target=/packages
COPY ./application /app/application
COPY *.py /app/

FROM gcr.io/distroless/python3
ENV PYTHONPATH=/packages
ARG FLASK_RUN_PORT=8000
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=application
ENV FLASK_RUN_PORT=${FLASK_RUN_PORT}
COPY --from=build-env /packages /packages
COPY --from=build-env /app /app
WORKDIR /app
CMD [ "/packages/bin/flask", "run" ]
