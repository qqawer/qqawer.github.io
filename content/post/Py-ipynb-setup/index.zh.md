---
title: macOS 搭建 Python 虚拟环境 + Jupyter/ipynb 完整配置指南
description: 本文档适配 macOS 系统，从 0 开始完成 Python 虚拟环境搭建、Jupyter 依赖安装，最终实现 VS Code 中 .ipynb 文件的正常运行。
date: 2026-03-10
slug: macos-python-jupyter-setup
categories:
    - Documentation
tags:
    - macOS
    - Python
    - Jupyter
    - VS Code
    - venv
toc: true
---

# macOS 搭建 Python 虚拟环境 + Jupyter/ipynb 完整配置指南

## 文档说明
本文档适配 macOS 系统，从 0 开始完成 Python 虚拟环境搭建、Jupyter 依赖安装，最终实现 VS Code 中 `.ipynb` 文件的正常运行，全程聚焦「环境隔离」和「新手友好」，所有命令可直接复制执行。

## 核心亮点
- **环境隔离**：通过 `venv` 确保项目依赖不干扰系统环境。
- **配置直达**：针对 macOS 和 VS Code 进行深度优化，解决找不到内核等常见痛点。
- **包管理**：包含环境迁移和 `requirements.txt` 的最佳实践。

## 最终目标
在指定目录（示例为机器学习项目目录）下创建独立虚拟环境，实现：
- 虚拟环境与系统全局 Python 完全隔离
- VS Code 中 `.ipynb` 文件使用该虚拟环境的依赖包
- Jupyter 内核正常启动，无版本兼容警告

## 一、前置准备
### 1.1 检查系统环境
确认 macOS 终端可正常使用（推荐自带「终端」或 iTerm2），无需提前安装 Python（下文会统一安装兼容版本）。

### 1.2 目标路径说明
本文示例虚拟环境存放路径：
```
/Users/outsider/Downloads/NUS-ISS/SA61-ClassDocument+Exam/SA4110 Machine Learning Application Development/Myenv/
```
可根据自身项目路径替换，注意路径中的空格需用引号包裹。

## 二、步骤 1：安装 Python 3.10（兼容 Jupyter 稳定版本）
macOS 自带 Python 版本较旧，优先通过 Homebrew 安装 Python 3.10（Jupyter 官方支持的 LTS 版本）。

### 2.1 安装 Homebrew（未安装则执行）
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
安装完成后，验证 Homebrew：
```bash
brew --version
```

### 2.2 安装 Python 3.10
```bash
brew install python@3.10
```

### 2.3 验证 Python 安装
```bash
/opt/homebrew/bin/python3.10 --version
```
✅ 预期输出：`Python 3.10.19`（版本号略有差异属正常）。

## 三、步骤 2：创建专属虚拟环境
### 3.1 进入目标目录
```bash
cd "/Users/outsider/Downloads/Myenv"
```

### 3.2 创建虚拟环境（命名为 `env`）
```bash
/opt/homebrew/bin/python3.10 -m venv env
```
执行后，`Myenv` 目录下会生成 `env` 文件夹（虚拟环境核心文件）。

```bash
# 重命名旧环境（可选，建议做）把env命名为env_old
mv env env_old
```

### 3.3 激活虚拟环境
```bash
source env/bin/activate
```
✅ 验证激活：终端提示符开头出现 `(env)`，说明已进入虚拟环境。

## 四、步骤 3：安装 Jupyter/ipynb 核心依赖
**所有操作需在激活虚拟环境（`(env)` 提示符）下执行**，确保依赖安装到虚拟环境中。

### 4.1 升级 pip（避免安装报错）
```bash
pip install --upgrade pip
```
⚠️ 若提示 `pip: command not found`，改用虚拟环境内置 pip：
```bash
/Users/outsider/Downloads/NUS-ISS/SA61-ClassDocument+Exam/SA4110 Machine Learning Application Development/Myenv/env/bin/python -m pip install --upgrade pip
```

### 4.2 安装 Jupyter 核心依赖
```bash
pip install jupyter ipykernel
```

### 4.3 （可选）安装机器学习常用包/安装旧包
根据项目需求安装，示例：
```bash
pip install pandas numpy scikit-learn matplotlib tensorflow
```

