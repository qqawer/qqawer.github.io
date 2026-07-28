---
title: "LeetCode 题解手记：从思路到复盘"
description: "持续记录 LeetCode 刷题过程中的原始思路、优化过程、关键不变量、复杂度分析和易错点。专题一：哈希与双指针。"
date: 2026-07-28
slug: "leetcode-solution-notes"
categories:
    - Programming
tags:
    - LeetCode
    - Algorithm
    - Hash Table
    - Two Pointers
    - Go
math: true
toc: true
---

这不是一份只收集“标准答案”的题解，而是一份持续更新的刷题手记。

每道题会尽量保留从直觉解法到优化解法的完整过程：最初为什么这样想、原方案慢在哪里、优化的突破口是什么，以及下次遇到什么信号时应该想到同类方法。

<!--more-->

## 使用方式

每做完一道题，按下面的顺序复盘：

1. 先用自己的话重述题意和约束。
2. 记录第一反应，即使它只是暴力解法。
3. 写出代码，并分析时间、空间复杂度。
4. 找出重复工作或没有利用的题目条件。
5. 写出优化方案和关键不变量。
6. 记录错误案例与可以迁移到其他题目的规律。
7. 隔几天不看答案，再独立实现一次。

> 本文中的“我的思路”是复盘草稿。以后重做题目时，应继续补充当时真正卡住的地方，而不只是留下最终代码。

## Go 刷题语法速查

### 1. `var`、`:=` 与常量

```go
var count int          // 0
var ok bool            // false
var name string        // ""
var nums []int         // nil
var index map[int]int  // nil，不能直接写入

var left, right int = 0, 10
answer := 42           // 自动推断为 int；只能在函数内部使用
const mod = 1_000_000_007
```

记忆：

- `var 变量名 类型`：先声明，自动取得该类型的零值。
- `变量名 := 值`：声明并初始化，只能写在函数内部。
- `=`：给已经存在的变量赋值。
- `const`：声明编译期常量。

```go
x := 1
x = 2   // 正确：重新赋值
// x := 2 // 错误：同一作用域没有新变量

x, y := 3, 4 // 至少有一个左侧变量是新变量时，可以使用 :=
x, z := 5, 6 // 正确：z 是新变量
```

### 2. 数组、切片与 Map 的创建

```go
// 数组：[长度]类型，长度固定且属于类型的一部分
var a [3]int               // [0, 0, 0]
b := [3]int{1, 2, 3}

// 切片：[]类型，长度可变
var nilSlice []int         // nil，len == 0，可以 append
empty := []int{}           // 非 nil 空切片
nums := []int{1, 2, 3}
nums = append(nums, 4)

// Map：map[键类型]值类型
var nilMap map[int]int     // nil，可以读取，不能写入
index := map[int]int{}     // 非 nil 空 Map，可以写入
index[7] = 1
```

### 3. `make`：创建切片、Map 和 Channel

`make` 只用于 `slice`、`map` 和 `channel`；刷题最常用前两种。

```go
// make([]T, length)
nums := make([]int, 5)      // len=5，内容为 [0,0,0,0,0]
nums[0] = 10

// make([]T, length, capacity)
result := make([]int, 0, 5) // len=0，cap=5；用 append 添加元素
result = append(result, 10)

// make(map[K]V)
count := make(map[int]int)
count[3]++

// 可选容量提示；不是长度限制
seen := make(map[string]bool, 100)
```

最容易混淆的地方：

```go
a := make([]int, 3)
a = append(a, 9) // [0,0,0,9]，不是 [9]

b := make([]int, 0, 3)
b = append(b, 9) // [9]
```

- 已知最终要按下标写入：`make([]int, n)`。
- 从空结果不断追加：`make([]int, 0, n)`。
- Map 必须用字面量 `{}` 或 `make` 初始化后才能写入。

`new(T)` 返回 `*T`，即指向 `T` 零值的指针；普通刷题很少需要：

```go
p := new(int) // 类型是 *int，*p == 0
*p = 7
```

### 4. `for` 的常用写法

Go 只有 `for`，但可以写成不同形式：

```go
// 经典三段式
for i := 0; i < n; i++ {
}

// 类似 while
for left < right {
    left++
}

// 无限循环
for {
    if done {
        break
    }
}
```

`continue` 跳过本轮，`break` 结束当前循环。

### 5. `for range` 遍历

#### 切片与数组

