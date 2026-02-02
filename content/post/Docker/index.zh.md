---
title: "Docker 学习笔记：镜像操作详解"
description: "深入理解 Docker 镜像的核心操作：获取、运行、列出与删除"
date: 2026-02-02
slug: "docker-image-operations"
categories:
    - Documentation
tags:
    - Docker
    - DevOps
toc: true
---

## 1. 获取镜像

### 1) `docker pull`

[docker pull 示意图](https://images.unsplash.com/photo-1605745341117-9575522cd999?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80)
*(示例图: 容器拉取流程)*

**命令格式**:  
`docker pull [选项] [Docker Registry地址[:端口号]/]仓库名[:标签]`

**地址格式**:
- 默认地址是 **Docker Hub** (`docker.io`)
- 格式一般为 `<域名/IP>[端口号]`

**仓库名**:
- 两段式名称 `<用户名>/<软件名>`
- 不指定用户名时默认为 `library` (官方镜像)

> **隐含操作**: `docker run` 命令会自动执行 pull 操作，若本地不存在对应镜像。

#### 例题: Ubuntu 镜像拉取

1.  通过 Docker Hub 搜索官方 Ubuntu 镜像。
2.  选择特定版本标签 (如 `18.04`)。
3.  执行命令:
    ```bash
    sudo docker pull ubuntu:18.04
    ```
    *(注意：非 root 用户需加 sudo 权限)*

---

### 2) 运行镜像

**基本命令**:
```bash
docker run -it --rm ubuntu:18.04 bash
```

**参数说明**:
- `-i`: **交互式操作** (Interactive)，保持标准输入打开。
- `-t`: **分配终端** (Terminal)，为容器分配一个伪终端。
- `--rm`: **自动删除**，容器退出后自动删除文件系统，避免堆积垃圾。
- `bash`: 指定运行的命令 (Shell)。

> **注意事项**:
> - 精简版 Linux (如 Alpine) 可能只支持 `sh` 而非 `bash`。
> - `--rm` 非常适合一次性任务场景 (如测试、脚本执行)。

#### 例题: Ubuntu 镜像运行

1.  执行命令:
    ```bash
    sudo docker run -it --rm ubuntu:18.04 bash
    ```
2.  验证系统版本:
    ```bash
    cat /etc/os-release
    ```
3.  退出容器:
    ```bash
    exit
    ```
    *(此时容器会自动删除)*

---

## 2. 列出本地的镜像

**基本命令**:
```bash
sudo docker images      # 或者
sudo docker image ls
```

**筛选技巧**:
- 结合 `grep` 过滤特定镜像:
    ```bash
    docker image ls | grep ubuntu
    ```
- 指定镜像查询:
    ```bash
    docker images ubuntu:18.04
    ```

**输出字段说明**:
- **REPOSITORY**: 仓库名
- **TAG**: 标签 (版本)
- **IMAGE ID**: 镜像 ID (唯一标识)
- **CREATED**: 创建时间
- **SIZE**: 镜像大小

---

## 3. 删除镜像

**基本命令**:

1.  **通过 ID 删除** (推荐简写):
    ```bash
    docker image rm 5a2  # 仅需输入前3位字符
    ```
2.  **通过名称删除**:
    ```bash
    docker image rm ubuntu:18.04
    ```

**注意事项**:
- ⚠️ **被容器使用的镜像无法删除** (需先停止并删除相关容器)。
- **批量删除** (慎用):
    ```bash
    docker image rm $(docker image ls -q ubuntu)
    ```

**删除过程**:
1.  **Untagged**: 移除标签引用。
2.  **Deleted**: 真正删除镜像层数据 (如果没有其他标签指向它)。

---

## 4. 知识小结

| 知识点 | 核心内容 | 易混淆点 / 注意事项 | 操作示例 |
| :--- | :--- | :--- | :--- |
| **镜像拉取** | `docker pull` 下载镜像而不启动 | 与 `run` 区别: `run` = `pull` + `create` + `start` | `docker pull ubuntu:18.04` |
| **镜像来源** | 默认 Docker Hub | 可配置国内加速源; 省略前缀默认 library | - |
| **版本控制** | 通过 Tag 区分 (如 5.7, 8.0) | `latest` 不一定是最新稳定版; 生产环境推荐指定 Tag | - |
| **交互式容器** | `-it` 参数 (交互+终端) | 需确认镜像包含 Shell (`bash`/`sh`) | `docker run -it --rm ubuntu bash` |
| **临时容器** | `--rm` 参数 (退出即删) | 数据随容器销毁; 适合临时任务 | - |
| **镜像管理** | `docker images` 查看列表 | `image` (单) vs `images` (复); 配合 `grep` | `docker images \| grep ubuntu` |
| **镜像删除** | `docker image rm` | **先删容器，再删镜像**; 简写 ID | `docker image rm 5a2` |