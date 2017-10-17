
build:
	docker build -t registry.cn-hangzhou.aliyuncs.com/wise2c/wise2c-flatnet-controller:latest -f controller.Dockerfile .

push:
	docker push registry.cn-hangzhou.aliyuncs.com/wise2c/wise2c-flatnet-controller:latest

all: build push


release_build:
	docker build -t registry.cn-hangzhou.aliyuncs.com/wise2c/wise2c-flatnet-controller:v0.1.0 -f controller.Dockerfile .

release_push:
	docker push registry.cn-hangzhou.aliyuncs.com/wise2c/wise2c-flatnet-controller:v0.1.0

release: release_build release_push