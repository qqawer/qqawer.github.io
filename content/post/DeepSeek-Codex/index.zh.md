---
title: "DeepSeek 接入 Codex"
description: "macOS 实操：DeepSeek 官方脚本接入 Codex、创建 API Key、常见报错排查与重启验证"
date: 2026-08-08
slug: "deepseek-codex-integration"
categories:
    - Tutorial
tags:
    - DeepSeek
    - Codex
    - macOS
toc: true
---


# 将 DeepSeek 接入 Codex（macOS 实操）

## 一、前言
Codex 是 OpenAI 推出的 AI 编程助手，通过 Responses API 与模型交互；DeepSeek API 原生兼容这一格式，因此可以把 DeepSeek 模型作为 Codex 的模型提供方来使用（目前官方支持 `deepseek-v4-flash`）。配置一次后，Codex CLI、ChatGPT 桌面端、VS Code 的 Codex 插件共用同一份配置文件，所有形态都能使用 DeepSeek 模型。

本文以 macOS 为例，记录完整的接入流程、重启验证方法，以及遇到 `The generated config.toml failed TOML validation (possibly duplicate keys)` 报错时的排查思路。

## 二、前置条件
- macOS（自带 `bash` 与 `curl`）
- 已安装 Codex CLI 或 ChatGPT 桌面端，并且**至少运行过一次**（保证 `~/.codex` 目录已存在）。官方脚本检测不到 Codex 配置目录会直接退出
- DeepSeek API Key（以 `sk-` 开头）