```go
nums := []int{10, 20, 30}

for i, v := range nums { // i: int 下标；v: int 元素副本
    fmt.Println(i, v)
}

for i := range nums {    // 只要下标
    nums[i] *= 2          // 修改原切片必须通过 nums[i]
}

for _, v := range nums { // 只要值
    fmt.Println(v)
}
```

`v` 是元素的副本，修改它不会修改原切片：

```go
for _, v := range nums {
    v = 0 // nums 不变
}
```

#### Map

```go
count := map[string]int{"go": 2, "java": 1}

for key, value := range count {
    fmt.Println(key, value)
}

for key := range count {
    delete(count, key)
}
```

Map 的遍历顺序不固定，不能依赖输出顺序。

#### 字符串：下标是字节位置，值是 `rune`

这是 `range string` 最特殊、也最容易忘记的地方：

```go
s := "A中B"

for i, r := range s {
    fmt.Printf("i=%d r=%c\n", i, r)
}
// i=0 r=A
// i=1 r=中
// i=4 r=B
```

`"中"` 的 UTF-8 编码占 3 个字节，所以索引从 `1` 跳到 `4`：

- `i` 的类型是 `int`，表示当前字符 UTF-8 编码的**起始字节下标**。
- `r` 的类型是 `rune`，表示解码后的 Unicode 码点。
- `len(s)` 返回**字节数**，不是字符数。

```go
s := "A中B"
fmt.Println(len(s))         // 5：字节数
fmt.Println(len([]rune(s))) // 3：rune 数

fmt.Printf("%x\n", s[1])       // e4：只取到“中”的第一个字节
fmt.Printf("%c\n", []rune(s)[1]) // 中
```

选择方式：

- 题目明确只有小写英文字母：使用 `s[i]` 和 `byte`，简单高效。
- 可能包含中文或其他 Unicode 字符：使用 `for _, r := range s` 或先转为 `[]rune`。

#### `range` 中常见类型

| 被遍历对象 | 第一个值 | 第二个值 |
|---|---|---|
| 数组、切片 | `int` 下标 | 元素副本 |
| 字符串 | `int` 字节下标 | `rune` |
| Map | key | value |
| Channel | 接收到的元素 | 无 |

## Go 刷题常用包速查

刷题不必记住标准库的所有 API。下面这些方法覆盖了大部分字符串、数字转换、排序和字符判断场景。

```go
import (
    "slices"
    "sort"
    "strconv"
    "strings"
    "unicode"
)
```

### 1. `strings`：处理字符串

| 方法签名 | 输入 → 输出 | 作用 |
|---|---|---|
| `HasPrefix(s, prefix string) bool` | `string, string → bool` | 是否以指定前缀开头 |
| `HasSuffix(s, suffix string) bool` | `string, string → bool` | 是否以指定后缀结尾 |
| `Index(s, substr string) int` | `string, string → int` | 首次出现位置；不存在返回 `-1` |
| `LastIndex(s, substr string) int` | `string, string → int` | 最后一次出现位置；不存在返回 `-1` |
| `Replace(s, old, new string, n int) string` | `string, string, string, int → string` | 替换前 `n` 个匹配；`n < 0` 表示全部 |
| `ReplaceAll(s, old, new string) string` | `string, string, string → string` | 替换全部匹配 |
| `Count(s, substr string) int` | `string, string → int` | 统计不重叠匹配次数 |
| `Repeat(s string, count int) string` | `string, int → string` | 重复字符串 `count` 次 |
| `ToLower(s string) string` | `string → string` | 转为小写 |
| `ToUpper(s string) string` | `string → string` | 转为大写 |
| `TrimSpace(s string) string` | `string → string` | 删除首尾 Unicode 空白 |
| `Trim(s, cutset string) string` | `string, string → string` | 删除首尾所有属于 `cutset` 的字符 |
| `TrimLeft(s, cutset string) string` | `string, string → string` | 只清理左侧 `cutset` 字符 |
| `TrimRight(s, cutset string) string` | `string, string → string` | 只清理右侧 `cutset` 字符 |
| `Split(s, sep string) []string` | `string, string → []string` | 按分隔符拆分全部 |
| `SplitN(s, sep string, n int) []string` | `string, string, int → []string` | 最多拆成 `n` 段；`n < 0` 表示不限 |
| `Join(elems []string, sep string) string` | `[]string, string → string` | 用分隔符连接 |
| `Contains(s, substr string) bool` | `string, string → bool` | 是否包含子串 |
| `ContainsAny(s, chars string) bool` | `string, string → bool` | 是否包含 `chars` 中任意字符 |
| `Fields(s string) []string` | `string → []string` | 按连续空白分词 |

