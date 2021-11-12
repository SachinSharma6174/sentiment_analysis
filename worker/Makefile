VERSION=v1
DOCKERUSER=sachinsharma6174

build:
	docker build -f Dockerfile-sentiment-worker -t sentiment-worker .
push:
	docker tag sentiment-worker $(DOCKERUSER)/sentiment-worker:$(VERSION)
	docker push $(DOCKERUSER)/sentiment-worker:$(VERSION)
	docker tag sentiment-worker $(DOCKERUSER)/sentiment-worker:latest
	docker push $(DOCKERUSER)/sentiment-worker:latest

