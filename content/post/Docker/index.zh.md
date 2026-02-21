---
title: "Docker 学习笔记"
description: "从入门到实践：Docker 核心概念、镜像操作与常用命令详解"
date: 2026-02-02
slug: "docker-learning-notes"
image: "helena-hertz-wWZzXlDpMog-unsplash.jpg"
categories:
    - Documentation
tags:
    - Docker
    - DevOps
toc: true
---

## 1. Docker 简介

Docker 是一个开源的应用容器化平台，它允许开发者将应用及其所有依赖打包到一个可移植的容器中，从而实现应用的快速部署和运行。相比于传统的虚拟机，Docker 更加轻量、启动更快，并且保证了环境的一致性。

## 2. Docker 的核心概念

- **镜像 (Image)**：Docker 镜像是一个轻量级、可执行的软件包，包含运行某个应用所需的所有内容（代码、运行时、库、环境变量、配置文件）。可以将它理解为“类的定义”。
- **容器 (Container)**：Docker 容器是镜像的运行实例。它是一个隔离的运行环境，可以在其中运行应用。可以将它理解为“类的实例”。
- **仓库 (Registry)**：存储 Docker 镜像的地方。Docker Hub 是默认的公共仓库，也有私有仓库（如 Harbor、AWS ECR）。
- **Dockerfile**：一个文本文件，包含了一系列构建 Docker 镜像的指令（如 `FROM`, `RUN`, `COPY`, `CMD` 等）。

---

## 3. Docker 镜像操作详解

### 3.1 获取镜像 (`docker pull`)

**命令格式**:  `docker pull [选项] [Registry地址/]仓库名[:标签]`

- 默认地址是 Docker Hub。
- 不指定标签默认为 `latest`。

#### 示例
```bash
# 拉取 Ubuntu 18.04 官方镜像
sudo docker pull ubuntu:18.04
```

### 3.2 运行镜像 (`docker run`)

**命令格式**: `docker run [选项] 镜像 [命令] [参数...]`

**常用参数**:
- `-i`: 交互式操作 (Interactive)
- `-t`: 分配伪终端 (Terminal)
- `--rm`: 容器退出后自动删除
- `-d`: 后台运行 (Detached)
- `-p`: 端口映射 (如 `-p 8080:80`)
- `-v`: 挂载卷 (Volume)

#### 示例

**1. 基础启动 (交互式)**
```bash
# 启动 Ubuntu 并进入容器终端，退出后自动删除容器
sudo docker run -it --rm ubuntu:18.04 bash
```

**2.后台运行Web服务 (Nginx)**
```bash
# -d: 后台运行
# -p: 将宿主机 8080 端口映射到容器 80 端口
# --name: 给容器起个名字叫 my-web
sudo docker run -d -p 8080:80 --name my-web nginx
```

**3. 挂载数据卷 (持久化数据)**
```bash
# -v: 将宿主机的 /opt/data 目录挂载到容器的 /var/lib/mysql
# -e: 设置环境变量 (比如 MySQL 密码)
sudo docker run -d \
  -p 3306:3306 \
  -v /opt/data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  --name my-db \
  mysql:5.7
```

### 3.3 列出本地镜像 (`docker images`)

**命令格式**: `docker images` 或 `docker image ls`

#### 示例
```bash
# 查看所有本地镜像
sudo docker images

# 筛选特定镜像 (结合 grep)
sudo docker images | grep ubuntu
```

### 3.4 删除镜像 (`docker rmi`)

**命令格式**: `docker rmi [选项] <镜像ID或名称>`

**注意**: 如果镜像正在被容器使用，需先删除容器或使用 `-f` 强制删除。

#### 示例
```bash
# 通过 ID 前3位删除
sudo docker rmi 5a2

# 通过完整名称删除
sudo docker rmi ubuntu:18.04

# (慎用) 批量删除无用镜像 (dangling images)
docker image prune
```

---

## 4. Docker 容器常用命令

### 4.1 列出容器 (`docker ps`)

- `docker ps`: 列出**正在运行**的容器。
- `docker ps -a`: 列出**所有**容器（包括已停止的）。