```go
s := "  go,java,python  "
s = strings.TrimSpace(s)            // "go,java,python"
langs := strings.Split(s, ",")      // []string{"go", "java", "python"}
joined := strings.Join(langs, "-")  // "go-java-python"

words := strings.Fields("I  love\tGo") // []string{"I", "love", "Go"}
hasGo := strings.Contains(joined, "go") // true
pos := strings.Index(joined, "java")    // 3

strings.HasPrefix("leetcode", "leet")       // true
strings.HasSuffix("main.go", ".go")         // true
strings.LastIndex("go gopher go", "go")     // 10
strings.Replace("a-a-a", "a", "x", 2)       // "x-x-a"
strings.Repeat("ab", 3)                     // "ababab"
strings.Trim("--go--", "-")                  // "go"
strings.TrimLeft("--go--", "-")              // "go--"
strings.SplitN("a,b,c", ",", 2)              // []string{"a", "b,c"}
strings.ContainsAny("team", "xyzm")          // true，因为包含 m
```

注意：

- Go 字符串不可原地修改；这些方法通常返回新字符串。
- `strings.Split("", ",")` 返回包含一个空字符串的切片；按空白分词时优先使用 `Fields`。
- 逐个处理 ASCII 字符可使用 `s[i]`；处理中文等 Unicode 字符应使用 `for _, r := range s`。

### 2. `strconv`：字符串与数字互转

| 方法签名 | 输入 → 输出 | 作用 |
|---|---|---|
| `Atoi(s string) (int, error)` | `string → int, error` | 十进制字符串转 `int` |
| `Itoa(i int) string` | `int → string` | `int` 转十进制字符串 |
| `ParseInt(s string, base, bitSize int) (int64, error)` | `string, int, int → int64, error` | 按指定进制解析有符号整数 |
| `ParseFloat(s string, bitSize int) (float64, error)` | `string, int → float64, error` | 字符串转浮点数 |
| `FormatInt(i int64, base int) string` | `int64, int → string` | 整数按指定进制转字符串 |

```go
n, err := strconv.Atoi("123")
if err != nil {
    // 输入不是合法整数
}
fmt.Println(n + 1) // 124

s := strconv.Itoa(-42) // "-42"

binary, _ := strconv.ParseInt("1011", 2, 64) // 11
hex := strconv.FormatInt(255, 16)            // "ff"
```

记忆方式：

- `Atoi`：ASCII to integer。
- `Itoa`：integer to ASCII。
- `Parse...`：字符串转数值，返回“结果 + error”。
- `Format...`：数值转字符串。

刷题时即使题目保证输入合法，也要知道 `Atoi` 和 `ParseInt` 会返回错误；工程代码不要直接忽略 `err`。

### 3. `sort`：排序与二分定位

| 方法签名 | 输入 → 输出 | 作用 |
|---|---|---|
| `Ints(x []int)` | `[]int → 无返回值` | 原地升序排列整数 |
| `Float64s(x []float64)` | `[]float64 → 无返回值` | 原地升序排列浮点数 |
| `Strings(x []string)` | `[]string → 无返回值` | 原地按字典序升序排列字符串 |
| `Slice(x any, less func(i, j int) bool)` | `切片, 比较函数 → 无返回值` | 按自定义规则原地排序 |
| `Search(n int, f func(int) bool) int` | `int, func(int) bool → int` | 返回 `[0,n)` 中第一个使 `f(i)` 为真的位置；没有则返回 `n` |
| `SearchInts(a []int, x int) int` | `[]int, int → int` | 在升序切片中返回第一个 `>= x` 的位置 |

这些排序方法会**直接修改原切片**：

```go
nums := []int{4, 1, 3, 2}
sort.Ints(nums) // nums = []int{1, 2, 3, 4}

scores := []float64{3.1, 1.5, 2.7}
sort.Float64s(scores) // []float64{1.5, 2.7, 3.1}

words := []string{"go", "apple", "java"}
sort.Strings(words) // []string{"apple", "go", "java"}

// 降序排序
sort.Slice(nums, func(i, j int) bool {
    return nums[i] > nums[j]
})

type Pair struct {
    Value int
    Index int
}

pairs := []Pair{{3, 0}, {1, 1}, {3, 2}}
sort.Slice(pairs, func(i, j int) bool {
    if pairs[i].Value == pairs[j].Value {
        return pairs[i].Index < pairs[j].Index // 次关键字
    }
    return pairs[i].Value < pairs[j].Value // 主关键字
})
```

