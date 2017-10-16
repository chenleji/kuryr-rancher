build:
	docker build -t registry.cn-hangzhou.aliyuncs.com/wise2c/kuryr-rancher:latest -f controller.Dockerfile .
push:
	docker push registry.cn-hangzhou.aliyuncs.com/wise2c/kuryr-rancher:latest
all:
	build push