#### 示例
```bash
# 查看当前运行的服务
docker ps

# 查看所有容器 (包括已停止的)
docker ps -a

# 只显示容器 ID (常用于脚本批量操作)
docker ps -q

# 结合使用: 显示所有容器的 ID
docker ps -aq
```

### 4.2 停止与启动 (`docker stop/start`)

- `docker stop <容器ID>`: 停止容器。
- `docker start <容器ID>`: 启动已停止的容器。
- `docker restart <容器ID>`: 重启容器。

#### 示例
```bash
# 停止一个 Nginx 容器
docker stop my-nginx

# 重启容器
docker restart my-nginx
```

### 4.3 删除容器 (`docker rm`)

- `docker rm <容器ID>`: 删除已停止的容器。
- `docker rm -f <容器ID>`: 强制删除运行中的容器。

#### 示例
```bash
# 删除一个已停止的容器
docker rm my-old-app

# 批量删除所有已停止的容器
docker rm $(docker ps -a -q)
```

### 4.4 查看日志 (`docker logs`)

排查问题时的核心命令。

- `docker logs <容器ID>`: 查看日志输出。
- `docker logs -f <容器ID>`: 实时跟踪日志 (Follow)。

#### 示例
```bash
# 实时查看后端服务的日志
docker logs -f my-backend-service
```

### 4.5 进入容器 (`docker exec`)

在运行的容器中执行命令，通常用于调试。

#### 示例
```bash
# 进入名为 web-server 的容器内部 Shell
docker exec -it web-server /bin/bash
# (如果是 Alpine 镜像，通常用 /bin/sh)
```

---

## 5. Dockerfile 核心指令详解与实战

Dockerfile 是一个文本文件，包含了一系列构建 Docker 镜像的指令。通过 `docker build` 命令，我们可以根据 Dockerfile 的描述自动创建镜像。

### 5.1 常用指令概览

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| **FROM** | 指定基础镜像 (必须是第一条指令) | `FROM ubuntu:18.04` |
| **RUN** | 执行 Shell 命令 (构建时执行) | `RUN apt-get update` |
| **COPY** | 复制本地文件到镜像 | `COPY ./app /usr/bin/app` |
| **WORKDIR** | 设置工作目录 (后续指令在该目录下执行) | `WORKDIR /app` |
| **ENV** | 设置环境变量 (持久化到镜像) | `ENV VERSION=1.0` |
| **ARG** | 设置构建参数 (仅构建时有效) | `ARG GO_VERSION=1.19` |
| **CMD** | 容器启动默认命令 (可被覆盖) | `CMD ["./app"]` |
| **ENTRYPOINT** | 容器启动入口点 (不可覆盖) | `ENTRYPOINT ["./app"]` |
| **EXPOSE** | 声明监听端口 | `EXPOSE 8080` |

### 5.2 核心指令辨析

#### 1. CMD 与 ENTRYPOINT 的区别
这是 Dockerfile 中最容易混淆的两个指令。

| 特性 | CMD | ENTRYPOINT |
| :--- | :--- | :--- |
| **作用** | 设置容器启动的默认命令 | 设置容器的执行入口 |
| **覆盖性** | `docker run` 后的参数会**完全覆盖** CMD | `docker run` 后的参数会**追加**到 ENTRYPOINT 后 |
| **最佳实践** | 用于提供默认参数 | 用于定义固定的执行程序 |

**组合使用最佳实践**:
使用 `ENTRYPOINT` 定义固定的主程序，使用 `CMD` 定义默认参数。
```dockerfile
FROM alpine
ENTRYPOINT ["ls"]
CMD ["-l"]
```
- `docker run my-image` -> 执行 `ls -l`
- `docker run my-image -a` -> 执行 `ls -a` (覆盖了 CMD 的 `-l`)

#### 2. ENV vs ARG
- **ENV (Environment Variable)**: 环境变量。不仅在构建过程中有效，**容器运行时**也依然存在。适合设置程序运行时需要的配置（如数据库地址）。
- **ARG (Build Argument)**: 构建参数。仅在 `docker build` **构建过程**中有效，构建好的镜像内不存在。适合设置版本号等构建时需要的变量。