二分定位：

```go
nums := []int{1, 3, 3, 7}

i := sort.SearchInts(nums, 3) // 1：第一个 >= 3 的位置
j := sort.SearchInts(nums, 5) // 3：5 不存在时的插入位置

// 第一个平方不小于 30 的非负整数
x := sort.Search(30, func(i int) bool {
    return i*i >= 30
}) // 6
```

关键点：`sort.Search` 要求条件具有单调性，即结果形如 `false false ... true true`。

### 4. `unicode`：判断和转换字符

`unicode` 处理的是 `rune`，适合字母、数字、空白和大小写判断，也能正确处理非 ASCII 字符。

| 方法签名 | 输入 → 输出 | 作用 |
|---|---|---|
| `IsDigit(r rune) bool` | `rune → bool` | 是否为 Unicode 十进制数字 |
| `IsLetter(r rune) bool` | `rune → bool` | 是否为 Unicode 字母 |
| `IsLower(r rune) bool` | `rune → bool` | 是否为小写字母 |
| `IsUpper(r rune) bool` | `rune → bool` | 是否为大写字母 |
| `IsNumber(r rune) bool` | `rune → bool` | 是否为 Unicode 数字，范围比 `IsDigit` 更广 |
| `IsSpace(r rune) bool` | `rune → bool` | 是否为空白字符 |
| `ToLower(r rune) rune` | `rune → rune` | 转为小写字符 |
| `ToUpper(r rune) rune` | `rune → rune` | 转为大写字符 |

```go
for _, r := range "Go语言 123" {
    switch {
    case unicode.IsLetter(r):
        fmt.Printf("%c 是字母\n", r)
    case unicode.IsDigit(r):
        fmt.Printf("%c 是数字\n", r)
    case unicode.IsSpace(r):
        fmt.Println("遇到空白")
    }
}

lower := unicode.ToLower('G') // 'g'
```

常见模板：只保留字母和数字，并忽略大小写。

```go
func normalize(s string) []rune {
    result := make([]rune, 0, len(s))
    for _, r := range s {
        if unicode.IsLetter(r) || unicode.IsDigit(r) {
            result = append(result, unicode.ToLower(r))
        }
    }
    return result
}
```

注意：`byte` 是一个字节，`rune` 是一个 Unicode 码点。涉及中文时，不要用 `s[i]` 把一个字节误当成一个完整字符。

### 5. `slices`：通用切片工具

`slices` 从 Go 1.21 起进入标准库，常用方法支持整数、字符串以及其他切片类型。

表中的 `E` 表示元素类型，`S` 表示形如 `[]E` 的切片类型。

| 方法签名（简化） | 输入 → 输出 | 作用 |
|---|---|---|
| `Max(x S) E` | `[]E → E` | 返回最大元素；空切片会 panic |
| `Min(x S) E` | `[]E → E` | 返回最小元素；空切片会 panic |
| `Index(s S, v E) int` | `[]E, E → int` | 首次出现位置；不存在返回 `-1` |
| `Contains(s S, v E) bool` | `[]E, E → bool` | 判断元素是否存在 |
| `BinarySearch(x S, target E) (int, bool)` | `有序 []E, E → int, bool` | 返回匹配位置或插入位置，以及是否找到 |
| `Clone(s S) S` | `[]E → []E` | 浅拷贝切片 |
| `Delete(s S, i, j int) S` | `[]E, int, int → []E` | 删除半开区间 `[i,j)`，必须接收返回值 |
| `Sort(x S)` | `[]E → 无返回值` | 原地升序排序 |
| `Reverse(s S)` | `[]E → 无返回值` | 原地反转 |
| `IsSorted(x S) bool` | `[]E → bool` | 是否按升序排列 |
| `Concat(slices ...S) S` | `多个 []E → []E` | 连接多个切片并返回新切片 |
| `Grow(s S, n int) S` | `[]E, int → []E` | 保证还能追加至少 `n` 个元素而不重新分配 |
| `Insert(s S, i int, v ...E) S` | `[]E, int, 若干 E → []E` | 在下标 `i` 前插入元素 |
| `Equal(s1, s2 S) bool` | `[]E, []E → bool` | 长度和对应元素是否都相等 |
| `Compare(s1, s2 S) int` | `[]E, []E → int` | 字典序比较，返回负数、`0` 或正数 |
| `Compact(s S) S` | `[]E → []E` | 合并连续重复元素 |
| `CompactFunc(s S, eq func(E, E) bool) S` | `[]E, 相等函数 → []E` | 按自定义相等规则合并连续元素 |
| `SortFunc(x S, cmp func(E, E) int)` | `[]E, 比较函数 → 无返回值` | 按比较函数原地排序 |

