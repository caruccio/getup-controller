VERSION := v0.0.1
REPOSITORY := getupcloud
IMAGE_NAME := getup-controller
GIT_COMMIT := $(shell git log -n1 --oneline)
GIT_COMMIT_ID := $(shell git log -n 1 --pretty=format:%h)
BUILD_DATE := $(shell LC_ALL=C date -u)
COMPILE := true

.PHONY: default
default: image

.PHONY: release
release: check-dirty image tag-latest push push-latest

.PHONY: image
image:
	docker build . -t $(REPOSITORY)/$(IMAGE_NAME):$(VERSION) \
        --build-arg VERSION="$(VERSION)" \
        --build-arg BUILD_DATE="$(BUILD_DATE)" \
        --build-arg GIT_COMMIT="$(GIT_COMMIT)" \
        --build-arg GIT_COMMIT_ID="$(GIT_COMMIT_ID)" \
        --build-arg COMPILE="$(COMPILE)"

check-dirty: DIFF_STATUS := $(shell git diff --stat)
check-dirty:
	@if [ -n "$(DIFF_STATUS)" ]; then \
	  echo "--> Refusing to build release on a dirty tree"; \
	  echo "--> Commit and try again."; \
	  exit 2; \
	fi

.PHONY: push
push:
	docker push $(REPOSITORY)/$(IMAGE_NAME):$(VERSION)

.PHONY: tag-latest
tag-latest:
	docker tag $(REPOSITORY)/$(IMAGE_NAME):$(VERSION) $(REPOSITORY)/$(IMAGE_NAME):latest

.PHONY: push-latest
push-latest:
	docker push $(REPOSITORY)/$(IMAGE_NAME):latest

#####
# Project specific

.PHONY: dev
dev: VERSION := $(VERSION)-dev
dev: dev-image dev-run

.PHONY: dev-image
dev-image: VERSION := $(VERSION)-dev
dev-image: COMPILE := false
dev-image: image

.PHONY: run
dev-run: VERSION := $(VERSION)-dev
dev-run:
	docker run -it --rm --name $(IMAGE_NAME)-$(VERSION) $(REPOSITORY)/$(IMAGE_NAME):$(VERSION)