#### 3. WORKDIR
- 用于指定工作目录。后续的 `RUN`, `CMD`, `ENTRYPOINT`, `COPY` 等指令都会在该目录下执行。
- 如果目录不存在，会自动创建。
- 推荐使用绝对路径。
```dockerfile
WORKDIR /app
COPY . .
# 此时文件被复制到了 /app 目录下
```

### 5.3 实战：构建 Go (Gin) 服务镜像

下面演示如何将一个 Go 语言写的 Web 服务 (Gin 框架) 打包成 Docker 镜像。

**1. 准备 Go 项目**
假设有一个编译好的二进制文件 `main` (注意需在 Linux 环境下编译或设置交叉编译 `CGO_ENABLED=0 GOOS=linux go build ...`)。

**2. 编写 Dockerfile**
```dockerfile
# 1. 指定基础镜像 (使用轻量级的 alpine)
FROM alpine:latest

# 2. 设置工作目录
WORKDIR /app

# 3. 复制二进制文件到镜像
COPY main /app/main

# 4. 声明服务端口
EXPOSE 8080

# 5. 设置启动命令
ENTRYPOINT ["./main"]
```

**3. 构建与运行**
```bash
# 构建镜像
docker build -t gin-server:v1 .

# 运行容器
docker run -d -p 8080:8080 --name my-gin-server gin-server:v1
```

---

## 6. 构建与发布 (`docker build & push`)

### 6.1 构建镜像 (`docker build`)

根据 Dockerfile 构建新镜像。

**命令格式**: `docker build -t <镜像名>:<标签> <Dockerfile路径>`

#### 示例

**1. 标准构建** (使用当前目录下的 Dockerfile)
```bash
# -t: 标记镜像名为 myapp，标签为 v1
# .: 上下文路径为当前目录
docker build -t myapp:v1 .
```

**2. 指定 Dockerfile 文件**
```bash
# -f: 指定 Dockerfile 的路径 (比如 Dockerfile.dev)
docker build -f Dockerfile.dev -t myapp:dev .
```

### 6.2 推送镜像 (`docker push`)

将本地镜像推送到远程仓库（需先 `docker login`）。

#### 示例
```bash
# 1. 登录
docker login

# 2. 标记镜像 (tag) 指向远程仓库地址
docker tag myapp:v1 myusername/myapp:v1

# 3. 推送
docker push myusername/myapp:v1
```

---

## 7. 使用场景与优缺点

### 7.1 使用场景
- **快速部署**: 消除“在我机器上能跑”的问题。
- **微服务架构**: 独立部署和扩展服务。
- **CI/CD**: 自动化构建和测试环境。

### 7.2 优势
- **轻量级**: 共享宿主机内核，资源占用少。
- **秒级启动**: 远快于虚拟机。
- **一致性**: 无论开发、测试还是生产环境，环境完全一致。

### 7.3 局限性
- **隔离性**: 弱于虚拟机（共享内核可能导致安全风险）。
- **持久化**: 数据需要挂载 Volume，否则重启即丢。
- **OS依赖**: 只能运行与宿主机内核兼容的 OS（如 Linux 容器不能直接在纯 Windows 核心运行，需 WSL2）。

---

## 8. 知识小结

| 知识点 | 核心内容 | 操作示例 |
| :--- | :--- | :--- |
| **镜像 (Image)** | 应用的静态打包 (类) | `docker pull ubuntu:18.04` |
| **容器 (Container)** | 镜像的动态运行实例 (对象) | `docker run -it ubuntu bash` |
| **列出容器** | 查看运行/所有状态 | `docker ps -a` |
| **日志查看** | 调试必用 | `docker logs -f my-app` |
| **进入容器** | 运行时调试 (exec) | `docker exec -it my-app bash` |
| **Dockerfile指令** | `COPY`, `CMD`, `ENTRYPOINT` | `ENTRYPOINT ["./app"]` |
| **构建镜像** | Dockerfile -> Image | `docker build -t my-app:v1 .` |
| **删除资源** | 这里要注意依赖关系 | `docker rm <ID>` (容器) / `docker rmi <ID>` (镜像) |

---

## 9. 未来发展

Docker 已经成为云原生时代的基石。随着 Kubernetes (K8s) 的普及，Docker 作为容器运行时（Runtime）的标准地位更加稳固。未来，它将继续在微服务、Serverless 和边缘计算中发挥核心作用。