> `slices` 包中没有 `Cut`。如果你想“切片”，直接使用 `s[i:j]`；如果你想删除一段，使用 `slices.Delete(s, i, j)`。`strings.Cut` 才是按分隔符把字符串切成前后两部分的方法。

```go
nums := []int{3, 1, 2, 2}
copyNums := slices.Clone(nums) // 修改副本不会影响 nums

slices.Sort(copyNums)          // []int{1, 2, 2, 3}
copyNums = slices.Compact(copyNums) // []int{1, 2, 3}
slices.Reverse(copyNums)       // []int{3, 2, 1}

hasTwo := slices.Contains(copyNums, 2) // true
pos := slices.Index(copyNums, 2)       // 1
largest := slices.Max(copyNums)        // 3
smallest := slices.Min(copyNums)       // 1
same := slices.Equal(nums, copyNums)   // false
```

删除、插入、连接和预分配：

```go
nums := []int{1, 2, 3, 4}
nums = slices.Delete(nums, 1, 3) // []int{1, 4}，删除 [1,3)
nums = slices.Insert(nums, 1, 9) // []int{1, 9, 4}
nums = slices.Grow(nums, 10)     // len 不变，保证额外容量

all := slices.Concat([]int{1, 2}, []int{3}, []int{4, 5})
// []int{1, 2, 3, 4, 5}

fmt.Println(slices.IsSorted([]int{1, 2, 3})) // true
fmt.Println(slices.Compare([]int{1, 2}, []int{1, 3})) // -1
```

自定义合并只处理**相邻**元素：

```go
words := []string{"Go", "go", "JAVA", "java"}
words = slices.CompactFunc(words, strings.EqualFold)
// []string{"Go", "JAVA"}
```

自定义排序函数返回：

- 负数：`a` 应排在 `b` 前面。
- `0`：二者相等。
- 正数：`a` 应排在 `b` 后面。

```go
words := []string{"pear", "a", "apple"}
slices.SortFunc(words, func(a, b string) int {
    if len(a) < len(b) {
        return -1
    }
    if len(a) > len(b) {
        return 1
    }
    return strings.Compare(a, b)
})
// []string{"a", "pear", "apple"}：先按长度，再按字典序
```

二分查找前必须先升序排序：

```go
nums := []int{7, 1, 3, 3}
slices.Sort(nums)

i, found := slices.BinarySearch(nums, 3)
// i == 1，found == true
```

### 6. `sort` 和 `slices` 怎么选

- 题目环境使用 Go 1.21+：普通切片操作优先使用 `slices`，写法更统一。
- 旧版 Go 环境：使用 `sort.Ints`、`sort.Strings` 和 `sort.Slice`。
- 需要 `sort.Search` 的通用“答案二分”模式：继续使用 `sort`。

最值得先记住的一组方法：

```text
strings：Fields、Split、Join、Contains、TrimSpace
strconv：Atoi、Itoa、ParseInt、FormatInt
sort：Ints、Slice、Search
unicode：IsLetter、IsDigit、ToLower
slices：Sort、Contains、Clone、Reverse、BinarySearch
```