## 三、整体流程
1. 打开官方接入文档：[Quick Start - Integrate with Codex](https://api-docs.deepseek.com/quick_start/agent_integrations/codex)
2. 创建 API Key：[DeepSeek Platform - API Keys](https://platform.deepseek.com/api_keys)
3. 在终端运行官方一键配置脚本
4. 重启 Codex，验证模型已切换

> 小技巧：如果提前设置了环境变量 `DEEPSEEK_API_KEY`（值需以 `sk-` 开头），脚本会直接使用它并跳过手动输入环节。

## 四、具体步骤

### 4.1 创建 API Key
打开 [DeepSeek Platform](https://platform.deepseek.com/api_keys)，创建一个新的 API key 并复制（以 `sk-` 开头）。也可以暂不创建，等脚本运行到输入 key 的环节时再去创建。

### 4.2 运行官方一键配置脚本
在终端中执行：

```bash
bash <(curl -fsSL https://cdn.deepseek.com/api-docs/codex-deepseek-setup.sh)
```

运行后按菜单选择操作：

- `1`：使用 `deepseek-v4-flash` 模型
- `2`：使用 `deepseek-v4-pro`（官方标注暂未支持，预计 2026 年 8 月初上线）
- `3`：恢复默认的 Codex 配置（删除 deepseek 相关配置）

首次安装输入 `1`，然后按提示粘贴 API key（必须以 `sk-` 开头，否则会要求重新输入）。

脚本会依次完成以下工作：

1. **备份**：将 `~/.codex/config.toml` 备份到 `~/.codex/backup-deepseek/`，之后可用菜单 `3` 一键还原
2. **写入 `~/.codex/models.json`**：向 Codex 声明 DeepSeek 模型的元数据（上下文窗口长度、支持的推理强度档位、工具调用格式等）
3. **改写 `~/.codex/config.toml`**：改写必要的顶层字段并新增 `[model_providers.deepseek]` 配置段；你原有的 MCP 服务器、项目信任级别等配置全部保留，与 DeepSeek 冲突的字段（如 `profiles`）会被删除并打印原因
4. **校验**：写入前先校验 `config.toml` / `models.json` 语法合法，校验失败则中止且不修改任何文件

安装成功后，`config.toml` 中与 DeepSeek 相关的配置大致如下：

```toml
model                  = "deepseek-v4-flash"
model_provider         = "deepseek"
preferred_auth_method  = "apikey"
forced_login_method    = "api"
model_reasoning_effort = "high"
model_catalog_json     = "~/.codex/models.json"

[model_providers.deepseek]
base_url  = "https://api.deepseek.com/"
wire_api  = "responses"
```

### 4.3 重启 Codex 验证
- **Codex CLI**：完全退出后重新打开，启动信息中应显示 `model: deepseek-v4-flash`
- **ChatGPT 桌面端**：模型选择器中显示「自定义」，实际使用的就是 DeepSeek 模型
- 之后再次运行脚本即可切换模型（选 `1` / `2`）或恢复默认配置（选 `3`）

## 五、常见报错：The generated config.toml failed TOML validation (possibly duplicate keys)

### 5.1 现象与原因
完整报错类似：

```text
✗ 生成的 config.toml 未通过 TOML 校验（可能存在重复 key），已中止。
原文件未被修改，备份在：~/.codex/backup-deepseek
```

TOML 规范不允许同一个 key 或同一个表被定义两次。当生成的新配置里出现重复 key 时（例如 `config.toml` 中原本已有 deepseek 相关配置、之前手动编辑留下的重复字段、或其他工具写坏的配置），`tomllib` 解析就会失败，脚本随即中止。**此时脚本尚未写入任何文件，你的原 `config.toml` 是安全的**，备份完整保留在 `~/.codex/backup-deepseek/`。

### 5.2 关键：为什么直接重跑脚本还是会报错
校验失败后，`~/.codex/backup-deepseek` 已经被创建（里面是安装前的 `config.toml` 备份），但 `models.json` 还没有写入。此时直接重跑脚本，会先命中脚本的「备份目录已存在但状态不符」检查（提示缺少 `models.json` 等），再次中止。所以需要先清理这个残留状态，才能回到首次安装流程。

### 5.3 修复步骤（推荐顺序）

**第 1 步：检查 `config.toml` 里是否有重复内容**

```bash
rg -n "^\[model_providers\.deepseek\]|^model\s*=|^model_provider\s*=" ~/.codex/config.toml
```

如果发现两个 `[model_providers.deepseek]` 段，或 `model` / `model_provider` 出现两次，手动删掉多余的、只保留一份（建议先 `cp ~/.codex/config.toml ~/.codex/config.toml.bak` 留个底）。

**第 2 步：清理残留的备份目录**

```bash
rm -rf ~/.codex/backup-deepseek
```

这也是官方脚本自己的报错提示中给出的处理方式（方案 b）。需要注意：这个目录里保存的是安装前的 `config.toml`，删掉后就不能再用菜单 `3` 一键还原了。如果还想保留还原能力，可以不删，改为重跑脚本选 `3` 先还原、再选 `1` 重新安装。

**第 3 步：重新运行官方脚本**

```bash
bash <(curl -fsSL https://cdn.deepseek.com/api-docs/codex-deepseek-setup.sh)
```

输入 `1`，粘贴 API key，等待安装完成。

### 5.4 如果删了备份目录重跑仍然报同样的错
说明重复 key 不是脚本产生的，而是 `config.toml` 本身的问题。常见情况：

- 之前手动配置过 deepseek，旧配置里残留了重复的段或键；
- 旧配置用了 `[model_providers]` 下的内联表写法（`deepseek = { ... }`），脚本的扫描器识别不到，追加新段时产生冲突；
- `config.toml` 被其他工具写坏，本身就存在重复 key。

此时需要：

1. 打开 `~/.codex/config.toml`，删除重复的段 / 键，只保留一份；
2. 或者把现有配置移走，让脚本基于干净状态生成，再把需要的 MCP 等配置手动合回来：

```bash
mv ~/.codex/config.toml ~/.codex/config.toml.bak
rm -rf ~/.codex/backup-deepseek
```

然后重新运行脚本即可。

## 六、小结
- 接入靠官方脚本一次完成：备份 → 写 `models.json` → 改写 `config.toml` → 校验 → 落盘
- API Key 以 `sk-` 开头；脚本校验失败时不会改坏原文件
- 遇到重复 key 报错：先清理 `config.toml` 里的重复项，再删除 `backup-deepseek` 残留（或选 `3` 还原），然后重跑脚本
- 装完记得重启 Codex：CLI 看启动信息中的 `model`，桌面端看模型选择器中的「自定义」
