CONTAINER_RUNTIME = podman
REGISTRY = docker.io
DATE_TAG = $(shell date +%Y%m%d)
BRANCH_NAME = $(shell git rev-parse --abbrev-ref HEAD | tr '/' '-')

BACKEND_IMAGE = $(REGISTRY)/ttyrex/lesnouvelles.quebec-backend:$(DATE_TAG)-$(BRANCH_NAME)
FRONTEND_IMAGE = $(REGISTRY)/ttyrex/lesnouvelles.quebec-frontend:$(DATE_TAG)-$(BRANCH_NAME)
WORKER_FEEDMAKER_IMAGE = $(REGISTRY)/ttyrex/lesnouvelles.quebec-worker-feedmaker:$(DATE_TAG)-$(BRANCH_NAME)
WORKER_FEEDPARSER_IMAGE = $(REGISTRY)/ttyrex/lesnouvelles.quebec-worker-feedparser:$(DATE_TAG)-$(BRANCH_NAME)
WORKER_NER_IMAGE = $(REGISTRY)/ttyrex/lesnouvelles.quebec-worker-ner:$(DATE_TAG)-$(BRANCH_NAME)

BACKEND_DIR = backend
FRONTEND_DIR = frontend
WORKER_FEEDMAKER_DIR = worker-feedmaker
WORKER_FEEDPARSER_DIR = worker-feedparser
WORKER_NER_DIR = worker-ner

CONTAINER_BUILD = $(CONTAINER_RUNTIME) build --no-cache
CONTAINER_PUSH = $(CONTAINER_RUNTIME) push

.PHONY: all backend worker-feedmaker worker-feedparser worker-ner frontend clean push

all: backend worker-feedmaker worker-feedparser worker-ner frontend

backend:
	@echo "Building backend container image with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_BUILD) -t $(BACKEND_IMAGE) -f $(BACKEND_DIR)/Dockerfile .
	@echo "Pushing backend container image to $(REGISTRY)..."
	$(CONTAINER_PUSH) $(BACKEND_IMAGE)

worker-feedmaker:
	@echo "Building worker-feedmaker container image with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_BUILD) -t $(WORKER_FEEDMAKER_IMAGE) -f $(WORKER_FEEDMAKER_DIR)/Dockerfile .
	@echo "Pushing worker-feedmaker container image to $(REGISTRY)..."
	$(CONTAINER_PUSH) $(WORKER_FEEDMAKER_IMAGE)

worker-feedparser:
	@echo "Building worker-feedparser container image with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_BUILD) -t $(WORKER_FEEDPARSER_IMAGE) -f $(WORKER_FEEDPARSER_DIR)/Dockerfile .
	@echo "Pushing worker-feedparser container image to $(REGISTRY)..."
	$(CONTAINER_PUSH) $(WORKER_FEEDPARSER_IMAGE)

worker-ner:
	@echo "Building worker-ner container image with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_BUILD) -t $(WORKER_NER_IMAGE) -f $(WORKER_NER_DIR)/Dockerfile .
	@echo "Pushing worker-ner container image to $(REGISTRY)..."
	$(CONTAINER_PUSH) $(WORKER_NER_IMAGE)

frontend:
	@echo "Building frontend container image with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_BUILD) -t $(FRONTEND_IMAGE) -f $(FRONTEND_DIR)/Dockerfile .
	@echo "Pushing frontend container image to $(REGISTRY)..."
	$(CONTAINER_PUSH) $(FRONTEND_IMAGE)

clean:
	@echo "Removing all container images..."
	$(CONTAINER_RUNTIME) rmi $(BACKEND_IMAGE) $(FRONTEND_IMAGE) $(WORKER_FEEDMAKER_IMAGE) $(WORKER_FEEDPARSER_IMAGE) $(WORKER_NER_IMAGE)