完整方法签名可查阅 Go 官方文档：[strings](https://pkg.go.dev/strings)、[strconv](https://pkg.go.dev/strconv)、[sort](https://pkg.go.dev/sort)、[unicode](https://pkg.go.dev/unicode)、[slices](https://pkg.go.dev/slices)。

## 专题一：哈希与双指针

### 1. 专题背景

哈希与双指针经常出现在数组、字符串和“若干数之和”问题中，但二者解决问题的方式不同。

#### 1.1 哈希：用空间换取查找速度

哈希表通过键快速定位值。在 Go 中，最常见的实现是 `map`：

```go
index := map[int]int{
    7: 1, // 数值 7 出现在下标 1
}
```

刷题时，出现以下信号可以优先考虑哈希：

- 需要快速判断某个值**是否出现过**。
- 需要统计元素的**出现次数**。
- 需要建立“字符 → 频次”“数值 → 下标”等映射。
- 暴力解法中存在一层反复执行的查找。

哈希表的查询和插入平均为 \(O(1)\)，但通常需要 \(O(n)\) 额外空间。它不是“自动优化器”，关键是先想清楚：

> `key` 表示什么，`value` 又保存什么？

例如“两数之和”不仅要判断补数是否存在，还要返回补数的下标，因此适合使用 `map[int]int`，其中键是数值，值是下标。

#### 1.2 双指针：用指针关系缩小搜索空间

双指针并不是某一种固定算法，而是使用两个位置变量协同遍历。常见形式包括：

| 类型 | 指针如何移动 | 常见场景 |
|---|---|---|
| 同向快慢指针 | 都向右，速度或职责不同 | 移动零、原地删除、去重 |
| 相向指针 | 从两端向中间靠拢 | 有序数组求和、三数之和、盛水容器 |
| 分离指针 | 分别遍历不同序列 | 合并有序数组、字符串比较 |

使用双指针的前提，是能够根据当前状态**安全排除一批候选答案**。如果移动任意一边都没有逻辑依据，那只是写了两个下标，还没有形成有效算法。

#### 1.3 两种方法如何选择

- 需要保留原数组下标，数组又无序：通常优先考虑哈希。
- 数据有序，或允许排序后再求组合：通常可以考虑相向双指针。
- 要在原数组中稳定地筛选或搬移元素：通常考虑快慢指针。
- 需要频次、分组或存在性判断：通常考虑哈希。

哈希经常用额外空间降低时间复杂度；双指针则常利用顺序、单调性或题目结构，在较低额外空间下减少无效枚举。

### 2. 本专题题目看板

题目来自当前学习清单，难度标记沿用截图中的 A/B 分组。

| 状态 | 分组 | 题号 | 题目 | 核心训练点 | 笔记 |
|:---:|:---:|---:|---|---|---|
| ✅ | A | 1 | [两数之和](https://leetcode.cn/problems/two-sum/) | 暴力枚举、补数、哈希映射 | [查看](#题目-1两数之和) |
| ⬜ | A | 49 | [字母异位词分组](https://leetcode.cn/problems/group-anagrams/) | 字符频次、哈希分组键 | 待完成 |
| ⬜ | A | 128 | [最长连续序列](https://leetcode.cn/problems/longest-consecutive-sequence/) | 哈希集合、序列起点 | 待完成 |
| ⬜ | A | 283 | [移动零](https://leetcode.cn/problems/move-zeroes/) | 快慢指针、原地覆盖 | 待完成 |
| ⬜ | A | 15 | [三数之和](https://leetcode.cn/problems/3sum/) | 排序、相向双指针、去重 | 待完成 |
| ⬜ | B | 11 | [盛最多水的容器](https://leetcode.cn/problems/container-with-most-water/) | 相向双指针、移动短板 | 待完成 |

状态说明：

- ⬜ 未开始
- 🟡 已完成首次提交，尚未复盘
- ✅ 已完成题解与复盘
- 🔁 已独立重做

### 3. 每道题的记录模板

以后新增题目时复制下面这段：

```markdown
## 题目 X：题目名称

### 题目摘要

- **题目链接**：
- **输入与输出**：
- **关键约束**：

### 我的第一反应

> 不看题解时，我最先想到什么？

### 解法一：直觉 / 暴力解法

#### 我的思路

#### 代码

#### 复杂度

- 时间复杂度：
- 空间复杂度：

#### 主要关注点

### 解法二：优化解法

#### 优化突破口

#### 代码

#### 复杂度

- 时间复杂度：
- 空间复杂度：

#### 关键不变量

### 对比与复盘

| 对比项 | 解法一 | 解法二 |
|---|---|---|
| 时间复杂度 |  |  |
| 空间复杂度 |  |  |
| 优点 |  |  |
| 局限 |  |  |

### 易错点

### 可迁移的规律

### 重做记录

- YYYY-MM-DD：
```

---

### 题目 1：两数之和

#### 题目摘要

- **题目链接**：[LeetCode 1. 两数之和](https://leetcode.cn/problems/two-sum/)
- **输入**：整数数组 `nums` 和目标值 `target`。
- **输出**：两个不同元素的下标，使对应元素之和等于 `target`。
- **关键约束**：只有一个有效答案；同一个元素不能使用两次；数组无序。

题目核心可以改写为：

\[
nums[i]+nums[j]=target
\]

固定一个数 `nums[j]` 后，需要寻找的另一个数就是：

\[
nums[i]=target-nums[j]
\]

这个“寻找补数”的过程，正是从暴力解法走向哈希解法的突破口。

#### 我的第一反应

最直观的方法是把所有两个数的组合都试一遍：

1. 外层循环选定第一个下标 `i`。
2. 内层循环从 `i+1` 开始寻找第二个下标 `j`。
3. 如果两数之和等于 `target`，立即返回。

这个方法与手工检查数对的过程一致，容易想到，也容易验证正确性。它的问题不在于“错”，而在于数组变大后重复查找太多。

#### 解法一：双层循环暴力枚举

##### 代码

```go
func twoSum(nums []int, target int) []int {
    for i, v := range nums {
        for j := i + 1; j < len(nums); j++ {
            if v+nums[j] == target {
                return []int{i, j}
            }
        }
    }
    return nil
}
```

##### 我的思路

外层的 `v` 是已经选定的第一个数，内层只检查它右边的元素。让 `j` 从 `i+1` 开始有两个作用：

- 不会把同一个元素使用两次。
- 不会重复检查 `(i, j)` 和 `(j, i)`。

题目保证存在唯一答案，所以找到以后可以直接返回，不需要收集所有组合。

##### 复杂度

- **时间复杂度：\(O(n^2)\)**。最坏情况下需要检查约 \(n(n-1)/2\) 个数对。
- **空间复杂度：\(O(1)\)**。除返回值外，只使用了少量变量。

##### 主要关注点

1. `j` 必须从 `i+1` 开始，而不是从 `0` 或 `i` 开始。
2. 这是正确的基线方案，可以先写出来验证对题意的理解。
3. 内层循环的工作本质是：反复寻找 `target-v` 是否存在。
4. 优化方向不是减少一次加法，而是消除重复的线性查找。

#### 解法二：一次遍历 + 哈希表

##### 优化突破口

如果固定当前元素 `x`，就只需知道它左边是否已经出现过 `target-x`。

暴力解法每次都在线性扫描；哈希解法则把已经访问过的“数值 → 下标”保存起来，使查询补数的平均时间从 \(O(n)\) 降为 \(O(1)\)。

##### 代码

```go
func twoSum(nums []int, target int) []int {
    idx := map[int]int{} // key：数值；value：该数值的下标

    for j, x := range nums {
        // 在左侧已遍历的元素中寻找 nums[i] = target - x
        if i, ok := idx[target-x]; ok {
            return []int{i, j}
        }

        // 当前元素留给后面的元素使用
        idx[x] = j
    }

    return nil
}
```

##### 我的思路

`idx` 只保存当前位置左边已经遍历过的元素。遍历到 `x` 时：

1. 计算补数 `target-x`。
2. 查询补数是否已经存在于 `idx`。
3. 如果存在，取出它的下标 `i`，与当前下标 `j` 一起返回。
4. 如果不存在，再把当前数值和下标放入哈希表。

这里必须**先查询、后写入**。以 `nums = [3, 3]`、`target = 6` 为例：

- 第一次遇到 `3`：表中没有补数 `3`，于是保存 `3 → 0`。
- 第二次遇到 `3`：查到 `3 → 0`，返回 `[0, 1]`。

如果先写入再查询，第一次遍历就可能用同一个元素同时充当两个数，违反题意。

##### 复杂度

- **时间复杂度：平均 \(O(n)\)**。数组遍历一次，哈希查询和插入平均为 \(O(1)\)。
- **空间复杂度：\(O(n)\)**。最坏情况下需要保存接近 \(n\) 个元素。

##### 关键不变量

在处理下标 `j` 之前：

> `idx` 中只保存区间 `[0, j)` 的元素值及其下标，不包含当前元素 `nums[j]`。

这个不变量同时保证了：

- 找到的 `i` 一定满足 `i < j`。
- 不会重复使用当前元素。
- 每个候选补数都能在需要时被找到。

##### 代码来源说明

哈希版本的代码与注释参考了灵茶山艾府的题解：

- 作者：灵茶山艾府
- 来源：[力扣题解：动画，从两数之和中我学会了如何使用哈希表](https://leetcode.cn/problems/two-sum/solutions/2326193/dong-hua-cong-liang-shu-zhi-he-zhong-wo-0yvmj/)

本文在此基础上重新整理了变量含义、执行顺序、不变量与复杂度分析。

#### 两种解法对比

| 对比项 | 解法一：暴力枚举 | 解法二：哈希表 |
|---|---|---|
| 时间复杂度 | \(O(n^2)\) | 平均 \(O(n)\) |
| 空间复杂度 | \(O(1)\) | \(O(n)\) |
| 核心操作 | 枚举所有数对 | 查询补数是否出现 |
| 优点 | 直观、额外空间少 | 只遍历一次、速度更快 |
| 局限 | 输入大时容易超时 | 使用额外哈希空间 |

这是一种典型的**空间换时间**：用 \(O(n)\) 的额外空间，换掉一层 \(O(n)\) 的重复查找。

#### 为什么不直接使用双指针

两数之和的原数组是无序的，并且题目要求返回原始下标。

如果先排序再使用左右指针，还必须额外保存每个数排序前的下标；排序本身需要 \(O(n\log n)\) 时间，整体也不如哈希方案直接。

因此，这道题的首选方案是哈希表。到了“三数之和”，题目返回的是数值组合而不是原下标，排序后更容易去重，双指针才会体现出优势。

#### 易错点

1. **把当前元素提前写入哈希表**：可能重复使用同一元素。
2. **哈希表方向写反**：这里应保存 `数值 → 下标`，因为查询条件是补数，返回目标是下标。
3. **用 `idx[x] != 0` 判断存在**：下标 `0` 是合法值，必须使用 Go 的 comma-ok 写法。
4. **忽略重复元素**：`[3,3]` 是必须通过的测试案例。
5. **暴力解法让 `j` 从 0 开始**：会重复枚举，也可能使用同一位置。

#### 建议测试案例

```text
nums = [2,7,11,15], target = 9  → [0,1]  // 普通情况
nums = [3,2,4],     target = 6  → [1,2]  // 补数在左边
nums = [3,3],       target = 6  → [0,1]  // 重复元素
nums = [-3,4,3,90], target = 0  → [0,2]  // 包含负数
```

#### 可迁移的规律

看到下面这种结构时，可以考虑“补数 + 哈希表”：

```text
固定当前值 x
需要寻找另一个值 y
并且 y 可以由目标值和 x 直接算出
```

在本题中，`y = target - x`。类似思想还会出现在差值问题、前缀和、计数配对等题型中。

#### 重做记录

- 2026-07-28：完成暴力解法与哈希解法的首次整理。
- 下次目标：不看代码，独立写出哈希版本，并准确解释为什么必须先查询再插入。

---

### 4. 后续题目占位

#### 题目 49：字母异位词分组

- **预习问题**：怎样为属于同一组的字符串设计相同的哈希键？
- **重点**：排序后的字符串作键；或使用字符频次数组作键。
- **状态**：⬜ 待完成。

#### 题目 128：最长连续序列

- **预习问题**：怎样判断一个数是不是连续序列的起点？
- **重点**：哈希集合；只从不存在 `x-1` 的 `x` 开始扩展。
- **状态**：⬜ 待完成。

#### 题目 283：移动零

- **预习问题**：如何在不复制数组的前提下，保持非零元素的相对顺序？
- **重点**：快指针负责探索，慢指针指向下一个非零元素应放置的位置。
- **状态**：⬜ 待完成。

#### 题目 15：三数之和

- **预习问题**：为什么排序后可以使用左右指针？怎样避免重复三元组？
- **重点**：排序、固定一个数、相向双指针、三层去重。
- **状态**：⬜ 待完成。

#### 题目 11：盛最多水的容器

- **预习问题**：为什么每次应该移动较短的一边？
- **重点**：面积由宽度和短板共同决定；移动长板无法突破当前短板上限。
- **状态**：⬜ 待完成。

### 5. 专题参考资料

- [Hello 算法：哈希表](https://www.hello-algo.com/chapter_hashing/hash_map/)
- [Hello 算法：哈希优化策略](https://www.hello-algo.com/chapter_searching/hashing_search/)
- [代码随想录：哈希表理论基础](https://programmercarl.com/哈希表理论基础.html)
- [代码随想录：双指针总结篇](https://programmercarl.com/algo/two-pointers/two-pointers-summary.html)
- [代码随想录：1. 两数之和](https://programmercarl.com/algo/hash-table/0001-two-sum.html)
