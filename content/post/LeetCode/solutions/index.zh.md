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
| ✅ | A | 49 | [字母异位词分组](https://leetcode.cn/problems/group-anagrams/) | 排序、哈希分组键 | [查看](#题目-49字母异位词分组) |
| ✅ | A | 128 | [最长连续序列](https://leetcode.cn/problems/longest-consecutive-sequence/) | 排序断点、哈希集合、序列起点 | [查看](#题目-128最长连续序列) |
| ✅ | A | 283 | [移动零](https://leetcode.cn/problems/move-zeroes/) | 原地栈、快慢指针、交换 | [查看](#题目-283移动零) |
| ✅ | A | 15 | [三数之和](https://leetcode.cn/problems/3sum/) | 排序、相向双指针、剪枝与去重 | [查看](#题目-15三数之和) |
| ✅ | B | 11 | [盛最多水的容器](https://leetcode.cn/problems/container-with-most-water/) | 相向双指针、面积短板、排除法 | [查看](#题目-11盛最多水的容器) |

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

### 题目 49：字母异位词分组

#### 题目摘要

- **题目链接**：[LeetCode 49. 字母异位词分组](https://leetcode.cn/problems/group-anagrams/)
- **输入**：字符串切片 `strs []string`。
- **输出**：把互为字母异位词的字符串放在同一个分组中，返回 `[][]string`。
- **关键性质**：字母异位词使用相同字符且每种字符出现次数相同，只是排列顺序不同。

例如：

```text
"eat"、"tea"、"ate" 排序后都是 "aet"
"tan"、"nat"       排序后都是 "ant"
```

所以问题可以转化为：

> 怎样为属于同一组的字符串构造完全相同、不同组之间又不同的哈希键？

#### 方法一：排序结果作为哈希键

```go
func groupAnagrams(strs []string) [][]string {
    idx := map[string][]string{}

    for _, v := range strs {
        runes := []rune(v)
        slices.Sort(runes)
        sortedS := string(runes)
        idx[sortedS] = append(idx[sortedS], v)
    }

    var res [][]string
    for _, list := range idx {
        res = append(res, list)
    }
    return res
}
```

##### 我的思路

如果直接拿原字符串作为 Map 的键，`"eat"` 和 `"tea"` 是两个不同的键，无法自动进入同一组。

但互为字母异位词的字符串排序后一定相同。因此可以把排序后的字符串当作“组名”：

```text
原字符串 v
   ↓ 转为 []rune
排序字符
   ↓ 转回 string
得到统一的分组键 sortedS
   ↓
idx[sortedS] = append(idx[sortedS], v)
```

这里的 Map 类型是：

```go
map[string][]string
//  key：排序后的标准形式
// value：属于该组的所有原字符串
```

执行 `idx[sortedS] = append(idx[sortedS], v)` 时，即使这个键第一次出现也不需要提前初始化切片：

1. 读取不存在的键，会得到 `[]string` 的零值 `nil`。
2. `append(nil, v)` 是合法的，会创建新切片。
3. 再把新切片写回 `idx[sortedS]`。

以 `["eat", "tea", "tan", "ate"]` 为例：

| 原字符串 | 排序后的键 | Map 中对应的分组 |
|---|---|---|
| `"eat"` | `"aet"` | `["eat"]` |
| `"tea"` | `"aet"` | `["eat","tea"]` |
| `"tan"` | `"ant"` | `["tan"]` |
| `"ate"` | `"aet"` | `["eat","tea","ate"]` |

最后遍历 Map 的所有 value，把每个 `[]string` 分组加入结果。

##### 为什么转换成 `[]rune`

字符串不可原地修改，而 `slices.Sort` 需要可修改的切片，所以先执行：

```go
runes := []rune(v)
```

`[]rune` 能按 Unicode 码点处理字符，对中文等多字节字符也正确。当前 LeetCode 题目只包含小写英文字母，因此使用 `[]byte` 也可以，但 `[]rune` 更通用、语义更清晰。

##### 复杂度

设：

- \(n\) 为字符串数量。
- \(k\) 为字符串的最大字符数。

每个字符串排序需要 \(O(k\log k)\)，共处理 \(n\) 个字符串：

- **时间复杂度：\(O(nk\log k)\)**。
- **空间复杂度：\(O(nk)\)**。哈希键、分组结果以及字符转换需要额外空间；若不计算返回结果，哈希表中的键和值仍会随输入增长。

##### 主要关注点

1. **Map 的键必须可比较**：`string` 可以作为键，`[]rune` 和 `[]byte` 不可以。
2. **保存原字符串**：排序只用于生成键，value 中追加的是原始的 `v`。
3. **必须接收 `append` 的返回值**：`append` 可能创建新的底层数组。
4. **不依赖 Map 顺序**：Go 的 Map 遍历顺序不固定，但题目允许任意顺序返回分组。
5. **空字符串可以正常处理**：`""` 排序后仍是 `""`，所有空字符串会进入同一组。

#### 方法二：字符计数作为哈希键

互为字母异位词的字符串不仅排序结果相同，每个字母的出现次数也完全相同。

题目限定字符串只包含小写英文字母，因此可以使用长度固定为 26 的数组：

```go
func groupAnagrams(strs []string) [][]string {
    groups := map[[26]int][]string{}

    for _, s := range strs {
        var count [26]int

        for _, ch := range s {
            count[ch-'a']++
        }

        groups[count] = append(groups[count], s)
    }

    var result [][]string
    for _, group := range groups {
        result = append(result, group)
    }
    return result
}
```

也可以使用 Go 1.23+ 的收集写法：

```go
func groupAnagrams(strs []string) [][]string {
    groups := map[[26]int][]string{}

    for _, s := range strs {
        var count [26]int
        for _, ch := range s {
            count[ch-'a']++
        }
        groups[count] = append(groups[count], s)
    }

    return slices.Collect(maps.Values(groups))
}
```

##### 我的思路

用数组的每个位置表示一个字母：

```text
下标：  0   1   2   3  ...  25
字母： 'a' 'b' 'c' 'd' ... 'z'
内容：该字母在字符串中的出现次数
```

`ch-'a'` 会把字符映射为 `0` 到 `25`：

```go
'a' - 'a' // 0
'b' - 'a' // 1
'z' - 'a' // 25
```

例如 `"abbc"` 得到的计数键可以简写为：

```text
[1, 2, 1, 0, 0, ..., 0]
 ↑  ↑  ↑
 a  b  c
```

无论输入是 `"abbc"`、`"bcab"` 还是 `"cbba"`，得到的 `[26]int` 都相同，因此会进入同一组。

##### 为什么 `[26]int` 能作为 Map 的键

Go 的 Map 键必须是可比较类型：

- 数组 `[26]int`：长度固定，所有元素都是可比较的 `int`，所以整个数组可比较，可以作为键。
- 切片 `[]int`：长度可变，不能使用 `==` 比较内容，所以不能作为 Map 的键。

因此必须写：

```go
map[[26]int][]string // 正确
```

不能写：

```go
// map[[]int][]string // 编译错误：invalid map key type []int
```

数组类型包含长度，`[26]int` 和 `[27]int` 是两种不同的类型。

##### 为什么这里的 `range string` 是安全的

```go
for _, ch := range s {
    count[ch-'a']++
}
```

`ch` 的类型是 `rune`。题目保证只有 `'a'` 到 `'z'`，所以 `ch-'a'` 一定落在 `[0,25]`。

如果输入可能包含大写字母、中文、标点或其他 Unicode 字符，就不能直接用长度为 26 的数组，否则可能越界。那时应根据字符范围调整方案，或者使用 `map[rune]int` 统计频次。

##### 复杂度

设 \(n\) 为字符串数量，\(k\) 为字符串的最大长度：

- **时间复杂度：\(O(nk)\)**。每个字符只统计一次，不再排序。
- **空间复杂度：\(O(nk)\)**。主要用于保存分组和原字符串；每个不同分组还需要一个固定长度为 26 的计数键。

和方法一相比，单个字符串的处理从 \(O(k\log k)\) 降为 \(O(k)\)。

##### 两种方法对比

| 对比项 | 方法一：排序键 | 方法二：计数键 |
|---|---|---|
| Map 类型 | `map[string][]string` | `map[[26]int][]string` |
| 单个字符串处理 | \(O(k\log k)\) | \(O(k)\) |
| 总时间复杂度 | \(O(nk\log k)\) | \(O(nk)\) |
| 字符范围 | 更容易支持一般字符 | 当前实现只适合 `a` 到 `z` |
| 键的可读性 | 排序后的字符串直观 | 固定数组更高效 |
| 实现难度 | 简单 | 需要正确映射字符下标 |

选择建议：

- 第一次做题或字符范围不固定：优先使用排序键，直观且不容易写错。
- 题目明确只有 26 个小写英文字母，并且希望进一步优化：使用 `[26]int` 计数键。

##### 来源说明

字符计数方法参考：

- 作者：力扣官方题解
- 来源：[49. 字母异位词分组——官方题解](https://leetcode.cn/problems/group-anagrams/solutions/520469/zi-mu-yi-wei-ci-fen-zu-by-leetcode-solut-gyoc/)

本文使用 Go 的 `[26]int` 可比较数组重新整理了实现、类型说明与复杂度分析。

#### 使用 `maps.Values` 和 `slices.Collect` 简化返回

如果使用 Go 1.23 或更高版本，最后的 Map 遍历可以缩写为：

```go
import (
    "maps"
    "slices"
)

func groupAnagrams(strs []string) [][]string {
    idx := map[string][]string{}

    for _, v := range strs {
        runes := []rune(v)
        slices.Sort(runes)
        key := string(runes)
        idx[key] = append(idx[key], v)
    }

    return slices.Collect(maps.Values(idx))
}
```

两个函数的类型关系是：

```go
maps.Values(idx)                 // iter.Seq[[]string]
slices.Collect(maps.Values(idx)) // [][]string
```

##### `maps.Values`

简化后的函数签名：

```go
func Values[Map ~map[K]V, K comparable, V any](m Map) iter.Seq[V]
```

- **输入**：`map[K]V`。
- **输出**：`iter.Seq[V]`，即一个逐个产生 Map value 的迭代器。
- **重点**：它没有立即返回 `[]V`。
- **顺序**：与 Map 遍历一样，没有固定顺序。

本题中 `idx` 的类型是 `map[string][]string`，所以：

```text
K = string
V = []string
maps.Values(idx) 的类型 = iter.Seq[[]string]
```

##### `slices.Collect`

简化后的函数签名：

```go
func Collect[E any](seq iter.Seq[E]) []E
```

- **输入**：`iter.Seq[E]` 迭代器。
- **输出**：包含迭代器所有元素的 `[]E`。
- **作用**：真正执行迭代，并把产生的值收集成切片。

本题中每次产生的元素 `E` 是一个 `[]string` 分组，因此最终得到 `[][]string`。

可以把两者理解成流水线：

```text
idx
  → maps.Values：只取所有 value，形成迭代器
  → slices.Collect：消费迭代器，收集成 [][]string
```

##### 为什么普通循环仍然值得掌握

```go
var res [][]string
for _, list := range idx {
    res = append(res, list)
}
return res
```

普通循环的优点是兼容旧版 Go，也更容易在收集过程中增加过滤、排序或其他处理。`slices.Collect(maps.Values(idx))` 更短，但依赖 Go 1.23+，并且不会让结果顺序变得稳定。

#### 可迁移的规律

“分组”类问题的核心通常是设计规范化的键：

```text
原始对象 → 规范化表示 → 作为 Map 的 key → 原对象追加到 value 切片
```

本题用“排序后的字符串”规范化。以后还会遇到：

- 用字符频次数组表示单词。
- 用约分后的分子、分母表示分数。
- 用平移后的相对坐标表示相同形状。

#### 重做记录

- 2026-07-28：完成排序键与 `[26]int` 字符计数键两种哈希分组解法。
- 下次目标：不看代码独立写出计数版本，并解释为什么数组可以作为 Map 的键、切片却不可以。

---

### 题目 128：最长连续序列

#### 题目摘要

- **题目链接**：[LeetCode 128. 最长连续序列](https://leetcode.cn/problems/longest-consecutive-sequence/)
- **输入**：未排序整数切片 `nums []int`。
- **输出**：最长连续数字序列的长度；这些数字不要求在原数组中相邻。
- **关键要求**：题目要求设计 \(O(n)\) 时间复杂度的算法。

例如：

```text
nums = [100,4,200,1,3,2]
最长连续序列 = [1,2,3,4]
答案 = 4
```

#### 方法一：排序后寻找断点

```go
func longestConsecutive(nums []int) int {
    if len(nums) == 0 {
        return 0
    }

    sort.Ints(nums)
    current, longest := 1, 1

    for i := 0; i < len(nums)-1; i++ {
        switch {
        case nums[i+1] == nums[i]+1:
            current++
            longest = max(longest, current)
        case nums[i+1] == nums[i]:
            continue
        default:
            current = 1
        }
    }

    return longest
}
```

##### 我的思路：找断点并统计连续段

排序以后，原本散落在数组中的连续数字会靠在一起：

```text
原数组：[100,4,200,1,3,2,2]
排序后：[1,2,2,3,4,100,200]
```

扫描相邻元素时只有三种情况：

1. `nums[i+1] == nums[i]+1`：数值连续，当前长度加一。
2. `nums[i+1] == nums[i]`：遇到重复数字，忽略它，当前长度不变。
3. 其他情况：出现断点，新序列从长度 1 重新开始。

其中：

- `current`：当前连续段的长度。
- `longest`：到目前为止见过的最大长度。

这就是“找断点，然后统计并比较大小”的完整表达。

##### 为什么重复数字不能重置长度

例如排序结果为：

```text
[0,1,1,2]
```

最长连续序列是 `[0,1,2]`，长度为 3。中间多出来的另一个 `1` 不应该把连续段截断，所以遇到相同元素必须 `continue`。

##### 复杂度与局限

- **时间复杂度：\(O(n\log n)\)**。瓶颈是排序，之后扫描为 \(O(n)\)。
- **额外空间复杂度**：取决于排序实现；不计算排序内部栈时常简写为 \(O(1)\)。
- **副作用**：`sort.Ints(nums)` 会直接修改输入切片的顺序。

这个方法是正确的，代码也很直观；但题目明确要求 \(O(n)\)，因此它没有满足题目的进阶复杂度要求。

#### 方法二：哈希集合 + 只从序列起点扩展

```go
func longestConsecutive(nums []int) int {
    set := make(map[int]struct{}, len(nums))
    for _, num := range nums {
        set[num] = struct{}{}
    }

    longest := 0

    for x := range set {
        if _, exists := set[x-1]; exists {
            continue // x 不是起点
        }

        y := x
        for {
            if _, exists := set[y]; !exists {
                break
            }
            y++
        }

        longest = max(longest, y-x)
    }

    return longest
}
```

也可以使用 `map[int]bool` 写得更短：

```go
func longestConsecutive(nums []int) (answer int) {
    has := map[int]bool{}
    for _, num := range nums {
        has[num] = true
    }

    for x := range has {
        if has[x-1] {
            continue
        }

        y := x + 1
        for has[y] {
            y++
        }
        answer = max(answer, y-x)
    }

    return
}
```

##### 优化突破口

排序法先把数字排好，再观察相邻元素是否连续。哈希法换了一个角度：

> 我们不需要知道所有数字的顺序，只需要快速判断“某个数字是否存在”。

哈希表平均可以在 \(O(1)\) 时间内完成存在性查询，因此可以直接询问：

```text
x-1 存在吗？     → 判断 x 是不是序列起点
x+1、x+2 存在吗？→ 从起点向右统计序列长度
```

##### 第一步：用 Map 建立去重后的数字集合

```go
has := map[int]bool{}
for _, num := range nums {
    has[num] = true
}
```

假设输入：

```go
nums := []int{100, 4, 200, 1, 3, 2, 2}
```

Map 中只会保留不同数字：

```text
100、4、200、1、3、2
```

重复的 `2` 不会产生第二个键。此后：

```go
has[3]  // true：3 存在
has[99] // false：99 不存在
```

##### 第二步：只从真正的序列起点开始

```go
for x := range has {
    if has[x-1] {
        continue
    }
    // 能执行到这里，说明 x-1 不存在，x 是起点
}
```

为什么检查的是 `x-1`？

假设集合里有 `{2,3,4,5}`：

```text
x=3：2 存在，不从 3 开始
x=4：3 存在，不从 4 开始
x=5：4 存在，不从 5 开始
x=2：1 不存在，2 是起点，扩展得到 [2,3,4,5]
```

如果 `x-1` 存在，说明 `x` 左边还有数字，从 `x` 开始只能得到一条不完整的序列。只有 `x-1` 不存在时，`x` 才是整条序列的最小值。

这一步确保 `[2,3,4,5]` 只从 `2` 统计一次，而不会分别从 `3`、`4`、`5` 重复统计。

##### 第三步：从起点不断寻找下一个数字

```go
y := x + 1
for has[y] {
    y++
}
```

假设当前起点 `x=1`，Map 中存在 `1、2、3、4`：

```text
y=2：存在，继续
y=3：存在，继续
y=4：存在，继续
y=5：不存在，停止
```

循环结束后：

```text
x = 1
y = 5
真正存在的序列是 [1,2,3,4]
```

此时 `y` 指向第一个不存在的数字，所以长度为：

\[
(y-1)-x+1=y-x
\]

因此代码写成：

```go
answer = max(answer, y-x)
```

而不是 `y-x+1`。

##### 完整运行示例

输入：

```go
nums := []int{100, 4, 200, 1, 3, 2}
```

虽然 Map 的遍历顺序不固定，但每个数字的判断逻辑如下：

| 当前数字 `x` | `x-1` 是否存在 | 是否为起点 | 处理结果 |
|---:|:---:|:---:|---|
| `100` | 否 | 是 | 序列 `[100]`，长度 1 |
| `4` | 是，存在 `3` | 否 | 跳过 |
| `200` | 否 | 是 | 序列 `[200]`，长度 1 |
| `1` | 否 | 是 | 序列 `[1,2,3,4]`，长度 4 |
| `3` | 是，存在 `2` | 否 | 跳过 |
| `2` | 是，存在 `1` | 否 | 跳过 |

最终得到：

```go
answer == 4
```

##### `for range Map` 是有序的吗

不是。Go 的 Map 遍历顺序没有规定，也不保证两次遍历得到相同顺序。

```go
for x := range has {
    fmt.Println(x)
}
```

可能先输出 `3`，也可能先输出 `100`。本题不依赖顺序：

- 如果先遇到 `3`，因为 `2` 存在，所以跳过。
- 即使最后才遇到 `1`，仍然能从 `1` 找到完整的 `[1,2,3,4]`。

Map 无序不会影响答案，因为“是不是起点”只由 `x-1` 是否存在决定，与遍历先后无关。

参考：[Go 语言规范：for range](https://go.dev/ref/spec#For_statements)。

##### 为什么看起来有两层循环，仍然是 \(O(n)\)

内层循环不会对每个 `x` 都完整执行。只有序列起点会进入扩展过程，其他成员因为存在前驱 `x-1` 而被跳过。

不同连续序列互不重叠，每个不同数字：

- 在外层集合遍历中访问一次。
- 最多再作为某条序列的成员被内层循环访问一次。

因此所有内层循环的总执行次数仍为 \(O(n)\)，不是 \(O(n^2)\)。

##### 为什么要遍历集合，而不是原数组

集合同时完成了去重。

如果原数组包含大量重复起点：

```text
[1,1,1,...,1,2,3,4,5]
```

遍历原数组会从每一个 `1` 都向后扩展一遍，可能退化到 \(O(n^2)\)。遍历集合时只有一个 `1`，整条链只计算一次。

##### `map[int]struct{}` 与 `map[int]bool`

两种写法都可以表示集合：

```go
set := map[int]struct{}{}
set[x] = struct{}{}
_, exists := set[x]
```

```go
has := map[int]bool{}
has[x] = true
exists := has[x]
```

- `map[int]struct{}` 更明确地表示“只关心键是否存在”，空结构体不保存额外数据。
- `map[int]bool` 写法更短，但要约定只存 `true`，否则“键不存在”和“键存在但值为 false”读出来都是 `false`。

##### 复杂度

设 \(n\) 为数组长度，\(m\) 为不同数字的数量：

- **时间复杂度：平均 \(O(n)\)**。构建集合需要 \(O(n)\)，查找和扩展总计 \(O(m)\)。
- **空间复杂度：\(O(m)\)**。哈希集合只保存不同数字。
- **副作用**：不会改变原始 `nums` 的顺序。

##### 可选的提前结束优化

参考代码中的：

```go
m := len(has)
if answer*2 >= m {
    break
}
```

意思是：所有连续序列彼此不重叠。如果已经找到一条长度至少为不同元素总数一半的序列，那么剩余元素不可能再组成一条更长的序列，可以提前结束。

这个优化是正确的，但不是实现 \(O(n)\) 的关键。初学时可以先省略，让“只从起点扩展”这一核心逻辑更清楚。

##### 两种方法一样吗

不一样，区别如下：

| 对比项 | 你的排序方法 | 哈希集合方法 |
|---|---|---|
| 如何让连续数字产生联系 | 排序后比较相邻元素 | 用哈希表查询前驱和后继 |
| 如何识别新序列 | 相邻差值不为 1 时出现断点 | `x-1` 不存在时，`x` 是起点 |
| 重复元素处理 | 显式 `continue` | 构建集合时自动去重 |
| 时间复杂度 | \(O(n\log n)\) | 平均 \(O(n)\) |
| 空间复杂度 | 取决于排序实现 | \(O(m)\) |
| 是否修改输入 | 是 | 否 |
| 是否满足题目要求的 \(O(n)\) | 否 | 是 |

两种方法的共同点，是都想办法让一条连续序列只统计一次；但实现手段和复杂度并不相同。

##### 易错点

1. 排序法忽略重复值，导致当前长度被错误重置。
2. 哈希法从每个元素都向后扩展，没有判断 `x-1` 是否存在。
3. 哈希法遍历原数组而不是去重后的集合。
4. 把“连续序列”误解成元素在原数组中的下标也必须连续。
5. 忘记空数组的答案是 0。

##### 建议测试案例

```text
nums = []                        → 0  // 空数组
nums = [7]                       → 1  // 单个元素
nums = [100,4,200,1,3,2]         → 4  // 普通情况
nums = [0,3,7,2,5,8,4,6,0,1]    → 9  // 包含重复元素
nums = [1,0,1,2]                 → 3  // 重复值不能截断序列
nums = [-2,-1,0,1,5]             → 4  // 包含负数
nums = [1,3,5,7]                 → 1  // 没有相邻连续数字
```

##### 来源说明

哈希集合的两个关键优化参考了灵茶山艾府的《两个关键优化，O(n) 时间复杂度》题解：

- 只从不存在前驱 `x-1` 的序列起点开始扩展。
- 遍历去重后的哈希集合，而不是包含重复项的原数组。

题目与题解列表：[LeetCode 128. 最长连续序列](https://leetcode.cn/problems/longest-consecutive-sequence/solutions/)

#### 重做记录

- 2026-07-29：完成排序断点法和哈希集合起点法。
- 下次目标：不排序写出 \(O(n)\) 解法，并解释为什么嵌套循环的总时间仍是 \(O(n)\)。

---

### 题目 283：移动零

#### 题目摘要

- **题目链接**：[LeetCode 283. 移动零](https://leetcode.cn/problems/move-zeroes/)
- **输入**：整数切片 `nums []int`。
- **要求**：把所有 `0` 移到末尾，同时保持非零元素的相对顺序。
- **限制**：必须原地修改，不能复制整个数组。

例如：

```text
输入： [0,1,0,3,12]
输出： [1,3,12,0,0]
```

#### 方法一：原地栈——先覆盖非零元素，再补零

```go
func moveZeroes(nums []int) {
    slow := 0

    for i := 0; i < len(nums); i++ {
        if nums[i] != 0 {
            nums[slow] = nums[i]
            slow++
        }
    }

    for i := slow; i < len(nums); i++ {
        nums[i] = 0
    }
}
```

##### 我的思路

可以把数组左侧看成一个只保存非零元素的“栈”：

- `i` 负责扫描所有元素。
- `slow` 表示当前已经保存了多少个非零元素。
- `slow` 同时也是下一个非零元素应该写入的位置。

每当 `nums[i] != 0`：

```go
nums[slow] = nums[i] // 把非零元素放到左侧
slow++               // 栈大小加一
```

第一遍结束后：

- `[0, slow)` 已经是所有非零元素，且相对顺序不变。
- `slow` 等于非零元素的数量。
- `[slow, len(nums))` 应该全部改成 `0`。

所以再用第二个循环填零。

##### 完整运行过程

输入：

```text
nums = [0,1,0,3,12]
```

| 扫描位置 `i` | `nums[i]` | 是否写入 | 写入后数组 | `slow` |
|---:|---:|:---:|---|---:|
| 0 | 0 | 否 | `[0,1,0,3,12]` | 0 |
| 1 | 1 | 是，写入 `nums[0]` | `[1,1,0,3,12]` | 1 |
| 2 | 0 | 否 | `[1,1,0,3,12]` | 1 |
| 3 | 3 | 是，写入 `nums[1]` | `[1,3,0,3,12]` | 2 |
| 4 | 12 | 是，写入 `nums[2]` | `[1,3,12,3,12]` | 3 |

注意第一遍结束后的后半部分仍然是旧数据：

```text
[1,3,12,3,12]
        ↑ 后面这些值已经没有意义
```

第二遍把 `[slow,n)` 填成零：

```text
[1,3,12,0,0]
```

##### 关键不变量

每次处理 `nums[i]` 之后：

> 区间 `[0, slow)` 保存了目前见过的全部非零元素，而且顺序与原数组相同。

因为我们始终从左到右读取，并且按发现顺序写入，所以不会改变非零元素的相对顺序。

##### 与“把 `nums` 当作栈”的方法一样吗

完全一样，只是变量名和补零写法不同：

| 你的写法 | 参考写法 | 含义 |
|---|---|---|
| `slow` | `stackSize` | 已保存的非零元素数量，也是下一次写入位置 |
| `nums[slow] = nums[i]` | `nums[stackSize] = x` | 非零元素入栈 |
| 第二个 `for` 填零 | `clear(nums[stackSize:])` | 清空剩余区间 |

Go 1.21+ 可以把第二个循环写成：

```go
clear(nums[slow:])
```

`clear` 会把切片中的每个元素设置为该类型的零值。对于 `[]int`，零值就是 `0`。

完整简写：

```go
func moveZeroes(nums []int) {
    slow := 0
    for _, x := range nums {
        if x != 0 {
            nums[slow] = x
            slow++
        }
    }
    clear(nums[slow:])
}
```

##### 复杂度

- **时间复杂度：\(O(n)\)**。第一遍扫描 \(n\) 个元素，第二遍最多再写 \(n\) 个零，\(O(2n)=O(n)\)。
- **空间复杂度：\(O(1)\)**。只使用了少量变量。

两遍循环不等于 \(O(n^2)\)，因为它们是先后执行，不是相互嵌套：

\[
O(n)+O(n)=O(n)
\]

#### 方法二：快慢指针交换元素

```go
func moveZeroes(nums []int) {
    slow := 0

    for fast, x := range nums {
        if x != 0 {
            nums[fast], nums[slow] = nums[slow], x
            slow++
        }
    }
}
```

##### 核心思路

把 `0` 看成数组中的空位：

- `fast` 从左到右寻找非零元素。
- `slow` 指向当前最左边的空位。
- 找到非零元素后，把它与最左边的空位交换。

交换之后：

- 非零元素进入左侧正确位置。
- 它原来的位置变成新的空位。
- `slow` 向右移动，继续指向最左空位。

##### 关键不变量

处理下标 `fast` 之前，数组被分成三部分：

```text
[0, slow)      已整理好的非零元素
[slow, fast)   已发现的零，也就是空位
[fast, n)      尚未检查的元素
```

当 `nums[fast] != 0` 时，把它和 `nums[slow]` 交换，三个区间的含义仍然成立。

##### 完整运行过程

输入：

```text
nums = [0,1,0,3,12]
```

| `fast` | `slow` | 当前值 | 操作后 |
|---:|---:|---:|---|
| 0 | 0 | 0 | 不操作：`[0,1,0,3,12]` |
| 1 | 0 | 1 | 交换下标 1、0：`[1,0,0,3,12]` |
| 2 | 1 | 0 | 不操作：`[1,0,0,3,12]` |
| 3 | 1 | 3 | 交换下标 3、1：`[1,3,0,0,12]` |
| 4 | 2 | 12 | 交换下标 4、2：`[1,3,12,0,0]` |

交换会把左侧空位中的 `0` 移到 `fast` 的旧位置，因此遍历结束后，右侧自然已经全是 `0`，不需要第二遍填零。

##### 如果数组开头没有零会怎样

例如：

```text
[1,2,0,3]
```

开始时 `fast == slow`，前两个非零元素只是与自己交换：

```go
nums[fast], nums[slow] = nums[slow], x
```

结果不变，`slow` 与 `fast` 一起前进。遇到第一个 `0` 后，`slow` 停在该位置，等待后面的非零元素与它交换。

##### 复杂度

- **时间复杂度：\(O(n)\)**。只扫描一次。
- **空间复杂度：\(O(1)\)**。

#### 两种方法一样吗

你的解法与方法一本质相同，与方法二不同：

| 对比项 | 方法一：覆盖后补零 | 方法二：交换 |
|---|---|---|
| 核心模型 | 把左侧当作非零元素栈 | 把零当作空位 |
| `slow` 的含义 | 下一个非零元素的写入位置 | 最左边空位的位置 |
| 遇到非零元素 | 覆盖到 `nums[slow]` | 与 `nums[slow]` 交换 |
| 如何得到末尾的零 | 第二遍循环或 `clear` | 交换时自动把零送到右边 |
| 遍历次数 | 最多两遍 | 一遍 |
| 时间复杂度 | \(O(n)\) | \(O(n)\) |
| 空间复杂度 | \(O(1)\) | \(O(1)\) |
| 是否保持非零顺序 | 是 | 是 |

两种方法的大 O 复杂度相同。交换法少一次补零遍历，但会执行交换写入；实际选择时，优先使用自己最容易正确解释和复现的版本。

#### 易错点

1. 第一遍覆盖完成后忘记把剩余区间填成零。
2. 把 `slow` 理解成“当前零的数量”；更准确地说，它是非零元素数量或下一写入位置。
3. 遇到零时也递增 `slow`，导致左侧留下空位。
4. 使用额外结果切片，违反原地修改要求。
5. 交换法移动错指针，破坏非零元素的相对顺序。

#### 建议测试案例

```text
nums = [0,1,0,3,12] → [1,3,12,0,0] // 普通情况
nums = [0]           → [0]           // 只有一个零
nums = [1]           → [1]           // 只有一个非零元素
nums = [0,0,0]       → [0,0,0]       // 全是零
nums = [1,2,3]       → [1,2,3]       // 没有零
nums = [1,0,1]       → [1,1,0]       // 相同非零元素
```

#### 来源说明

“原地栈”和“交换元素”两种解释参考了灵茶山艾府的题解。题目与题解列表：

- [LeetCode 283. 移动零](https://leetcode.cn/problems/move-zeroes/solutions/)

#### 重做记录

- 2026-07-29：完成覆盖补零法和快慢指针交换法。
- 下次目标：能够分别说出两种方法中 `slow` 的准确含义和循环不变量。

---

### 题目 15：三数之和

#### 题目摘要

- **题目链接**：[LeetCode 15. 三数之和](https://leetcode.cn/problems/3sum/)
- **输入**：整数切片 `nums []int`。
- **输出**：所有和为 `0` 且互不重复的三元组。
- **注意**：答案中的三元组不能重复，但输入数字可以重复。

核心公式：

\[
nums[i]+nums[left]+nums[right]=0
\]

固定第一个数 `nums[i]` 后，问题变为：

\[
nums[left]+nums[right]=-nums[i]
\]

这就变成了有序数组上的“两数之和”，可以使用相向双指针。

#### 写法一：基础排序 + 双指针

```go
func threeSum(nums []int) [][]int {
    sort.Ints(nums)
    result := [][]int{}

    for i := 0; i < len(nums)-2; i++ {
        if i > 0 && nums[i] == nums[i-1] {
            continue
        }

        left, right := i+1, len(nums)-1

        for left < right {
            sum := nums[i] + nums[left] + nums[right]

            if sum < 0 {
                left++
            } else if sum > 0 {
                right--
            } else {
                result = append(result, []int{
                    nums[i],
                    nums[left],
                    nums[right],
                })

                for left < right && nums[left] == nums[left+1] {
                    left++
                }
                for left < right && nums[right] == nums[right-1] {
                    right--
                }

                left++
                right--
            }
        }
    }

    return result
}
```

##### 第一步：为什么必须先排序

排序有三个作用：

1. 让双指针可以根据和的大小决定移动方向。
2. 让相同数字相邻，方便跳过重复项。
3. 把三数之和转化为固定一个数后的有序两数之和。

例如：

```text
原数组：[-1,0,1,2,-1,-4]
排序后：[-4,-1,-1,0,1,2]
```

`sort.Ints(nums)` 会直接修改输入切片。如果不能改变输入，需要先克隆：

```go
nums = slices.Clone(nums)
sort.Ints(nums)
```

##### 第二步：固定第一个数

```go
for i := 0; i < len(nums)-2; i++ {
```

`i` 最多走到倒数第三个位置，因为右边还要留出两个元素。

固定 `nums[i]` 后：

```go
left := i + 1
right := len(nums) - 1
```

- `left` 指向剩余区间最小的候选数。
- `right` 指向剩余区间最大的候选数。

##### 第三步：为什么这样移动指针

数组已经升序排列：

```go
sum := nums[i] + nums[left] + nums[right]
```

- `sum < 0`：总和太小，需要增大，执行 `left++`。
- `sum > 0`：总和太大，需要减小，执行 `right--`。
- `sum == 0`：找到答案，记录后两个指针都向中间移动。

为什么 `sum < 0` 时不能移动 `right`？

`right--` 只会让右边的数更小，总和会更小，不可能靠近 `0`。只有 `left++` 才可能让总和变大。

同理，`sum > 0` 时只有 `right--` 才能让总和变小。

##### 完整运行示例

对排序后的数组：

```text
[-4,-1,-1,0,1,2]
```

固定 `i=1`，即 `nums[i]=-1`：

| `left` 的值 | `right` 的值 | 三数之和 | 操作 |
|---:|---:|---:|---|
| `-1` | `2` | `0` | 记录 `[-1,-1,2]`，两边移动 |
| `0` | `1` | `0` | 记录 `[-1,0,1]`，两边移动 |

最终得到：

```text
[[-1,-1,2], [-1,0,1]]
```

#### 三层去重分别在防什么

三数之和最难的部分通常不是双指针，而是去重。

##### 第一层：固定数字 `nums[i]` 去重

```go
if i > 0 && nums[i] == nums[i-1] {
    continue
}
```

如果当前固定数字和上一个相同，那么当前能组成的三元组，上一次固定相同数字时已经检查过。

例如：

```text
[-1,-1,0,1]
 ↑  ↑
```

第二个 `-1` 不需要再次作为固定数字。

注意不能写成：

```go
// 错误
if nums[i] == nums[i+1] {
    continue
}
```

这样会错过 `[-1,-1,2]`，因为一个合法三元组可以使用两个数值相同但下标不同的元素。

##### 第二层：`left` 去重

找到答案后：

```go
for left < right && nums[left] == nums[left+1] {
    left++
}
```

跳过右侧连续出现、数值相同的 `left` 候选，避免生成相同三元组。

##### 第三层：`right` 去重

```go
for left < right && nums[right] == nums[right-1] {
    right--
}
```

同理，跳过左侧连续出现、数值相同的 `right` 候选。

跳过重复值以后还要：

```go
left++
right--
```

离开当前已经记录的组合，继续搜索下一组答案。

#### 写法二：加入两个边界剪枝

基础写法已经正确。下面的版本在进入双指针前，先判断当前固定数字是否还有可能组成答案：

```go
func threeSum(nums []int) (answer [][]int) {
    slices.Sort(nums)
    n := len(nums)

    for i := 0; i < n-2; i++ {
        x := nums[i]

        if i > 0 && x == nums[i-1] {
            continue
        }

        // 当前 x 能组成的最小三数和已经大于 0
        if x+nums[i+1]+nums[i+2] > 0 {
            break
        }

        // 当前 x 能组成的最大三数和仍然小于 0
        if x+nums[n-2]+nums[n-1] < 0 {
            continue
        }

        left, right := i+1, n-1

        for left < right {
            sum := x + nums[left] + nums[right]

            if sum < 0 {
                left++
            } else if sum > 0 {
                right--
            } else {
                answer = append(answer, []int{
                    x,
                    nums[left],
                    nums[right],
                })

                for left++; left < right && nums[left] == nums[left-1]; left++ {
                }
                for right--; left < right && nums[right] == nums[right+1]; right-- {
                }
            }
        }
    }

    return
}
```

##### 优化一：最小三数和已经大于 0

```go
if x+nums[i+1]+nums[i+2] > 0 {
    break
}
```

对于当前固定数字 `x`，右边最小的两个数就是：

```text
nums[i+1] 和 nums[i+2]
```

它们组成的是当前 `x` 所能得到的最小三数和。如果连最小值都大于 `0`，其他组合只会更大。

为什么这里可以直接 `break`？

后续的 `x` 还会继续变大，因此以后所有三数和也只会更大，不可能再得到 `0`。整个外层循环可以结束。

##### 优化二：最大三数和仍然小于 0

```go
if x+nums[n-2]+nums[n-1] < 0 {
    continue
}
```

数组最后两个数是最大的两个候选。如果当前 `x` 加上它们仍然小于 `0`，说明当前 `x` 太小，本轮不可能找到答案。

为什么这里只能 `continue`，不能 `break`？

后续固定数字 `x` 会变大，将来仍可能让三数和达到 `0`。因此只跳过当前 `i`，继续尝试下一个固定数字。

可以这样记：

```text
最小组合都太大 → 后面只会更大 → break
最大组合都太小 → 换个更大的 x 还有机会 → continue
```

#### 写法三：加入答案前判断重复

前两种写法是在找到答案后，用循环一次跳过所有重复的 `left` 和 `right`。

另一种写法是：指针每次只移动一步，但准备加入答案时检查当前 `left` 是否与上一次相同。

```go
func threeSum(nums []int) (answer [][]int) {
    slices.Sort(nums)
    n := len(nums)

    for i := 0; i < n-2; i++ {
        x := nums[i]

        if i > 0 && x == nums[i-1] {
            continue
        }
        if x+nums[i+1]+nums[i+2] > 0 {
            break
        }
        if x+nums[n-2]+nums[n-1] < 0 {
            continue
        }

        left, right := i+1, n-1

        for left < right {
            sum := x + nums[left] + nums[right]

            if sum < 0 {
                left++
            } else if sum > 0 {
                right--
            } else {
                if left == i+1 || nums[left] != nums[left-1] {
                    answer = append(answer, []int{
                        x,
                        nums[left],
                        nums[right],
                    })
                }

                left++
                right--
            }
        }
    }

    return
}
```

##### 去重判断是什么意思

```go
if left == i+1 || nums[left] != nums[left-1]
```

满足任意一个条件就可以记录答案：

1. `left == i+1`：双指针刚开始，左边没有本轮使用过的候选值。
2. `nums[left] != nums[left-1]`：当前左值与上一次不同，因此三元组也不同。

如果：

```go
left > i+1 && nums[left] == nums[left-1]
```

说明固定数字 `x` 没变，当前左值也和上一次一样。三数和仍为 `0` 时，右值也必然对应相同数值，所以这是重复三元组，不加入答案。

例如：

```text
nums = [-3,1,1,2,2]
```

第一次找到：

```text
[-3,1,2]
```

指针各移动一步后又得到：

```text
[-3,1,2]
```

此时新的 `left` 值仍然是 `1`，与前一个 `left` 值相同，因此跳过第二次加入。

#### 三种写法的关系

三种写法使用的是同一个主算法：

```text
排序
  → 固定 nums[i]
  → 剩余区间使用左右指针
  → 根据三数和移动指针
  → 对答案去重
```

区别主要在剪枝和去重位置：

| 对比项 | 写法一：基础版 | 写法二：边界剪枝 | 写法三：加入前去重 |
|---|---|---|---|
| 主体算法 | 排序 + 双指针 | 排序 + 双指针 | 排序 + 双指针 |
| 外层重复值 | 跳过 | 跳过 | 跳过 |
| 内层去重 | 找到后循环跳过左右重复值 | 找到后循环跳过左右重复值 | 加入答案前检查左值 |
| 上下界剪枝 | 无 | 有 | 有 |
| 可读性 | 最直观 | 性能与可读性均衡 | 更短，但去重条件较抽象 |
| 推荐顺序 | 先掌握 | 熟练后使用 | 理解去重本质后再使用 |

对于学习和面试，建议优先掌握写法一，再加上写法二的两个剪枝。写法三并没有改变复杂度，主要提供另一种去重视角。

#### 复杂度

排序需要 \(O(n\log n)\)。外层枚举固定数字最多 \(n\) 次，每次双指针最多扫描 \(n\) 个位置：

\[
O(n\log n)+O(n^2)=O(n^2)
\]

- **时间复杂度：\(O(n^2)\)**。
- **额外空间复杂度：通常记为 \(O(1)\)**，不计算返回结果，并忽略排序实现使用的栈空间。
- **副作用**：排序会修改输入数组。

虽然排序本身是 \(O(n\log n)\)，但这里还有 \(O(n^2)\) 的外层枚举加双指针，因此最终保留增长更快的 \(O(n^2)\)。

#### 易错点

1. 忘记排序，却仍根据 `sum` 大小移动左右指针。
2. 外层不去重，产生重复三元组。
3. 找到答案后只移动一个指针，或两个指针都不移动，导致重复或死循环。
4. 外层用 `nums[i] == nums[i+1]` 去重，错误跳过合法的重复数字组合。
5. 优化一应该 `break`，优化二应该 `continue`。
6. 返回的是三元组的数值，不是下标。
7. 忘记 `sort.Ints` 或 `slices.Sort` 会修改原切片。

#### 建议测试案例

```text
nums = [-1,0,1,2,-1,-4] → [[-1,-1,2],[-1,0,1]]
nums = [0,1,1]           → []
nums = [0,0,0]           → [[0,0,0]]
nums = [0,0,0,0]         → [[0,0,0]]       // 答案不能重复
nums = [-2,0,1,1,2]      → [[-2,0,2],[-2,1,1]]
nums = []                → []
```

#### 来源说明

优化剪枝和“加入答案前判断重复”的写法参考了灵茶山艾府的《极致优化！一个视频讲透双指针！》题解。题目与题解列表：

- [LeetCode 15. 三数之和](https://leetcode.cn/problems/3sum/solutions/)

#### 重做记录

- 2026-07-29：完成基础双指针、上下界剪枝和加入前去重三种写法。
- 下次目标：能独立解释三层去重，以及为什么优化一用 `break`、优化二用 `continue`。

---

### 题目 11：盛最多水的容器

#### 题目摘要

- **题目链接**：[LeetCode 11. 盛最多水的容器](https://leetcode.cn/problems/container-with-most-water/)
- **输入**：整数切片 `height []int`，`height[i]` 表示下标 `i` 处竖线的高度。
- **输出**：任选两条竖线与横轴组成容器时，能够盛放的最大水量。
- **注意**：容器不能倾斜。

如果选择下标 `left` 和 `right` 两条线：

\[
面积=(right-left)\times\min(height[left],height[right])
\]

其中：

- `right-left` 是容器宽度。
- 两条线中较短的一条决定水面高度。

#### 解法：相向双指针

```go
func maxArea(height []int) int {
    left := 0
    right := len(height) - 1
    result := 0

    for left < right {
        width := right - left
        waterHeight := min(height[left], height[right])
        currentArea := width * waterHeight
        result = max(result, currentArea)

        if height[left] < height[right] {
            left++
        } else {
            right--
        }
    }

    return result
}
```

#### 我的思路

最直接的方法是枚举所有两条线的组合：

```go
for left := 0; left < len(height); left++ {
    for right := left + 1; right < len(height); right++ {
        // 计算面积
    }
}
```

这样会检查约 \(n^2\) 个组合，时间复杂度为 \(O(n^2)\)。

双指针从数组两端开始：

```go
left := 0
right := len(height) - 1
```

此时宽度最大。之后每次把一个指针向中间移动，宽度必然减小。因此想得到更大面积，只能寄希望于决定水位的短板变高。

整个算法可以概括为：

```text
从最大宽度开始
    ↓
计算当前面积
    ↓
移动较短的一边
    ↓
尝试用更高的短板弥补宽度损失
```

#### 为什么面积由短板决定

假设：

```text
height[left] = 3
height[right] = 8
```

水面不可能超过高度 `3`，否则会从左边溢出。因此容器高度是：

```go
min(3, 8) // 3
```

这就是经典的木桶短板效应：高的那一侧再高，也无法独自提高水位。

#### 为什么每次移动较短的一边

假设当前：

```text
height[left] <= height[right]
```

当前面积为：

\[
(right-left)\times height[left]
\]

接下来宽度无论如何都会变小。

如果移动较高的右边：

- 宽度变小。
- 左边短板 `height[left]` 不变。
- 新高度最多仍然是 `height[left]`。

因此新面积一定不会比当前更大。保留短板、移动长板没有意义，可以安全排除。

如果移动较短的左边：

- 宽度仍会变小。
- 但有可能遇到更高的左边界。
- 新的短板可能升高，从而有机会抵消宽度的损失。

所以规则是：

```text
左边更短 → left++
右边更短 → right--
```

注意，这不是说移动短板后面积一定变大，而是：

> 移动短板是当前唯一仍有可能得到更大面积的选择。

#### 一个更严格的排除证明

如果 `height[left] <= height[right]`，保持 `left` 不动，任取新的右端点 `k`，其中：

\[
left<k<right
\]

新容器满足：

\[
k-left<right-left
\]

并且：

\[
\min(height[left],height[k])\le height[left]
\]

也就是说，新容器的宽度更小，高度又不可能超过当前短板，所以所有以当前 `left` 为左边界、右端点在内部的容器，都不可能超过当前面积。

因此可以一次排除当前 `left`，放心执行 `left++`。

右边较短时完全对称，可以排除当前 `right`。

#### 完整运行示例

输入：

```text
height = [1,8,6,2,5,4,8,3,7]
```

| `left` | `right` | 两侧高度 | 宽度 | 当前面积 | 移动 |
|---:|---:|---|---:|---:|---|
| 0 | 8 | `1, 7` | 8 | 8 | 左边短，`left++` |
| 1 | 8 | `8, 7` | 7 | 49 | 右边短，`right--` |
| 1 | 7 | `8, 3` | 6 | 18 | 右边短，`right--` |
| 1 | 6 | `8, 8` | 5 | 40 | 两边相等，本代码移动右边 |
| 1 | 5 | `8, 4` | 4 | 16 | 右边短，`right--` |
| 1 | 4 | `8, 5` | 3 | 15 | 右边短，`right--` |
| 1 | 3 | `8, 2` | 2 | 4 | 右边短，`right--` |
| 1 | 2 | `8, 6` | 1 | 6 | 右边短，`right--` |

最大面积为：

\[
(8-1)\times\min(8,7)=7\times7=49
\]

#### 两边高度相等时移动谁

代码写的是：

```go
if height[left] < height[right] {
    left++
} else {
    right--
}
```

当两边相等时会进入 `else`，移动右指针。也可以移动左指针，甚至同时移动两边，都不会错。

原因是两边高度相同时，当前两侧都是短板。保持其中一侧不变、只缩小宽度，不可能得到更大面积；至少可以安全排除其中任意一侧。

#### 逐行理解代码

```go
left := 0
right := len(height) - 1
```

从最宽的容器开始。

```go
for left < right {
```

两条线必须位于不同下标；相遇时宽度为零，搜索结束。

```go
currentArea := min(height[left], height[right]) * (right - left)
result = max(result, currentArea)
```

用短板高度乘以宽度，并更新历史最大面积。

```go
if height[left] < height[right] {
    left++
} else {
    right--
}
```

排除当前较短的边界，尝试寻找更高的新短板。

#### 关键不变量

每轮循环开始时：

> 所有可能超过当前最大面积、但还没有被排除的组合，其左右端点都位于闭区间 `[left,right]` 内。

每次移动短板时，我们已经证明：以被移除短板为一侧、另一侧位于当前区间内部的所有组合，都不可能优于刚计算过的当前组合。因此排除它不会漏掉最优答案。

#### 复杂度

- **时间复杂度：\(O(n)\)**。左右指针总共最多移动 \(n-1\) 次。
- **空间复杂度：\(O(1)\)**。只使用几个整数变量。
- **副作用**：不会修改输入切片。

虽然存在两个指针，但它们只向中间移动，不会回退，所以不是 \(O(n^2)\)。

#### 易错点

1. 面积高度使用较高的一边，而不是 `min`。
2. 宽度写成 `right-left+1`；这里两条竖线的水平距离是 `right-left`。
3. 每次移动较高的一边，无法排除无效候选。
4. 误以为移动短板后面积必须增大；它只是唯一可能变大的方向。
5. 计算面积后没有更新历史最大值。
6. 使用嵌套循环枚举所有组合，时间复杂度退化为 \(O(n^2)\)。

#### 建议测试案例

```text
height = [1,8,6,2,5,4,8,3,7] → 49
height = [1,1]                 → 1
height = [1,2,1]               → 2
height = [4,3,2,1,4]           → 16
height = [1,2,4,3]             → 4
```

#### 可迁移的规律

这道题展示了双指针的一个重要判断标准：

> 移动指针之前，要证明被排除的一批候选不可能包含更优答案。

这里通过“宽度必然减小”和“短板限制高度”证明可以排除短板一侧。以后遇到相向双指针问题，也应先找到类似的单调性或排除依据，而不是凭感觉移动指针。

#### 参考资料

- [代码随想录：11. 盛最多水的容器](https://programmercarl.com/hot100/0011.container-with-most-water.html)

#### 重做记录

- 2026-07-30：完成相向双指针解法与移动短板证明。
- 下次目标：不看代码，独立说明为什么移动长板不可能让面积变大。

### 5. 专题参考资料

- [Hello 算法：哈希表](https://www.hello-algo.com/chapter_hashing/hash_map/)
- [Hello 算法：哈希优化策略](https://www.hello-algo.com/chapter_searching/hashing_search/)
- [代码随想录：哈希表理论基础](https://programmercarl.com/哈希表理论基础.html)
- [代码随想录：双指针总结篇](https://programmercarl.com/algo/two-pointers/two-pointers-summary.html)
- [代码随想录：1. 两数之和](https://programmercarl.com/algo/hash-table/0001-two-sum.html)
