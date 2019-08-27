FROM summerwind/whitebox-controller:latest AS base

FROM python:3.6-alpine

ARG VERSION
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_COMMIT_ID
ARG COMPILE=true

COPY --from=base /bin/whitebox-controller /bin/whitebox-controller
COPY app/ /app/

RUN pip install -r /app/requirements.txt

ENTRYPOINT ["/bin/whitebox-controller"]
