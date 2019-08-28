FROM summerwind/whitebox-controller:latest AS base

FROM python:3.6-alpine

ARG VERSION
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_COMMIT_ID
ARG COMPILE=true

COPY --from=base /bin/whitebox-controller /bin/whitebox-controller
COPY app /app
COPY config /config

RUN apk add jq --no-cache && \
    pip install -r /app/requirements.txt && \
    ( \
        echo "VERSION=\"$VERSION\""; \
        echo "BUILD_DATE=\"$BUILD_DATE\""; \
        echo "GIT_COMMIT=\"$GIT_COMMIT\""; \
        echo "GIT_COMMIT_ID=\"$GIT_COMMIT_ID\""; \
    ) > /app/.version

WORKDIR /app

ENTRYPOINT ["/app/entrypoint"]
