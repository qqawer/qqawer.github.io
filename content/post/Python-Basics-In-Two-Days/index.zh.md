---
title: "Python 基础详解：从第一行代码到 API、异常与异步"
description: "一篇适合初学者反复查阅的 Python 基础教程：从解释器、变量、字符串和容器讲到函数、模块、文件、异常、类、venv、pip、HTTP API、类型注解、装饰器与 asyncio。"
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

很多 Python 学习路线的问题，不是内容不够，而是内容太密：刚记住列表，马上遇到生成器；刚会写类，又被元类拦住。学了几天，概念见过不少，真正需要调用一个 API 时还是不知道从哪里下手。

更实用的目标是：**先掌握一条能跑通小项目的最短路径，再让项目暴露知识缺口。**

[廖雪峰的 Python 教程](https://liaoxuefeng.com/books/python/introduction/index.html)面向零基础读者，示例完整、路径平缓；[Python 官方 Tutorial](https://docs.python.org/3/tutorial/)则明确假设读者已经懂一点编程，更适合校准语言细节和 Python 的惯用写法。把两者叠在一起，一条高效路线就很清楚了：

1. 先学数据、分支、循环、函数和异常，获得“能写程序”的能力；
2. 再学模块、虚拟环境、包、HTTP 和 JSON，获得“能做项目”的能力；
3. 最后补类、类型注解、装饰器和异步，获得“能读工程代码”的能力。

{{< figure src="/post/python-basics-in-two-days/01-learning-route.png" alt="小黑推着代码沿 Python 学习路线前进，先经过变量、函数与异常，再接通 API 项目" caption="不要先翻完整本字典：沿着一条可运行的路线，先把小项目接通。" >}}

这篇文章不是章节目录的摘要，而是一份可以反复回来的基础手册。每一部分尽量回答六个问题：它是什么、为什么存在、基本语法怎么写、代码会输出什么、初学者最容易错在哪里，以及它会在真实项目的什么地方出现。

建议第一次按顺序阅读并亲手运行代码；第二次从目录直接跳到忘记的知识点；第三次尝试不看答案完成文末的小项目。看到暂时用不到的进阶内容，可以先理解用途，不必强行背诵。

## 0. 开始之前：解释器、脚本与第一行代码

### 0.1 Python 程序是怎样运行的

我们写下的是 Python 源代码，常见文件扩展名是 `.py`。运行时，Python 解释器读取源码并执行。对初学者来说，可以先把解释器理解成“读懂 Python 语法并让计算机行动的程序”。

在终端输入下面的命令，先确认环境：

```bash
python3 --version
```

如果输出类似 `Python 3.14.1`，说明 Python 3 已经可用。不同系统上的命令可能是 `python3` 或 `python`，后文统一写 `python`；你应使用自己电脑上指向 Python 3 的那个命令。

Python 有两种常用运行方式。

第一种是交互模式（REPL）：

```text
$ python
>>> 1 + 2
3
>>> name = "Ada"
>>> print(name)
Ada
```

`>>>` 是解释器的提示符，不要把它复制进 `.py` 文件。交互模式适合验证一个表达式、查看一个对象，关闭窗口后输入的代码不会自动保存。

第二种是脚本模式。新建 `hello.py`：

```python
name = input("你的名字：")
print(f"你好，{name}！")
```

然后运行：

```bash
python hello.py
```

执行过程可以分成三步：`input()` 等待用户输入并返回字符串；这个字符串被名字 `name` 引用；`print()` 把 f-string 格式化后的结果写到终端。

### 0.2 表达式、语句与注释

表达式会产生一个值，例如 `1 + 2`、`len("Python")`、`age >= 18`。语句执行一种操作，例如赋值、条件判断、循环、导入或函数定义。

```python
price = 20                 # 赋值语句，右侧 20 是表达式
discounted = price * 0.8   # price * 0.8 的结果是 16.0
print(discounted)          # 输出：16.0
```

井号 `#` 后面是单行注释。注释应该解释“为什么这样做”或提醒限制，而不是逐字翻译代码。

```python
timeout = 10  # 防止网络请求无限等待
```

### 0.3 缩进、大小写和命名

Python 对大小写敏感：`name`、`Name` 和 `NAME` 是三个不同名字。常见命名约定是：

| 对象 | 写法 | 示例 |
| --- | --- | --- |
| 变量、函数、模块 | 小写单词加下划线 | `user_name`、`fetch_data()` |
| 类 | 每个单词首字母大写 | `ApiClient` |
| 常量约定 | 全大写加下划线 | `MAX_RETRIES` |

Python 用缩进划分代码块。官方风格通常使用 4 个空格，不要在同一个文件里混用 Tab 和空格。

```python
age = 20

if age >= 18:
    print("成年人")
    print("可以进入")

print("判断结束")
```

前两个 `print()` 属于 `if`，最后一个不属于。缩进不是为了好看，而是语法的一部分。

## 1. 第一层心智模型：名字指向对象

Python 变量没有固定类型，**对象有类型，变量只是指向对象的名字**：

```python
age = 18             # age 指向整数对象 18
age = "eighteen"     # 现在改为指向字符串对象
```

这叫动态类型。它让代码简洁，却不等于“没有类型”。`18 + 1` 合法，`"18" + 1` 会在运行时抛出 `TypeError`。

### 1.1 先认识最常用的基本类型

| 类型 | 含义 | 示例 |
| --- | --- | --- |
| `int` | 整数，大小不局限于 32 位 | `42`、`-7`、`1_000_000` |
| `float` | 浮点数 | `3.14`、`1.5e3` |
| `bool` | 布尔值 | `True`、`False` |
| `str` | 文本字符串 | `"Python"`、`'你好'` |
| `NoneType` | “没有值”这一状态 | `None` |

可以用 `type()` 查看对象类型，用 `isinstance()` 判断对象是否属于某种类型：

```python
age = 18

print(type(age))               # <class 'int'>
print(isinstance(age, int))    # True
print(isinstance(age, str))    # False
```

业务代码中通常更适合用 `isinstance()` 判断，而不是比较 `type(x) == int`，因为前者也能自然处理继承关系。

`bool` 值只有 `True` 和 `False`，首字母必须大写。`None` 也必须大写，它不是空字符串 `""`，不是数字 `0`，也不是字符串 `"None"`。

```python
result = None

if result is None:
    print("结果尚未产生")
```

判断是否为 `None` 时使用 `is None`，这是在判断是不是同一个特殊对象。

### 1.2 数字运算与精度

```python
print(7 + 3)    # 10，加法
print(7 - 3)    # 4，减法
print(7 * 3)    # 21，乘法
print(7 / 3)    # 2.333...，普通除法总是得到浮点数
print(7 // 3)   # 2，向下取整除法
print(7 % 3)    # 1，余数
print(2 ** 3)   # 8，幂
```

下划线可以提高大数字的可读性，`1_000_000` 和 `1000000` 完全相等。

浮点数并不能精确表示所有十进制小数：

```python
print(0.1 + 0.2)  # 可能显示 0.30000000000000004
```

这不是 Python 独有的错误，而是二进制浮点表示的限制。普通显示可以用 `round()`；涉及精确金额时应研究标准库的 `decimal.Decimal`，不要直接把浮点数当作精确货币。

### 1.3 类型转换不是“自动猜测”

`input()` 永远返回字符串。要参与数字运算，需要显式转换：

```python
text = input("年龄：")   # 假设输入 18
age = int(text)
print(age + 1)           # 19
```

常见转换函数包括 `int()`、`float()`、`str()`、`bool()`、`list()`。转换可能失败：`int("十八")` 会抛出 `ValueError`，所以来自用户或网络的数据不能盲目信任。

```python
raw = "3.14"
number = float(raw)
message = "圆周率约为 " + str(number)
```

Python 不会把字符串数字和整数自动相加。显式转换虽然多写几个字符，却能让数据含义更清楚。

### 1.4 `==` 和 `is` 不是一回事

`==` 比较值是否相等，`is` 比较两个名字是否指向同一个对象：

```python
a = [1, 2]
b = [1, 2]
c = a

print(a == b)  # True：内容相同
print(a is b)  # False：是两个不同列表
print(a is c)  # True：指向同一个列表
```

除 `is None`、`is True` 等单例判断外，大多数值比较都应使用 `==`。

更容易踩坑的是可变性：

```python
a = [1, 2]
b = a
b.append(3)

print(a)  # [1, 2, 3]
```

`a` 和 `b` 指向同一个列表对象，修改 `b` 并没有创建新列表。与之相对，整数、字符串和元组通常按不可变对象理解：所谓“修改”，实际是让名字重新指向另一个对象。

如果确实需要一个独立列表，可以创建浅拷贝：

```python
a = [1, 2]
b = a.copy()
b.append(3)

print(a)  # [1, 2]
print(b)  # [1, 2, 3]
```

但浅拷贝只复制最外层容器。若列表内部还有列表，内层对象仍可能共享。遇到嵌套数据时，需要理解 `copy.deepcopy()` 的作用和成本。

{{< figure src="/post/python-basics-in-two-days/02-names-and-objects.png" alt="小黑转动对象转盘，名字 a 和 b 同时指向一个可变列表，而 c 从 42 重新绑定到 43" caption="变量是名字，不是盒子；两个名字可以指向同一个可变对象。" >}}

这个模型还能解释函数参数。官方教程将其描述为：传入的是**对象引用的值**。函数若修改传入的列表，调用方能看到变化；若只给参数名重新赋值，调用方的名字不受影响。

```python
def add_item(items: list[str]) -> None:
    items.append("Python")       # 修改同一个列表


def replace(items: list[str]) -> None:
    items = ["new"]              # 只让局部名字指向新列表
```

这一节的复习问题：

1. `input()` 返回什么类型？
2. `a = b` 会复制对象吗？
3. `==` 和 `is` 分别比较什么？
4. 为什么金额计算不能想当然地使用 `float`？

## 2. 常用数据结构：先学会选，不要只会背

### 2.1 字符串：文本不是字符数组作业

字符串用单引号或双引号包围，两者没有功能差异。字符串本身不可变：所有“修改字符串”的方法都会返回新字符串。

```python
language = "Python"

print(language[0])       # P，第一个字符的索引是 0
print(language[-1])      # n，-1 表示最后一个字符
print(language[0:3])     # Pyt，包含起点，不包含终点
print(language[:2])      # Py，省略起点表示从头开始
print(language[2:])      # thon，省略终点表示直到结尾
print(len(language))     # 6
```

切片的一般形式是 `sequence[start:stop:step]`。`stop` 不包含在结果中，这种“左闭右开”设计使 `text[:3]` 恰好包含 3 个字符。

```python
print("abcdef"[::2])   # ace，每隔一个取一个
print("abcdef"[::-1])  # fedcba，反转字符串
```

常见字符串方法：

```python
raw = "  Python,API,JSON  "

clean = raw.strip()           # 去掉两端空白
parts = clean.split(",")      # ['Python', 'API', 'JSON']
joined = " | ".join(parts)    # Python | API | JSON

print(clean.lower())          # python,api,json
print(clean.startswith("Py"))
print(clean.replace("API", "HTTP API"))
```

注意 `strip()` 不会修改 `raw`，必须接住返回值。`split()` 把一个字符串拆成列表；`join()` 则由分隔符调用，把多个字符串拼起来。

字符串里若包含引号、换行等特殊字符，可以使用转义：

```python
message = "他说：\"你好\"\n然后离开了。"
path = r"data\notes.txt"  # r 前缀创建原始字符串，反斜杠通常不再转义
```

格式化字符串优先使用 f-string：

```python
name = "cpython"
stars = 70_123
ratio = 0.856

print(f"{name} 有 {stars:,} stars")       # cpython 有 70,123 stars
print(f"完成率：{ratio:.1%}")             # 完成率：85.6%
```

大括号中可以放表达式，冒号后是格式说明。初学阶段记住 `:.2f` 保留两位小数、`:,` 添加千位分隔符、`:.1%` 显示百分比就很实用。

### 2.2 四种核心容器怎么选

Python 最常见的容器可以用四个问题区分：

| 类型 | 是否有序 | 是否可变 | 是否允许重复 | 典型用途 |
| --- | --- | --- | --- | --- |
| `list` | 是 | 是 | 是 | 一组会增删、排序的数据 |
| `tuple` | 是 | 否 | 是 | 不希望被改动的一组值 |
| `dict` | 保留插入顺序 | 是 | 键唯一 | 按键查值、表示 JSON 对象 |
| `set` | 不依赖顺序 | 是 | 否 | 去重、成员测试、集合运算 |

这里说 `dict` 保留插入顺序，是指按键加入字典的先后进行迭代；但业务代码不应把字典当成靠数字索引访问的列表。`set` 更不应该依赖显示顺序。

### 2.3 list：最常用的可变序列

```python
languages = ["Python", "JavaScript", "Go"]

print(languages[0])        # Python
languages.append("Rust")  # 在末尾添加一个元素
languages.insert(1, "Java")
languages.remove("Go")    # 按值删除；找不到会报 ValueError
last = languages.pop()     # 删除并返回最后一个元素

print("Python" in languages)  # True
print(len(languages))          # 元素数量
```

需要区分几个相似操作：`append(x)` 把 `x` 当一个元素加入；`extend(iterable)` 把可迭代对象中的每个元素逐一加入；`+` 创建新列表。

```python
items = [1, 2]
items.append([3, 4])
print(items)  # [1, 2, [3, 4]]

items = [1, 2]
items.extend([3, 4])
print(items)  # [1, 2, 3, 4]
```

排序也有两个版本：

```python
scores = [80, 65, 92]

new_scores = sorted(scores, reverse=True)  # 返回新列表
scores.sort()                              # 原地修改，返回 None
```

如果写成 `scores = scores.sort()`，`scores` 会变成 `None`，这是非常常见的初学者错误。

### 2.4 tuple：不可变的有序序列

```python
point = (10, 20)
x, y = point
print(x, y)  # 10 20
```

元组常用于表达位置固定的一组值，或一次返回多个结果。只有一个元素的元组必须写逗号：`single = (42,)`。`(42)` 只是带括号的整数。

“元组不可变”指元组保存的引用位置不能替换；如果某个位置指向列表，列表自身仍可改变：

```python
data = ("tasks", ["read"])
data[1].append("code")
print(data)  # ('tasks', ['read', 'code'])
```

### 2.5 dict：用键找到值

```python
repo = {
    "name": "cpython",
    "stars": 70_000,
    "archived": False,
}

print(repo["name"])                 # cpython
print(repo.get("language"))          # None
print(repo.get("language", "未知"))  # 未知

repo["language"] = "Python"         # 新增或覆盖
stars = repo.pop("stars")            # 删除并返回值
```

`repo["missing"]` 会抛出 `KeyError`；`repo.get("missing")` 返回 `None`。如果字段缺失本身就是数据错误，应使用方括号让程序尽早暴露问题；如果字段确实可选，才使用 `get()` 提供默认值。

字典的键必须是可哈希对象，常用的是字符串、数字、元组；列表不能作为字典键。遍历字典时：

```python
for key in repo:                 # 默认遍历键
    print(key)

for key, value in repo.items(): # 同时获得键和值
    print(key, value)
```

### 2.6 set：去重与快速成员判断

```python
topics = {"python", "api", "python"}
print(topics)  # 重复的 python 只保留一个

topics.add("asyncio")
topics.discard("missing")  # 不存在也不会报错
```

集合运算很适合权限、标签和分组问题：

```python
backend = {"python", "go", "java"}
favorite = {"python", "rust"}

print(backend & favorite)  # 交集：{'python'}
print(backend | favorite)  # 并集
print(backend - favorite)  # 差集：backend 中有但 favorite 中没有
```

空集合必须写 `set()`；`{}` 创建的是空字典。

### 2.7 容器的通用操作

`len()`、`in`、索引、切片、遍历是容器间可以迁移的知识：

```python
names = ["Ada", "Linus", "Guido"]

print(len(names))
print("Guido" in names)
print(names[1:])

for name in names:
    print(name)
```

不要为了获得索引就默认写 `range(len(names))`。只需要元素时直接遍历；同时需要序号时用 `enumerate()`。

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

上面的推导式等价于：

```python
popular_names = []

for repo in repos:
    if repo["stars"] >= 1000:
        popular_names.append(repo["name"])
```

刚开始学习时，先确保能写出普通循环，再学习压缩写法。推导式的目标是清晰，不是比赛谁写得短。

几个高频习惯值得直接记住：

```python
for index, repo in enumerate(repos, start=1):
    print(index, repo["name"])

for name, stars in {"cpython": 70000}.items():
    print(name, stars)

unique_topics = {topic for repo in repos for topic in repo["topics"]}
```

Python 的 `for` 遍历的是可迭代对象，而不是 C 风格的计数器。需要索引时优先考虑 `enumerate()`，同时遍历两个序列时考虑 `zip()`。官方教程还特别提醒：不要一边遍历同一个集合一边修改它；可以遍历副本，或构造一个新集合。

这一节的复习问题：

1. `append()` 与 `extend()` 有什么区别？
2. 为什么 `scores = scores.sort()` 会丢失列表？
3. `dict[key]` 与 `dict.get(key)` 应该怎样选择？
4. 空集合为什么不能写成 `{}`？

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

函数遇到 `return` 会立即结束，因此最后一行不必再写 `else`。这种提前返回能减少嵌套，但前提是每个分支仍然容易理解。

### 3.1 比较运算与逻辑运算

```python
age = 20
has_ticket = True

can_enter = age >= 18 and has_ticket
needs_help = age < 18 or not has_ticket
```

常用比较运算符是 `==`、`!=`、`>`、`>=`、`<`、`<=`；逻辑运算符是 `and`、`or`、`not`。Python 支持链式比较：

```python
score = 85

if 60 <= score < 90:
    print("通过，但未达到优秀")
```

`and` 和 `or` 会短路。`A and B` 在 A 为假时不会计算 B；`A or B` 在 A 为真时不会计算 B。这常被用来保护后续表达式：

```python
users = []

if users and users[0]["active"]:
    print("第一个用户处于活动状态")
```

因为空列表是假值，`users[0]` 不会在列表为空时执行，从而避免 `IndexError`。不过，过长的短路表达式会降低可读性，拆成多个判断通常更好。

### 3.2 `if / elif / else` 只执行一个分支

```python
status_code = 404

if 200 <= status_code < 300:
    message = "成功"
elif status_code == 404:
    message = "资源不存在"
elif status_code >= 500:
    message = "服务器错误"
else:
    message = "其他状态"

print(message)  # 资源不存在
```

解释器从上往下检查条件，执行第一个成立的分支后就离开整组判断。分支顺序因此很重要：先写宽泛条件，可能让后面的具体条件永远无法执行。

### 3.3 `for`、`range()` 与 `while`

`for` 适合“对一批元素逐个处理”：

```python
total = 0

for number in [10, 20, 30]:
    total += number

print(total)  # 60
```

`range(start, stop, step)` 产生一个整数序列，仍然不包含 `stop`：

```python
print(list(range(5)))          # [0, 1, 2, 3, 4]
print(list(range(2, 6)))       # [2, 3, 4, 5]
print(list(range(10, 4, -2)))  # [10, 8, 6]
```

`range()` 返回的是惰性可迭代对象，不会预先创建所有整数；这里用 `list()` 只是为了看清内容。

`while` 适合“不知道具体循环几次，只知道继续条件”：

```python
attempts = 3

while attempts > 0:
    password = input("密码：")
    if password == "python":
        print("登录成功")
        break
    attempts -= 1
else:
    print("尝试次数已用完")
```

循环的 `else` 容易被误解。它不是“条件为假时执行”，而是“循环没有被 `break` 提前终止时执行”。实际项目中可以使用，但如果团队不熟悉这一语法，清晰的标志变量有时更易维护。

### 3.4 `break`、`continue` 与死循环

```python
for number in range(1, 6):
    if number == 2:
        continue  # 跳过本轮剩余代码
    if number == 5:
        break     # 结束整个循环
    print(number)
```

输出为：

```text
1
3
4
```

`while True` 本身并不是错误，但循环体必须存在可靠的 `break`、`return` 或异常出口。初学者写 `while` 时，最好主动检查：循环条件依赖的变量是否真的会更新？

### 3.5 `match / case` 不只是另一个 switch

```python
def describe_event(event: dict) -> str:
    match event:
        case {"type": "message", "text": text}:
            return f"收到消息：{text}"
        case {"type": "error", "code": 404}:
            return "资源不存在"
        case {"type": "error", "code": code} if code >= 500:
            return "服务器错误"
        case _:
            return "未知事件"
```

这里不仅比较固定值，还从字典结构中取出了 `text` 和 `code`。`_` 是兜底通配符。只有当分支确实围绕同一种数据结构展开时，模式匹配才比普通 `if` 更清楚。

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

### 3.6 初学者常见错误

```python
if age = 18:       # 错：= 是赋值，不是比较
    ...

if age == 18:      # 对：== 才是相等比较
    ...
```

不要写 `if x == 1 or 2:`。表达式实际相当于 `(x == 1) or 2`，而 `2` 被视为真，因此条件几乎总成立。正确写法是：

```python
if x == 1 or x == 2:
    ...

if x in {1, 2}:
    ...
```

这一节的复习问题：

1. `range(1, 5)` 包含哪些整数？
2. `continue` 与 `break` 的影响范围有何不同？
3. `while` 为什么容易产生死循环？
4. 循环后的 `else` 在什么情况下执行？

## 4. 函数：把变化关进参数，把结果交给 return

函数不是为了减少几行复制粘贴，而是给一段逻辑划出边界。一个好函数通常有明确输入、单一职责和可预测输出。

### 4.1 定义、调用与返回值

```python
def greet(name: str) -> str:
    message = f"你好，{name}"
    return message


result = greet("Ada")
print(result)  # 你好，Ada
```

`def` 创建函数；`name` 是形参；`"Ada"` 是调用时传入的实参；`return` 把结果交还给调用处。函数只定义不会自动运行，必须写 `greet(...)` 才会调用。

没有显式 `return` 的函数也会返回 `None`：

```python
def show_message(message: str) -> None:
    print(message)


value = show_message("hello")  # 先输出 hello
print(value)                    # 再输出 None
```

因此要区分“打印结果”和“返回结果”。`print()` 面向人显示内容；`return` 让其他代码继续使用结果。可复用函数通常应返回数据，由程序入口决定怎样显示。

### 4.2 位置参数、关键字参数与默认参数

```python
def connect(host: str, port: int = 443, secure: bool = True) -> str:
    scheme = "https" if secure else "http"
    return f"{scheme}://{host}:{port}"


connect("example.com")
connect("example.com", 8080, False)
connect(host="example.com", port=8080, secure=False)
```

位置参数依赖顺序，关键字参数直接写出名字。参数一多，关键字调用通常更易读。带默认值的参数必须放在普通参数之后。

`/` 和 `*` 可以限制调用方式：

```python
def request(path, /, *, timeout=10):
    ...


request("/users", timeout=5)
```

`/` 之前只能按位置传；`*` 之后只能按关键字传。初学阶段不必频繁设计这类接口，但需要在阅读标准库和框架函数签名时认识它们。

### 4.3 `*args` 与 `**kwargs`

```python
def total(*numbers: float) -> float:
    return sum(numbers)


print(total(1, 2, 3))  # 6
```

`*numbers` 收集额外位置参数，函数内部得到元组。`**options` 收集额外关键字参数，函数内部得到字典：

```python
def show_options(**options: object) -> None:
    for key, value in options.items():
        print(key, value)


show_options(timeout=10, verify=True)
```

星号也能反向解包已有容器：

```python
values = [3, 8, 1]
print(max(*values))

options = {"host": "example.com", "port": 8080}
print(connect(**options))
```

不要为了“灵活”让所有函数都接受任意参数。明确的函数签名更容易阅读、补全和检查。

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

### 4.4 作用域：函数里的名字去哪里找

Python 查找名字时，可以先用 LEGB 顺序理解：Local（当前函数）、Enclosing（外层函数）、Global（模块）、Built-in（内置名字）。

```python
tax_rate = 0.1  # 全局名字


def final_price(price: float) -> float:
    discount = 5  # 局部名字
    return price * (1 + tax_rate) - discount
```

函数可以读取全局名字，但在函数里大量修改全局状态会让代码难以测试。优先把依赖作为参数传入，把结果返回。

```python
def final_price(price: float, tax_rate: float, discount: float) -> float:
    return price * (1 + tax_rate) - discount
```

不要把变量命名为 `list`、`str`、`sum`、`id` 等内置名称，否则会遮蔽原有函数：

```python
list = [1, 2]  # 后面再调用 list("abc") 会失败
```

### 4.5 函数也是对象

```python
def double(number: int) -> int:
    return number * 2


operation = double
print(operation(5))  # 10
```

函数可以赋给变量、放进容器、作为参数传给其他函数，也可以由函数返回。这是理解 `sorted(key=...)`、回调、高阶函数和装饰器的基础。

```python
names = ["Guido", "Ada", "Linus"]
print(sorted(names, key=len))  # 按字符串长度排序
```

这里传入的是函数对象 `len`，不是调用结果，所以没有写括号。

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

### 4.6 函数设计检查表

写完函数后可以问：

1. 函数名是否描述动作，例如 `load_users`，而不是模糊的 `handle`？
2. 输入和返回值是否清楚？
3. 是否混合了读取、计算、打印、保存等多个职责？
4. 是否偷偷修改传入的可变对象？如果是，调用者能否看出来？
5. 异常应该在这里处理，还是交给更了解业务的调用者？

练习：编写 `normalize_names(names)`，接收字符串列表，去掉每个名字两端空白、删除空字符串、统一为首字母大写，并返回新列表，不修改原列表。

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

### 5.1 `import` 到底做了什么

假设 `api.py` 中有：

```python
BASE_URL = "https://api.example.com"


def fetch_repos():
    return ["cpython"]
```

可以导入整个模块：

```python
import api

print(api.BASE_URL)
print(api.fetch_repos())
```

也可以从模块导入指定名字：

```python
from api import fetch_repos

print(fetch_repos())
```

第一种写法多一个 `api.` 前缀，却能明确名字来自哪里。避免 `from api import *`，因为它会把许多名字直接塞进当前作用域，容易发生冲突，也让读者无法判断来源。

模块首次导入时，顶层代码会执行。因此可执行入口通常放在下面的判断里：

```python
def main() -> None:
    print("作为脚本运行")


if __name__ == "__main__":
    main()
```

直接执行文件时，特殊变量 `__name__` 的值是 `"__main__"`；被别的模块导入时，值是模块名。这能防止测试或导入函数时意外启动整个程序。

多个模块可以组成包。现代 Python 支持多种包布局，初学时可以先认识传统的 `__init__.py`：

```text
repo_report/
├── main.py
└── report/
    ├── __init__.py
    ├── api.py
    └── formatter.py
```

然后写 `from report.api import fetch_repos`。模块搜索失败时，先检查当前工作目录、文件名、包层级和是否误用了同名文件。例如把自己的文件命名为 `requests.py`，可能会遮蔽真正的第三方 `requests` 包。

### 5.2 标准库、第三方包和自己的模块

这三类来源要分清：

- 标准库随 Python 安装，例如 `json`、`pathlib`、`datetime`、`collections`；
- 第三方包需要安装，例如 `requests`、`pytest`；
- 自己的模块就是项目中的 `.py` 文件。

推荐按这三组排列导入，每组之间空一行：

```python
from pathlib import Path

import requests

from report.formatter import render_report
```

### 5.3 为什么每个项目都需要虚拟环境

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

完整操作顺序可以这样记：

```bash
mkdir repo-report
cd repo-report
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install requests
python -m pip list
```

Windows PowerShell 的激活命令不同，但环境目录仍可叫 `.venv`。离开项目时运行 `deactivate`。虚拟环境通常不提交到 Git，因为体积大且与本机路径相关；应在 `.gitignore` 中加入 `.venv/`，提交依赖说明文件。

`pip freeze` 会记录环境里所有已安装版本，适合简单项目复现：

```text
requests==2.32.5
```

另一台电脑上可以运行：

```bash
python -m pip install -r requirements.txt
```

遇到“明明安装了却还是 `ModuleNotFoundError`”，最常见原因是安装包和运行程序使用了不同解释器。依次检查：

```bash
python -c "import sys; print(sys.executable)"
python -m pip --version
python -m pip show requests
```

这三个路径应该指向同一套环境。

## 6. 文件与 JSON：让数据离开程序后还能存在

### 6.1 用 `with` 打开文件

```python
from pathlib import Path

path = Path("notes.txt")

with path.open("w", encoding="utf-8") as file:
    file.write("Python 基础\n")

with path.open("r", encoding="utf-8") as file:
    content = file.read()

print(content)
```

`"w"` 表示写入，会覆盖已有内容；`"a"` 表示追加；`"r"` 表示读取。文本文件应明确指定 `encoding="utf-8"`，减少跨平台乱码。

`with` 创建上下文，离开代码块时会自动关闭文件，即使中途抛出异常也一样。这比手动调用 `file.close()` 更可靠。

文件很大时，不要一次 `read()` 全部装入内存，可以逐行遍历：

```python
with Path("large.log").open(encoding="utf-8") as file:
    for line in file:
        print(line.rstrip())
```

`pathlib.Path` 把路径表示为对象，拼接路径时比手写斜杠更稳妥：

```python
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
report_path = output_dir / "report.md"
```

### 6.2 JSON 与 Python 对象如何对应

JSON 是文本格式，不是 Python 字典本身。常见对应关系是：

| JSON | Python |
| --- | --- |
| object | `dict` |
| array | `list` |
| string | `str` |
| number | `int` 或 `float` |
| true / false | `True` / `False` |
| null | `None` |

`json.loads()` 从字符串解析，`json.dumps()` 转为字符串；`json.load()` 和 `json.dump()` 则直接处理文件对象。

```python
import json

raw = '{"name": "cpython", "stars": 70000}'
repo = json.loads(raw)
print(repo["name"])  # cpython

text = json.dumps(repo, ensure_ascii=False, indent=2)
print(text)
```

`ensure_ascii=False` 让中文直接显示，`indent=2` 便于人类阅读。

保存到文件：

```python
from pathlib import Path
import json

data = {"language": "Python", "topics": ["API", "asyncio"]}

with Path("data.json").open("w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)
```

JSON 不能直接保存任意 Python 对象，例如 `set`、`Path`、自定义类实例。需要先转换成 JSON 支持的基本结构。

## 7. 调 API：完成第一个真正有用的小项目

HTTP API 可以先理解为一个远程函数：你发送请求，它返回状态码、响应头和响应体。JSON 是常见的响应体格式，对象和数组进入 Python 后通常变成 `dict` 和 `list`。

### 7.1 先看懂一次 HTTP 请求

访问下面的地址：

```text
https://api.github.com/search/repositories?q=language:python&sort=stars
```

可以拆成：

- `https`：通信协议；
- `api.github.com`：主机；
- `/search/repositories`：资源路径；
- `?` 后面的 `q` 和 `sort`：查询参数；
- `GET`：读取资源时常用的 HTTP 方法。

服务端返回状态码。常见分类：

| 范围 | 含义 | 例子 |
| --- | --- | --- |
| 2xx | 请求成功 | `200 OK` |
| 3xx | 重定向 | `301 Moved Permanently` |
| 4xx | 请求方需要修正 | `400 Bad Request`、`404 Not Found`、`429 Too Many Requests` |
| 5xx | 服务端失败 | `500 Internal Server Error`、`503 Service Unavailable` |

“收到了响应”不等于“请求成功”。网络库通常能正常返回一个 `404` 响应对象，因此必须检查状态码。

### 7.2 先写最小请求，再逐步加保护

最小版本：

```python
import requests

response = requests.get("https://api.github.com")
print(response.status_code)
print(response.text[:100])
```

`response.text` 是解码后的文本，`response.content` 是原始字节，`response.json()` 尝试把响应体解析为 JSON。即使服务端声称返回 JSON，内容损坏时解析仍可能失败。

更可靠的版本应使用 `params`、请求头、超时和状态检查：

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

逐行看这段代码：

1. `params` 让 `requests` 负责 URL 编码，不要手动拼接用户输入；
2. `headers` 告诉服务端期望的响应格式；
3. `timeout=10` 限制等待时间，避免程序无限挂起；
4. `raise_for_status()` 遇到 4xx、5xx 时抛出 `HTTPError`；
5. `response.json()` 把响应解析为 Python 对象；
6. `payload["items"][:limit]` 取列表前 `limit` 项；
7. `main()` 负责组织流程，而 `fetch_repos()` 只负责取数据。

运行结果会随 GitHub 实时数据变化，大致类似：

```text
public-apis/public-apis        ⭐ 300000
donnemartin/system-design-primer ⭐ 290000
...
```

### 7.3 把原始 JSON 变成自己的数据

API 返回的字典往往包含几十个字段，业务通常只需要少数几个。越早转换成自己的结构，后续代码越不依赖外部接口细节。

```python
def simplify_repo(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": raw["full_name"],
        "url": raw["html_url"],
        "stars": raw["stargazers_count"],
        "description": raw.get("description") or "暂无描述",
    }
```

`raw.get("description") or "暂无描述"` 同时处理键不存在、值为 `None` 或空字符串的情况。若空字符串在业务上有特殊含义，就不应使用这种简写，而应分别判断。

### 7.4 生成 Markdown 报告

```python
def render_report(repos: list[dict[str, Any]]) -> str:
    lines = ["# Python 热门仓库", ""]

    for index, repo in enumerate(repos, start=1):
        lines.append(f"## {index}. [{repo['name']}]({repo['url']})")
        lines.append("")
        lines.append(f"- Stars：{repo['stars']:,}")
        lines.append(f"- 简介：{repo['description']}")
        lines.append("")

    return "\n".join(lines)
```

这里先把每一行放进列表，最后一次 `join()`，比在循环里不断用 `text += ...` 更容易组织，也避免频繁创建中间字符串。

保存报告：

```python
from pathlib import Path

raw_repos = fetch_repos("python", limit=5)
repos = [simplify_repo(repo) for repo in raw_repos]
report = render_report(repos)
Path("report.md").write_text(report, encoding="utf-8")
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

### 7.5 API 调试清单

请求失败时按顺序检查：

1. URL、HTTP 方法和参数名是否正确；
2. 是否需要认证令牌，令牌是否放在正确请求头；
3. 状态码和响应体说了什么；
4. `Content-Type` 是否真的是 JSON；
5. 返回 JSON 的最外层到底是字典还是列表；
6. 字段是否可选，是否可能为 `null`；
7. 是否触发频率限制；
8. 是否设置了合理超时。

不要把 API 密钥直接写进源码或提交到 Git。真实项目应从环境变量或密钥管理服务读取。

## 8. 异常与调试：报错不是敌人，含糊的失败才是

语法错误意味着代码还不能被解析；异常意味着代码已开始运行，但遇到了无法按当前路径继续处理的情况。`try / except / else / finally` 分别承担不同职责：

### 8.1 先学会读 traceback

例如：

```python
def average(total: float, count: int) -> float:
    return total / count


print(average(100, 0))
```

会得到类似：

```text
Traceback (most recent call last):
  File "demo.py", line 5, in <module>
    print(average(100, 0))
  File "demo.py", line 2, in average
    return total / count
ZeroDivisionError: division by zero
```

阅读顺序：

1. 最后一行说明异常类型和直接原因：除数为零；
2. 从下往上找最靠近错误的自己代码：`return total / count`；
3. 再看它由谁调用、参数从哪里来；
4. 回到数据源修复原因，而不是先把异常藏起来。

常见异常包括：

| 异常 | 常见原因 |
| --- | --- |
| `NameError` | 使用了未定义或拼错的名字 |
| `TypeError` | 类型不支持某操作，或函数参数不匹配 |
| `ValueError` | 类型可以接受，但具体值无效，如 `int("abc")` |
| `KeyError` | 字典中没有这个键 |
| `IndexError` | 序列索引越界 |
| `AttributeError` | 对象没有这个属性或方法 |
| `FileNotFoundError` | 文件路径不存在 |
| `ModuleNotFoundError` | 模块未安装、环境错误或导入路径错误 |

### 8.2 `try / except / else / finally` 的职责

```python
try:
    number = int(input("请输入整数："))
except ValueError as exc:
    print(f"输入无法转换：{exc}")
else:
    print(f"转换成功：{number}")
finally:
    print("本次输入处理结束")
```

- `try` 只放可能失败且需要处理的代码；
- `except` 捕获指定异常；
- `else` 在没有异常时执行；
- `finally` 无论成功、异常甚至提前 `return` 都会执行。

`try` 范围不应包住几十行无关代码，否则无法判断异常究竟来自哪里，也可能意外吞掉本应暴露的程序错误。

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

异常分支从具体到宽泛排列。`requests.Timeout` 也是 `RequestException` 的子类，如果先捕获 `RequestException`，后面的超时分支永远不会到达。

只捕获自己能处理的异常。直接写 `except Exception: pass` 会抹掉现场，让程序表面继续运行、数据却悄悄出错。需要释放文件、网络连接等资源时，优先使用 `with` 上下文管理器；必须无论成功失败都执行的清理，放进 `finally`。

{{< figure src="/post/python-basics-in-two-days/03-exception-routing.png" alt="小黑操作异常分拣机，让正常结果、预期错误与清理动作走向不同出口，并推开吞掉所有错误的黑布" caption="异常处理的目标不是让错误消失，而是把可处理的失败变成明确分支。" >}}

官方 Tutorial 的[错误与异常](https://docs.python.org/3/tutorial/errors.html)章节还覆盖主动 `raise`、异常链、自定义异常和清理动作。初学阶段最重要的是学会读 traceback：**先看最后一行的异常类型和消息，再从下往上找第一处属于自己代码的位置。**

### 8.3 主动抛出异常

函数收到无效输入时，可以立即 `raise`：

```python
def calculate_average(total: float, count: int) -> float:
    if count <= 0:
        raise ValueError("count 必须大于 0")
    return total / count
```

这比返回 `None` 或 `-1` 更明确，因为调用者不会把失败结果误当正常数字继续计算。

业务规则复杂时可以定义自己的异常：

```python
class RateLimitError(Exception):
    """API 调用超过频率限制。"""


def check_status(status_code: int) -> None:
    if status_code == 429:
        raise RateLimitError("请求过于频繁，请稍后重试")
```

捕获底层异常并增加业务语义时，用异常链保留原始原因：

```python
try:
    value = int("not-a-number")
except ValueError as exc:
    raise RuntimeError("配置中的重试次数无效") from exc
```

### 8.4 调试不是到处塞 `print()`

`print()` 适合小程序快速观察，但复杂项目应逐步学会：

- 在编辑器中设置断点，逐行运行并检查变量；
- 使用 `repr(value)` 看清换行、空格等不可见字符；
- 用 `logging` 记录级别、时间和上下文；
- 用最小输入复现问题；
- 写断言或测试固定住预期行为。

```python
def normalize_name(name: str) -> str:
    return name.strip().title()


assert normalize_name("  ada lovelace ") == "Ada Lovelace"
```

`assert` 适合开发阶段检查内部不变量，不应用来校验不可信用户输入；Python 在优化模式下可以跳过断言。

这一节的复习问题：

1. `ValueError` 与 `TypeError` 有什么不同？
2. 为什么应从具体异常捕获到宽泛异常？
3. `else` 和 `finally` 分别何时执行？
4. 什么情况下应该让异常继续向上传播？

## 9. 类与对象：当数据和行为属于同一个概念

不是所有代码都需要类。若只是输入数据、计算结果，一个函数往往更直接。当一组状态和行为需要共同维护时，类才开始有价值。

### 9.1 类、实例、属性与方法

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

调用 `Repo(...)` 时，Python 创建实例并调用 `__init__()` 初始化。`self` 不需要由调用者传入：`repo.is_popular()` 大致相当于 `Repo.is_popular(repo)`。

每个实例有独立的实例属性：

```python
first = Repo("python/cpython", 70_000)
second = Repo("demo/project", 10)

first.stars += 1
print(first.stars)   # 70001
print(second.stars)  # 10
```

类属性则由类定义并被实例共享：

```python
class Repo:
    platform = "GitHub"  # 类属性

    def __init__(self, name: str) -> None:
        self.name = name  # 实例属性
```

不要把可变列表误放成类属性，除非你真的希望所有实例共享它：

```python
class BadRepo:
    tags = []  # 所有实例共享同一个列表，通常不是想要的结果
```

### 9.2 `@dataclass`：主要用于保存数据的类

如果类主要承担数据容器职责，标准库 `dataclasses` 可以自动生成初始化、显示和比较方法：

```python
from dataclasses import dataclass, field


@dataclass
class Repo:
    name: str
    stars: int
    topics: list[str] = field(default_factory=list)

    def is_popular(self, threshold: int = 1_000) -> bool:
        return self.stars >= threshold
```

列表字段使用 `default_factory=list`，原因和函数的可变默认参数相同：每个实例都应获得自己的新列表。

### 9.3 属性约定与 `property`

Python 没有 Java 式的强制私有字段。单下划线 `_token` 表示“这是内部实现，请不要从外部依赖”；双下划线会触发名称改写，但也不是绝对安全边界。

需要在读写属性时验证规则，可以使用 `property`：

```python
class Account:
    def __init__(self, balance: float = 0) -> None:
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("余额不能小于 0")
        self._balance = value
```

外部仍然写 `account.balance = 100`，但赋值会经过检查。不要把每个字段都机械包装成 property；只有需要计算、验证或保持接口兼容时才使用。

### 9.4 继承、多态与组合

```python
class Formatter:
    def render(self, data: list[dict]) -> str:
        raise NotImplementedError


class MarkdownFormatter(Formatter):
    def render(self, data: list[dict]) -> str:
        return "\n".join(item["name"] for item in data)
```

子类继承父类并覆盖方法。多态意味着调用者只依赖共同接口，不必知道具体子类：

```python
def save_report(formatter: Formatter, data: list[dict]) -> None:
    text = formatter.render(data)
    print(text)
```

但很多关系更适合组合：`ReportService` 内部持有一个 `Formatter`，而不是继承它。判断问题可以很朴素：A **是一个** B，可能考虑继承；A **使用一个** B，通常考虑组合。

官方 Tutorial 的[类](https://docs.python.org/3/tutorial/classes.html)章节特别强调名字、对象、作用域和命名空间。理解这些基础，比先背双下划线方法更重要。

这一节的复习问题：

1. 类和实例分别是什么？
2. 类属性与实例属性有什么差异？
3. 为什么 `field(default_factory=list)` 比 `topics=[]` 安全？
4. 什么时候一个函数比类更简单？

## 10. 类型注解：让代码更容易被人和工具理解

类型注解已经在前文出现很多次：

```python
def find_repo(name: str, repos: list[Repo]) -> Repo | None:
    for repo in repos:
        if repo.name == name:
            return repo
    return None
```

`Repo | None` 表示可能返回仓库，也可能没有结果。调用者必须处理空值：

```python
repo = find_repo("python/cpython", repos)

if repo is None:
    print("没有找到")
else:
    print(repo.stars)
```

常见类型写法：

```python
names: list[str] = ["Ada", "Guido"]
scores: dict[str, int] = {"Ada": 100}
point: tuple[int, int] = (10, 20)
identifier: int | str = "user-42"
```

类型注解不会自动阻止错误值进入函数。运行时校验、静态类型检查和测试是不同层次的工具，不能互相替代。类型也不宜写得过度复杂；如果一条注解比函数主体还难懂，应考虑拆分结构或定义清晰的数据类。

## 11. 装饰器：不改函数正文，给调用包一层行为

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

### 11.1 从最简单的包装开始

```python
def announce(func):
    def wrapper():
        print("函数开始")
        result = func()
        print("函数结束")
        return result

    return wrapper


@announce
def hello():
    print("Hello")
```

调用 `hello()` 时，实际调用的是 `wrapper()`。包装器必须把原函数的返回值交还，否则被装饰函数会悄悄变成返回 `None`。

通用装饰器使用 `*args` 和 `**kwargs` 转发参数，并用 `functools.wraps` 保留原函数的名称、文档等元数据。上面的计时版本已经展示了这两个要点。

### 11.2 带参数的装饰器为什么多一层

```python
from functools import wraps


def repeat(times: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(3)
def say_hi():
    print("hi")
```

`@repeat(3)` 先调用 `repeat(3)` 得到真正的装饰器，再把 `say_hi` 交给它。刚学习时把每一层的输入和输出写在纸上，比死记模板有效。

## 12. 可迭代对象、迭代器与生成器

前文的字符串、列表、字典、集合以及 `range()` 都能被 `for` 遍历，因此都是可迭代对象（iterable）。`for` 循环背后会先取得迭代器，再不断请求下一个值，直到收到结束信号。

```python
names = ["Ada", "Guido"]
iterator = iter(names)

print(next(iterator))  # Ada
print(next(iterator))  # Guido
```

继续调用 `next()` 会抛出 `StopIteration`，`for` 循环会替我们处理这个结束信号。

生成器是一种按需产生值的迭代器。函数中出现 `yield` 后，调用函数不会一次执行到底，而是返回生成器对象：

```python
def count_up_to(limit: int):
    number = 1
    while number <= limit:
        yield number
        number += 1


for number in count_up_to(3):
    print(number)
```

输出：

```text
1
2
3
```

每次 `yield` 交出一个值并暂停，下一次迭代再从暂停处继续。这样处理大量数据时不必先把所有结果放进列表。

```python
squares = (number * number for number in range(1_000_000))
first_three = [next(squares) for _ in range(3)]
```

圆括号形式是生成器表达式，方括号形式是列表推导式。生成器节省内存，但通常只能消费一次，也不能像列表那样随意按索引访问。数据量很小、需要重复遍历时，列表往往更简单。

## 13. asyncio：优化等待，不是让 CPU 突然变快

同步代码一次等待一个请求，写法直观，通常应该先从它开始。当程序需要同时等待许多网络请求时，`asyncio` 可以在一个任务等待 I/O 的间隙推进其他任务。

### 13.1 同步、并发与并行

- **同步**：当前步骤完成后才进入下一步；
- **并发**：多个任务在同一时间段内交替推进；
- **并行**：多个任务在同一时刻真正同时运行。

`asyncio` 主要提供单线程协作式并发。协程只有执行到 `await` 并等待可等待操作时，事件循环才有机会切换任务；它不会随时强行打断普通 Python 代码。

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

如果每个模拟请求等待 1 秒，顺序等待三次大约需要 3 秒；`gather()` 并发等待大约需要 1 秒多一点，因为三段等待重叠了。减少的是总等待时间，不是让单次操作变快。

顺序版本是：

```python
async def sequential() -> list[str]:
    results = []
    results.append(await fetch_one("A"))
    results.append(await fetch_one("B"))
    results.append(await fetch_one("C"))
    return results
```

### 13.2 协程函数、协程对象和任务不要混淆

```python
async def work() -> int:
    await asyncio.sleep(1)
    return 42


coroutine = work()               # 创建协程对象，还没有得到结果
result = await coroutine         # 驱动协程执行并等待结果
task = asyncio.create_task(work())  # 调度为任务，可与其他任务并发推进
```

在普通脚本顶层不能直接写 `await`，通常由 `asyncio.run(main())` 创建并管理事件循环。在已经有事件循环的环境（如部分 Notebook 或异步框架）中，再调用 `asyncio.run()` 可能报错，应遵循宿主环境的入口方式。

### 13.3 异步中的异常与取消

`await` 的协程抛出异常时，异常会传播到等待它的调用者。`gather()` 中任何任务失败时，不能想当然地认为其他外部操作都被回滚；网络请求、文件写入等副作用需要单独设计一致性和清理。

```python
async def main() -> None:
    try:
        results = await asyncio.wait_for(
            asyncio.gather(fetch_one("A"), fetch_one("B")),
            timeout=2,
        )
        print(results)
    except TimeoutError:
        print("整组任务超时")
```

真实程序还要考虑单个请求超时、任务取消、重试次数和并发上限。并发越高不一定越快：可能压垮本机连接池、触发远端限流，或让错误同时爆发。

### 13.4 不要在异步函数里塞阻塞调用

下面的代码虽然写在 `async def` 里，仍会阻塞事件循环：

```python
import time


async def bad_example() -> None:
    time.sleep(5)  # 阻塞整个线程，没有让出控制权
```

模拟等待应使用 `await asyncio.sleep(5)`；HTTP 请求则选择原生异步客户端。`requests.get()` 是同步调用，直接放进协程不会自动变成异步。

{{< figure src="/post/python-basics-in-two-days/04-sync-vs-async.png" alt="同步场景中小黑守着一只水壶等待，异步场景中小黑在多只水壶等待期间切换任务" caption="异步不会让一壶水烧得更快；它让等待期间的服务员不必站着发呆。" >}}

异步适合大量 I/O 等待，不适合直接解决 CPU 密集计算。也不要在协程里调用会长时间阻塞的同步库，否则整个事件循环仍会被卡住。廖雪峰的[协程与异步 I/O](https://liaoxuefeng.com/books/python/async-io/coroutine/index.html)可以帮助建立直觉，但真实 HTTP 项目还需要选择支持异步的客户端，并学习超时、取消、并发上限和错误传播。

这一节的复习问题：

1. 并发与并行是什么关系？
2. 调用协程函数后为什么没有立刻得到结果？
3. `await` 在等待期间把控制权交给了谁？
4. 为什么在协程里调用 `requests.get()` 仍可能卡住事件循环？

## 14. 测试：把“这次能跑”变成“以后也能跑”

最简单的测试就是准备输入并断言输出：

```python
def level(stars: int) -> str:
    if stars >= 10_000:
        return "popular"
    if stars >= 1_000:
        return "growing"
    return "small"


def test_level() -> None:
    assert level(999) == "small"
    assert level(1_000) == "growing"
    assert level(9_999) == "growing"
    assert level(10_000) == "popular"
```

边界值最值得测试，因为分支错误经常发生在 `999/1000`、空列表、第一个元素、最后一个元素这类位置。

安装并运行 `pytest`：

```bash
python -m pip install pytest
python -m pytest
```

纯计算函数容易测试；把网络请求、文件写入和 `input()` 全塞进同一个函数则很难测试。这也是为什么前文反复建议拆成“获取数据、转换数据、渲染文本、保存文件”几层。

不要让基础测试依赖真实 GitHub API，否则网络波动、频率限制和实时数据变化都会导致不稳定。可以把一小段固定 JSON 当作输入，测试 `simplify_repo()` 与 `render_report()`。

```python
def test_simplify_repo() -> None:
    raw = {
        "full_name": "python/cpython",
        "html_url": "https://github.com/python/cpython",
        "stargazers_count": 70_000,
        "description": None,
    }

    result = simplify_repo(raw)

    assert result["name"] == "python/cpython"
    assert result["description"] == "暂无描述"
```

## 15. 把所有知识拼成一个完整项目

最终目录：

```text
repo-report/
├── .gitignore
├── requirements.txt
├── main.py
├── api.py
├── formatter.py
└── tests/
    └── test_formatter.py
```

各文件只承担一种职责：

- `api.py`：发送 HTTP 请求，返回原始数据；
- `formatter.py`：转换数据并生成 Markdown；
- `main.py`：读取参数、组织流程、处理用户可理解的错误；
- `tests/`：用固定输入检查转换和渲染逻辑。

`main.py` 可以这样组织：

```python
from pathlib import Path

import requests

from api import fetch_repos
from formatter import render_report, simplify_repo


def main() -> None:
    language = input("编程语言（默认 Python）：").strip() or "Python"

    try:
        raw_repos = fetch_repos(language, limit=5)
    except requests.Timeout:
        print("请求超时，请检查网络后重试")
        return
    except requests.RequestException as exc:
        print(f"请求失败：{exc}")
        return

    repos = [simplify_repo(repo) for repo in raw_repos]
    report = render_report(repos)
    output = Path("report.md")
    output.write_text(report, encoding="utf-8")
    print(f"已生成：{output.resolve()}")


if __name__ == "__main__":
    main()
```

这个入口故意保持同步，因为五个结果只需要一次 HTTP 请求。不要为了练习异步而把不需要并发的程序复杂化。等需求变成“同时查询十种语言”时，再考虑异步客户端和并发限制。

## 16. 两天学习安排：以输出物验收

### 第一天：写出同步版本

上午依次完成：

1. 在 REPL 中练习数字、字符串、类型转换；
2. 用列表和字典保存三条仓库数据；
3. 用 `if` 按 star 数分级；
4. 用 `for` 输出每条数据；
5. 把筛选和渲染拆成函数。

下午学习模块、异常、文件与 JSON，并完成：

```text
输入关键词 → 调用一个公开 API → 筛选结果 → 输出 Markdown 报告
```

当天的验收标准不是“看完多少章”，而是：能独立写一个函数，能解释参数和返回值，遇到异常能读 traceback，知道数据为什么是 `list` 或 `dict`。

### 第二天：把脚本整理成项目

上午从空目录创建 `venv`，安装 `requests`，把代码拆成三个模块，完成 GitHub API 报告。下午给核心函数加类型注解，写 `pytest` 测试，再分别尝试数据类、计时装饰器和三个模拟异步请求。

当天的验收标准是：能从空目录创建环境并运行项目，能解释 `import`、JSON 解析、异常分支和 `await` 分别解决什么问题。

两天不是“精通 Python”的承诺，而是第一次建立完整闭环。之后应重复修改这个项目：加入命令行参数、缓存结果、增加测试、替换 API。每次只引入一个新概念。

## 17. 高频复习卡：忘记时直接回来查

| 忘记的问题 | 快速答案 |
| --- | --- |
| 用户输入是什么类型？ | `input()` 总是返回 `str` |
| 如何判断没有值？ | `value is None` |
| 列表末尾添加一个元素？ | `items.append(value)` |
| 列表加入另一批元素？ | `items.extend(values)` |
| 安全读取可选字典键？ | `data.get(key, default)` |
| 同时遍历序号和元素？ | `enumerate(items, start=1)` |
| 同时遍历两个序列？ | `zip(a, b)` |
| 函数没有 `return` 会怎样？ | 返回 `None` |
| 为什么不用列表作默认参数？ | 默认值只创建一次，会被多次调用共享 |
| 如何处理文件后自动关闭？ | `with ... as ...` |
| 字符串解析 JSON？ | `json.loads(text)` |
| Python 对象变 JSON 字符串？ | `json.dumps(data)` |
| 为什么写 `python -m pip`？ | 保证使用当前解释器对应的 pip |
| 怎样检查 HTTP 失败状态？ | `response.raise_for_status()` |
| 类型注解会自动校验吗？ | 默认不会 |
| `yield` 做什么？ | 逐个产生值并保存暂停位置 |
| `await` 做什么？ | 等待可等待对象，并把控制权交回事件循环 |

## 18. 真正需要记住的，不是语法清单

Python 基础可以压缩成四个动作：

1. 用对象和容器表示数据；
2. 用控制流和函数组织变化；
3. 用模块、环境和包连接外部能力；
4. 用异常、类型与测试守住边界。

类、装饰器和异步不是另一门语言，只是这四个动作在更大代码里的延伸。学到能写函数、能调 API、能看懂报错时，就应该开始做项目。项目会非常诚实地告诉你下一章该读什么。

最后给初学者一个判断标准：如果你能不看答案写出“读取输入 → 调 API → 检查错误 → 解析 JSON → 筛选数据 → 保存文件”，并能解释每一行为什么存在，那么基础已经形成了。忘记具体方法名很正常，知道问题属于哪一层、应该去哪里查，比背完整个标准库重要得多。

## 参考资料

- [廖雪峰：Python 教程](https://liaoxuefeng.com/books/python/introduction/index.html)
- [Python 3 Tutorial](https://docs.python.org/3/tutorial/)
- [Python Tutorial：控制流](https://docs.python.org/3/tutorial/controlflow.html)
- [Python Tutorial：数据结构](https://docs.python.org/3/tutorial/datastructures.html)
- [Python Tutorial：模块](https://docs.python.org/3/tutorial/modules.html)
- [Python Tutorial：错误与异常](https://docs.python.org/3/tutorial/errors.html)
- [Python Tutorial：类](https://docs.python.org/3/tutorial/classes.html)
- [Python Tutorial：虚拟环境与包](https://docs.python.org/3/tutorial/venv.html)
