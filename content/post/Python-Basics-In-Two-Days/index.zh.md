---
title: "Python 基础速通：两天学会写函数、调 API 和看懂报错"
description: "结合廖雪峰 Python 教程与 Python 官方 Tutorial，用一个 API 小项目串起变量、容器、控制流、函数、类、异常、venv、pip、JSON、类型注解、装饰器与 asyncio。"
date: 2026-09-03
slug: "python-basics-in-two-days"
categories:
    - Backend
tags:
    - Python
    - Python 基础
    - API
    - asyncio
    - 学习笔记
image: /post/python-basics-in-two-days/01-learning-route.png
toc: true
---

很多 Python 学习路线的问题，不是内容不够，而是内容太完整：刚记住列表，马上遇到生成器；刚会写类，又被元类拦住。学了几天，概念见过不少，真正需要调用一个 API 时还是不知道从哪里下手。

更实用的目标是：**先掌握一条能跑通小项目的最短路径，再让项目暴露知识缺口。**

[廖雪峰的 Python 教程](https://liaoxuefeng.com/books/python/introduction/index.html)面向零基础读者，示例完整、路径平缓；[Python 官方 Tutorial](https://docs.python.org/3/tutorial/)则明确假设读者已经懂一点编程，更适合校准语言细节和 Python 的惯用写法。把两者叠在一起，一条高效路线就很清楚了：

1. 先学数据、分支、循环、函数和异常，获得“能写程序”的能力；
2. 再学模块、虚拟环境、包、HTTP 和 JSON，获得“能做项目”的能力；
3. 最后补类、类型注解、装饰器和异步，获得“能读工程代码”的能力。

{{< figure src="/post/python-basics-in-two-days/01-learning-route.png" alt="小黑推着代码沿 Python 学习路线前进，先经过变量、函数与异常，再接通 API 项目" caption="不要先翻完整本字典：沿着一条可运行的路线，先把小项目接通。" >}}

这篇文章不追求覆盖 Python 的每个角落，而是用一个“调用 API、筛选数据、输出结果”的小项目，把真正高频的基础串起来。

## 1. 第一层心智模型：名字指向对象

Python 变量没有固定类型，**对象有类型，变量只是指向对象的名字**：

```python
age = 18             # age 指向整数对象 18
age = "eighteen"     # 现在改为指向字符串对象
```

这叫动态类型。它让代码简洁，却不等于“没有类型”。`18 + 1` 合法，`"18" + 1` 会在运行时抛出 `TypeError`。

更容易踩坑的是可变性：

```python
a = [1, 2]
b = a
b.append(3)

print(a)  # [1, 2, 3]
```

`a` 和 `b` 指向同一个列表对象，修改 `b` 并没有创建新列表。与之相对，整数、字符串和元组通常按不可变对象理解：所谓“修改”，实际是让名字重新指向另一个对象。

{{< figure src="/post/python-basics-in-two-days/02-names-and-objects.png" alt="小黑转动对象转盘，名字 a 和 b 同时指向一个可变列表，而 c 从 42 重新绑定到 43" caption="变量是名字，不是盒子；两个名字可以指向同一个可变对象。" >}}

这个模型还能解释函数参数。官方教程将其描述为：传入的是**对象引用的值**。函数若修改传入的列表，调用方能看到变化；若只给参数名重新赋值，调用方的名字不受影响。

```python
def add_item(items: list[str]) -> None:
    items.append("Python")       # 修改同一个列表


def replace(items: list[str]) -> None:
    items = ["new"]              # 只让局部名字指向新列表
```

## 2. 常用数据结构：先学会选，不要只会背

Python 最常见的容器可以用四个问题区分：

| 类型 | 是否有序 | 是否可变 | 是否允许重复 | 典型用途 |
| --- | --- | --- | --- | --- |
| `list` | 是 | 是 | 是 | 一组会增删、排序的数据 |
| `tuple` | 是 | 否 | 是 | 不希望被改动的一组值 |
| `dict` | 保留插入顺序 | 是 | 键唯一 | 按键查值、表示 JSON 对象 |
| `set` | 不依赖顺序 | 是 | 否 | 去重、成员测试、集合运算 |

处理 API 返回数据时，最常见的是 `list[dict]`：外层是一批记录，内层每条记录由键和值组成。

```python
repos = [
    {"name": "cpython", "stars": 70000, "topics": ["python"]},
    {"name": "demo", "stars": 12, "topics": []},
]

popular_names = [
    repo["name"]
    for repo in repos
    if repo["stars"] >= 1000
]
```

列表推导式适合“遍历、筛选、变换”都很短的场景。逻辑一旦包含多层条件、异常或副作用，普通 `for` 循环通常更容易读。

几个高频习惯值得直接记住：

```python
for index, repo in enumerate(repos, start=1):
    print(index, repo["name"])

for name, stars in {"cpython": 70000}.items():
    print(name, stars)

unique_topics = {topic for repo in repos for topic in repo["topics"]}
```

Python 的 `for` 遍历的是可迭代对象，而不是 C 风格的计数器。需要索引时优先考虑 `enumerate()`，同时遍历两个序列时考虑 `zip()`。官方教程还特别提醒：不要一边遍历同一个集合一边修改它；可以遍历副本，或构造一个新集合。

## 3. 控制流：缩进就是语法

Python 用缩进表示代码块，通常使用 4 个空格：

```python
def level(stars: int) -> str:
    if stars >= 10_000:
        return "popular"
    elif stars >= 1_000:
        return "growing"
    return "small"
```

基础阶段需要掌握的控制流不多：

- `if / elif / else`：根据条件分支；
- `for`：遍历可迭代对象；
- `while`：条件成立时重复；
- `break`：退出当前循环；
- `continue`：跳到下一轮；
- `match / case`：按值或结构做模式匹配，适合分支较多且结构稳定的输入。

Python 里的空容器、空字符串、数字 `0` 和 `None` 在条件中都被视为假值，因此常见写法是：

```python
if not repos:
    print("没有结果")
```

但“缺少值”和“值恰好为空”含义不同时，应明确写 `value is None`，不要只依赖真假判断。

## 4. 函数：把变化关进参数，把结果交给 return

函数不是为了减少几行复制粘贴，而是给一段逻辑划出边界。一个好函数通常有明确输入、单一职责和可预测输出。

```python
def select_popular(
    repos: list[dict],
    *,
    min_stars: int = 1_000,
) -> list[dict]:
    """返回 star 数不低于阈值的仓库。"""
    return [repo for repo in repos if repo.get("stars", 0) >= min_stars]
```

这里同时出现了几个重要语法：

- `min_stars=1_000` 是默认参数；
- 单独的 `*` 让后续参数只能按关键字传递，调用时更清楚；
- `list[dict]` 是类型注解，帮助编辑器和类型检查工具理解代码；
- 三引号字符串是 docstring，用来说明函数契约。

类型注解默认**不会在运行时强制检查类型**。它更像写给人、IDE 和静态检查器的可执行说明。

默认参数还有一个经典陷阱：默认值只在函数定义时计算一次，不要把可变对象直接写成默认值。

```python
  # 错误：多次调用会共享同一个列表
def collect_bad(item, bucket=[]):
    bucket.append(item)
    return bucket


  # 正确：用 None 表示“尚未创建”
def collect(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

## 5. 模块、venv 与 pip：让“我的电脑能跑”变成“这个项目能跑”

一个 `.py` 文件就是模块。项目变大后，可以按职责拆分：

```text
repo_report/
├── .venv/
├── main.py
├── api.py
└── formatter.py
```

用导入连接模块：

```python
from api import fetch_repos
from formatter import render_report
```

第三方包不应该随意安装进系统 Python。官方 Tutorial 的[虚拟环境与包管理](https://docs.python.org/3/tutorial/venv.html)章节给出的核心思路是：每个项目拥有独立环境，从而避免不同项目对同一个库要求不同版本时互相冲突。

```bash
python -m venv .venv

  # macOS / Linux
source .venv/bin/activate

  # Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install requests
python -m pip freeze > requirements.txt
```

推荐写 `python -m pip`，因为它明确使用当前这个 Python 解释器对应的 `pip`。看到终端前出现 `(.venv)` 只是提示，真正的验证方式是检查解释器位置和包列表。

## 6. 调 API 与 JSON：第一个真正有用的小项目

HTTP API 可以先理解为一个远程函数：你发送请求，它返回状态码、响应头和响应体。JSON 是常见的响应体格式，对象和数组进入 Python 后通常变成 `dict` 和 `list`。

下面用公开的 GitHub API 查询仓库。示例不需要令牌，但未认证请求有更严格的频率限制。

```python
from typing import Any

import requests


def fetch_repos(language: str, limit: int = 5) -> list[dict[str, Any]]:
    url = "https://api.github.com/search/repositories"
    response = requests.get(
        url,
        params={"q": f"language:{language}", "sort": "stars"},
        headers={"Accept": "application/vnd.github+json"},
        timeout=10,
    )
    response.raise_for_status()

    payload = response.json()
    return payload["items"][:limit]


def main() -> None:
    for repo in fetch_repos("python"):
        print(f"{repo['full_name']:<30} ⭐ {repo['stargazers_count']}")


if __name__ == "__main__":
    main()
```

这一小段代码已经把基础知识连成了闭环：

- 字符串、整数、字典和列表负责保存数据；
- 函数和参数划定职责；
- `requests` 模块负责 HTTP；
- `response.json()` 把 JSON 响应解析成 Python 对象；
- `for` 循环遍历结果；
- f-string 格式化输出；
- `if __name__ == "__main__"` 让文件既可作为脚本运行，也可被其他模块导入。

调用 API 时至少要养成三个习惯：设置 `timeout`，检查非成功状态码，不要假设每个字段都永远存在。廖雪峰教程的 [`requests` 章节](https://liaoxuefeng.com/books/python/third-party-modules/requests/index.html)适合快速上手；项目中还应继续查阅 `requests` 自身文档确认参数和异常类型。

## 7. 异常：报错不是敌人，含糊的失败才是

语法错误意味着代码还不能被解析；异常意味着代码已开始运行，但遇到了无法按当前路径继续处理的情况。`try / except / else / finally` 分别承担不同职责：

```python
import requests


def safe_fetch() -> list[dict]:
    try:
        return fetch_repos("python")
    except requests.Timeout:
        print("请求超时，可以稍后重试")
    except requests.HTTPError as exc:
        print(f"服务返回错误状态：{exc}")
    except requests.RequestException as exc:
        print(f"网络请求失败：{exc}")
    return []
```

只捕获自己能处理的异常。直接写 `except Exception: pass` 会抹掉现场，让程序表面继续运行、数据却悄悄出错。需要释放文件、网络连接等资源时，优先使用 `with` 上下文管理器；必须无论成功失败都执行的清理，放进 `finally`。

{{< figure src="/post/python-basics-in-two-days/03-exception-routing.png" alt="小黑操作异常分拣机，让正常结果、预期错误与清理动作走向不同出口，并推开吞掉所有错误的黑布" caption="异常处理的目标不是让错误消失，而是把可处理的失败变成明确分支。" >}}

官方 Tutorial 的[错误与异常](https://docs.python.org/3/tutorial/errors.html)章节还覆盖主动 `raise`、异常链、自定义异常和清理动作。初学阶段最重要的是学会读 traceback：**先看最后一行的异常类型和消息，再从下往上找第一处属于自己代码的位置。**

## 8. 类：当数据和行为属于同一个概念

不是所有代码都需要类。若只是输入数据、计算结果，一个函数往往更直接。当一组状态和行为需要共同维护时，类才开始有价值。

```python
class Repo:
    def __init__(self, name: str, stars: int) -> None:
        self.name = name
        self.stars = stars

    def is_popular(self, threshold: int = 1_000) -> bool:
        return self.stars >= threshold


repo = Repo("python/cpython", 70_000)
print(repo.is_popular())
```

`Repo` 是类，`repo` 是实例，`self` 指向当前实例。实例属性保存每个仓库自己的数据，方法描述这个对象能做什么。继承与多态值得了解，但组合通常更容易控制；不要为了“面向对象”而把每个函数都塞进类。

官方 Tutorial 的[类](https://docs.python.org/3/tutorial/classes.html)章节特别强调名字、对象、作用域和命名空间。理解这些基础，比先背双下划线方法更重要。

## 9. 装饰器：不改函数正文，给调用包一层行为

Python 函数也是对象，可以赋值、传参和返回。装饰器正是利用这一点，把一个函数交给另一个函数包装。

```python
from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import Any


def timed(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__}: {perf_counter() - start:.3f}s")

    return wrapper


@timed
def build_report() -> list[dict]:
    return fetch_repos("python")
```

`@timed` 大致等价于 `build_report = timed(build_report)`。日志、权限、缓存、重试和 Web 路由中经常看到装饰器。先理解“函数进、函数出”的包装关系，再读框架代码会轻松很多。

## 10. asyncio：优化等待，不是让 CPU 突然变快

同步代码一次等待一个请求，写法直观，通常应该先从它开始。当程序需要同时等待许多网络请求时，`asyncio` 可以在一个任务等待 I/O 的间隙推进其他任务。

```python
import asyncio


async def fetch_one(name: str) -> str:
    print(f"开始：{name}")
    await asyncio.sleep(1)  # 模拟网络等待
    return f"完成：{name}"


async def main() -> None:
    results = await asyncio.gather(
        fetch_one("A"),
        fetch_one("B"),
        fetch_one("C"),
    )
    print(results)


asyncio.run(main())
```

`async def` 定义协程函数；调用它得到协程对象；`await` 暂停当前协程，把控制权交还事件循环；`gather()` 并发等待多个可等待对象。

{{< figure src="/post/python-basics-in-two-days/04-sync-vs-async.png" alt="同步场景中小黑守着一只水壶等待，异步场景中小黑在多只水壶等待期间切换任务" caption="异步不会让一壶水烧得更快；它让等待期间的服务员不必站着发呆。" >}}

异步适合大量 I/O 等待，不适合直接解决 CPU 密集计算。也不要在协程里调用会长时间阻塞的同步库，否则整个事件循环仍会被卡住。廖雪峰的[协程与异步 I/O](https://liaoxuefeng.com/books/python/async-io/coroutine/index.html)可以帮助建立直觉，但真实 HTTP 项目还需要选择支持异步的客户端，并学习超时、取消、并发上限和错误传播。

## 11. 两天学习安排：以输出物验收

### 第一天：写出同步版本

上午掌握变量、字符串、列表、字典、集合、条件和循环；下午学习函数、模块、异常、文件与 JSON，并完成：

```text
输入关键词 → 调用一个公开 API → 筛选结果 → 输出 Markdown 报告
```

当天的验收标准不是“看完多少章”，而是：能独立写一个函数，能解释参数和返回值，遇到异常能读 traceback，知道数据为什么是 `list` 或 `dict`。

### 第二天：把脚本整理成项目

先用 `venv` 和 `pip` 隔离依赖，再给核心函数加类型注解，抽出一个小类，写一个计时装饰器。最后把三个模拟请求改成 `asyncio.gather()`，对比同步和异步的总耗时。

当天的验收标准是：能从空目录创建环境并运行项目，能解释 `import`、JSON 解析、异常分支和 `await` 分别解决什么问题。

## 12. 真正需要记住的，不是语法清单

Python 基础可以压缩成四个动作：

1. 用对象和容器表示数据；
2. 用控制流和函数组织变化；
3. 用模块、环境和包连接外部能力；
4. 用异常、类型与测试守住边界。

类、装饰器和异步不是另一门语言，只是这四个动作在更大代码里的延伸。学到能写函数、能调 API、能看懂报错时，就应该开始做项目。项目会非常诚实地告诉你下一章该读什么。

## 参考资料

- [廖雪峰：Python 教程](https://liaoxuefeng.com/books/python/introduction/index.html)
- [Python 3 Tutorial](https://docs.python.org/3/tutorial/)
- [Python Tutorial：控制流](https://docs.python.org/3/tutorial/controlflow.html)
- [Python Tutorial：数据结构](https://docs.python.org/3/tutorial/datastructures.html)
- [Python Tutorial：模块](https://docs.python.org/3/tutorial/modules.html)
- [Python Tutorial：错误与异常](https://docs.python.org/3/tutorial/errors.html)
- [Python Tutorial：类](https://docs.python.org/3/tutorial/classes.html)
- [Python Tutorial：虚拟环境与包](https://docs.python.org/3/tutorial/venv.html)
