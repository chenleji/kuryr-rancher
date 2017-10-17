
build:
	docker build -t registry.cn-hangzhou.aliyuncs.com/wise2c/wise2c-flatnet-controller:latest -f controller.Dockerfile .

push:
	docker push registry.cn-hangzhou.aliyuncs.com/wise2c/wise2c-flatnet-controller:latest

all: build push