```bash
# 从旧环境导出所有包到 requirements.txt，带有空格所以用\ 转义
/Users/outsider/Downloads/NUS-ISS/SA61-ClassDocument+Exam/SA4110\ Machine\ Learning\ Application\ Development/Myenv/myenv_old/bin/python -m pip freeze > requirements.txt

# 激活新环境（提示符变成 (env)）
source env/bin/activate
# 在新环境中安装所有包
pip install -r requirements.txt
```

### 4.4 验证依赖安装
```bash
pip list
```
✅ 预期输出：列表中包含 `jupyter`、`ipykernel`、`pandas`（若安装）等包。

## 五、步骤 4：VS Code 配置（识别虚拟环境）
### 5.1 安装必要扩展
打开 VS Code → 左侧扩展栏（快捷键 `Cmd+Shift+X`），搜索并安装：
- `Jupyter`（微软官方，图标为紫色笔记本）
- `Python`（微软官方，图标为蓝色蛇形）

### 5.2 选择虚拟环境作为 ipynb 内核
1. 打开目标 `.ipynb` 文件（或新建：`Cmd+Shift+P` → 输入 `Jupyter: Create New Notebook`）；
2. 点击 VS Code 右上角「Select Kernel」→ 选择「Select Another Kernel...」；
3. 选择「Python Environments...」；
4. 在列表中找到虚拟环境：`env (Python 3.10.19) /Users/outsider/.../Myenv/env/bin/python`；
   ⚠️ 若未显示，选择「Enter interpreter path...」→「Browse...」，手动定位到：
   ```
   /Users/outsider/Downloads/NUS-ISS/SA61-ClassDocument+Exam/SA4110 Machine Learning Application Development/Myenv/env/bin/python
   ```
5. 选中后，VS Code 自动加载该环境的依赖。

## 六、步骤 5：验证配置成功
在 `.ipynb` 文件中新建代码单元格，运行以下代码：
```python
# 验证 Python 解释器路径（是否为虚拟环境）
import sys
print("Python 路径（含 Myenv/env 则正确）：", sys.executable)

# 验证 Jupyter 内核
import ipykernel
print("ipykernel 版本：", ipykernel.__version__)

# 验证安装的包（示例：numpy）
try:
    import numpy
    print("numpy 版本：", numpy.__version__)
    print("✅ 配置成功！ipynb 可正常使用虚拟环境")
except ImportError:
    print("❌ 包未加载，需检查安装步骤")
```

✅ 预期输出示例：
```
Python 路径（含 Myenv/env 则正确）： /Users/outsider/.../Myenv/env/bin/python
ipykernel 版本： 6.25.2
numpy 版本： 1.26.4
✅ 配置成功！ipynb 可正常使用虚拟环境
```

## 七、常见问题解决（macOS 专属）
### 7.1 VS Code 找不到虚拟环境
- 重启 VS Code（macOS 需重启扫描新环境）；
- 先在 VS Code 左下角状态栏切换 Python 解释器到虚拟环境，再切回 ipynb 选内核；
- 检查 `env/bin/` 目录下是否有 `python`、`pip`、`ipykernel` 文件。

### 7.2 ipynb 提示「内核启动失败」
激活虚拟环境后执行：
```bash
source env/bin/activate
pip install --upgrade ipykernel
python -m ipykernel install --user --name=env  # 注册内核到系统
```

### 7.3 终端关闭后虚拟环境失效
每次打开新终端，重新执行激活命令：
```bash
cd "/Users/outsider/.../Myenv" && source env/bin/activate
```

## 八、核心操作总结
1. **环境创建**：`python3.10 -m venv env` 生成虚拟环境，`source env/bin/activate` 激活；
2. **依赖安装**：激活环境后用 `pip` 安装 `jupyter ipykernel`，确保依赖隔离；
3. **VS Code 配置**：手动定位虚拟环境的 `python` 路径，避免选全局环境；
4. **验证关键**：ipynb 中输出的 Python 路径包含 `Myenv/env`，且能导入安装的包。

## 九、常用快捷操作
| 操作                  | 命令/快捷键                          |
|-----------------------|--------------------------------------|
| 激活虚拟环境          | `source env/bin/activate`            |
| 退出虚拟环境          | `deactivate`                         |
| 导出包列表            | `pip freeze > requirements.txt`      |
| 一键安装包列表        | `pip install -r requirements.txt`    |
| VS Code 打开 ipynb    | `code 文件名.ipynb`（终端执行）|
| 重启 Jupyter 内核     | VS Code 中点击「Kernel」→「Restart Kernel」 |
