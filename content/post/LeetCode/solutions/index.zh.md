---
title: "LeetCode 题解手记：从思路到复盘"
description: "持续记录 LeetCode 刷题过程中的原始思路、优化过程、关键不变量、复杂度分析和易错点。专题一：哈希与双指针；专题二：滑动窗口、前缀和与区间。"
date: 2026-07-28
slug: "leetcode-solution-notes"
categories:
    - Programming
tags:
    - LeetCode
    - Algorithm
    - Hash Table
    - Two Pointers
    - Sliding Window
    - Prefix Sum
    - Intervals
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
    "math"
    "slices"
    "sort"
    "strconv"
    "strings"
    "unicode"
)
```

### 1. `strings`：处理字符串

| 方法签名 | 输入 → 输出 | 作用 | 示例 |
|---|---|---|---|
| `HasPrefix(s, prefix string) bool` | `string, string → bool` | 是否以指定前缀开头 | `strings.HasPrefix("leetcode", "leet")` → `true` |
| `HasSuffix(s, suffix string) bool` | `string, string → bool` | 是否以指定后缀结尾 | `strings.HasSuffix("main.go", ".go")` → `true` |
| `Index(s, substr string) int` | `string, string → int` | 首次出现位置；不存在返回 `-1` | `strings.Index("go gopher", "goph")` → `3` |
| `LastIndex(s, substr string) int` | `string, string → int` | 最后一次出现位置；不存在返回 `-1` | `strings.LastIndex("go gopher go", "go")` → `10` |
| `Replace(s, old, new string, n int) string` | `string, string, string, int → string` | 替换前 `n` 个匹配；`n < 0` 表示全部 | `strings.Replace("a-a-a", "a", "x", 2)` → `"x-x-a"` |
| `ReplaceAll(s, old, new string) string` | `string, string, string → string` | 替换全部匹配 | `strings.ReplaceAll("a-a-a", "a", "x")` → `"x-x-x"` |
| `Count(s, substr string) int` | `string, string → int` | 统计不重叠匹配次数 | `strings.Count("banana", "an")` → `2` |
| `Repeat(s string, count int) string` | `string, int → string` | 重复字符串 `count` 次 | `strings.Repeat("ab", 3)` → `"ababab"` |
| `ToLower(s string) string` | `string → string` | 转为小写 | `strings.ToLower("Go")` → `"go"` |
| `ToUpper(s string) string` | `string → string` | 转为大写 | `strings.ToUpper("go")` → `"GO"` |
| `TrimSpace(s string) string` | `string → string` | 删除首尾 Unicode 空白 | `strings.TrimSpace(" hi ")` → `"hi"` |
| `Trim(s, cutset string) string` | `string, string → string` | 删除首尾所有属于 `cutset` 的字符 | `strings.Trim("--go--", "-")` → `"go"` |
| `TrimLeft(s, cutset string) string` | `string, string → string` | 只清理左侧 `cutset` 字符 | `strings.TrimLeft("--go--", "-")` → `"go--"` |
| `TrimRight(s, cutset string) string` | `string, string → string` | 只清理右侧 `cutset` 字符 | `strings.TrimRight("--go--", "-")` → `"--go"` |
| `Split(s, sep string) []string` | `string, string → []string` | 按分隔符拆分全部 | `strings.Split("a,b,c", ",")` → `["a" "b" "c"]` |
| `SplitN(s, sep string, n int) []string` | `string, string, int → []string` | 最多拆成 `n` 段；`n < 0` 表示不限 | `strings.SplitN("a,b,c", ",", 2)` → `["a" "b,c"]` |
| `Join(elems []string, sep string) string` | `[]string, string → string` | 用分隔符连接 | `strings.Join([]string{"a", "b"}, "-")` → `"a-b"` |
| `Contains(s, substr string) bool` | `string, string → bool` | 是否包含子串 | `strings.Contains("gopher", "ph")` → `true` |
| `ContainsAny(s, chars string) bool` | `string, string → bool` | 是否包含 `chars` 中任意字符 | `strings.ContainsAny("team", "xyzm")` → `true` |
| `Fields(s string) []string` | `string → []string` | 按连续空白分词 | `strings.Fields("a b\tc")` → `["a" "b" "c"]` |

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

| 方法签名 | 输入 → 输出 | 作用 | 示例 |
|---|---|---|---|
| `Atoi(s string) (int, error)` | `string → int, error` | 十进制字符串转 `int` | `strconv.Atoi("123")` → `123, nil` |
| `Itoa(i int) string` | `int → string` | `int` 转十进制字符串 | `strconv.Itoa(-42)` → `"-42"` |
| `ParseInt(s string, base, bitSize int) (int64, error)` | `string, int, int → int64, error` | 按指定进制解析有符号整数 | `strconv.ParseInt("1011", 2, 64)` → `11` |
| `ParseFloat(s string, bitSize int) (float64, error)` | `string, int → float64, error` | 字符串转浮点数 | `strconv.ParseFloat("3.14", 64)` → `3.14` |
| `FormatInt(i int64, base int) string` | `int64, int → string` | 整数按指定进制转字符串 | `strconv.FormatInt(255, 16)` → `"ff"` |

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

| 方法签名 | 输入 → 输出 | 作用 | 示例 |
|---|---|---|---|
| `Ints(x []int)` | `[]int → 无返回值` | 原地升序排列整数 | `sort.Ints([]int{3, 1, 2})` → `[1 2 3]` |
| `Float64s(x []float64)` | `[]float64 → 无返回值` | 原地升序排列浮点数 | `sort.Float64s(scores)` |
| `Strings(x []string)` | `[]string → 无返回值` | 原地按字典序升序排列字符串 | `sort.Strings(words)` |
| `Slice(x any, less func(i, j int) bool)` | `切片, 比较函数 → 无返回值` | 按自定义规则原地排序 | `sort.Slice(pairs, func(i, j int) bool { return pairs[i].Value < pairs[j].Value })` |
| `Search(n int, f func(int) bool) int` | `int, func(int) bool → int` | 返回 `[0,n)` 中第一个使 `f(i)` 为真的位置；没有则返回 `n` | `sort.Search(30, func(i int) bool { return i*i >= 30 })` → `6` |
| `SearchInts(a []int, x int) int` | `[]int, int → int` | 在升序切片中返回第一个 `>= x` 的位置 | `sort.SearchInts([]int{1, 3, 3, 7}, 3)` → `1` |

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

| 方法签名 | 输入 → 输出 | 作用 | 示例 |
|---|---|---|---|
| `IsDigit(r rune) bool` | `rune → bool` | 是否为 Unicode 十进制数字 | `unicode.IsDigit('5')` → `true` |
| `IsLetter(r rune) bool` | `rune → bool` | 是否为 Unicode 字母 | `unicode.IsLetter('中')` → `true` |
| `IsLower(r rune) bool` | `rune → bool` | 是否为小写字母 | `unicode.IsLower('a')` → `true` |
| `IsUpper(r rune) bool` | `rune → bool` | 是否为大写字母 | `unicode.IsUpper('A')` → `true` |
| `IsNumber(r rune) bool` | `rune → bool` | 是否为 Unicode 数字，范围比 `IsDigit` 更广 | `unicode.IsNumber('Ⅻ')` → `true` |
| `IsSpace(r rune) bool` | `rune → bool` | 是否为空白字符 | `unicode.IsSpace('\t')` → `true` |
| `ToLower(r rune) rune` | `rune → rune` | 转为小写字符 | `unicode.ToLower('A')` → `'a'` |
| `ToUpper(r rune) rune` | `rune → rune` | 转为大写字符 | `unicode.ToUpper('a')` → `'A'` |

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

| 方法签名（简化） | 输入 → 输出 | 作用 | 示例 |
|---|---|---|---|
| `Max(x S) E` | `[]E → E` | 返回最大元素；空切片会 panic | `slices.Max([]int{3, 1, 2})` → `3` |
| `Min(x S) E` | `[]E → E` | 返回最小元素；空切片会 panic | `slices.Min([]int{3, 1, 2})` → `1` |
| `Index(s S, v E) int` | `[]E, E → int` | 首次出现位置；不存在返回 `-1` | `slices.Index([]int{3, 1, 2}, 2)` → `2` |
| `Contains(s S, v E) bool` | `[]E, E → bool` | 判断元素是否存在 | `slices.Contains([]int{3, 1, 2}, 4)` → `false` |
| `BinarySearch(x S, target E) (int, bool)` | `有序 []E, E → int, bool` | 返回匹配位置或插入位置，以及是否找到 | `slices.BinarySearch([]int{1, 3, 3, 7}, 3)` → `(1, true)` |
| `Clone(s S) S` | `[]E → []E` | 浅拷贝切片 | `copyNums := slices.Clone(nums)` |
| `Delete(s S, i, j int) S` | `[]E, int, int → []E` | 删除半开区间 `[i,j)`，必须接收返回值 | `slices.Delete([]int{1, 2, 3, 4}, 1, 3)` → `[1 4]` |
| `Sort(x S)` | `[]E → 无返回值` | 原地升序排序 | `slices.Sort(nums)` |
| `Reverse(s S)` | `[]E → 无返回值` | 原地反转 | `slices.Reverse(nums)` |
| `IsSorted(x S) bool` | `[]E → bool` | 是否按升序排列 | `slices.IsSorted([]int{1, 2, 3})` → `true` |
| `Concat(slices ...S) S` | `多个 []E → []E` | 连接多个切片并返回新切片 | `slices.Concat([]int{1, 2}, []int{3})` → `[1 2 3]` |
| `Grow(s S, n int) S` | `[]E, int → []E` | 保证还能追加至少 `n` 个元素而不重新分配 | `nums = slices.Grow(nums, 10)` |
| `Insert(s S, i int, v ...E) S` | `[]E, int, 若干 E → []E` | 在下标 `i` 前插入元素 | `slices.Insert([]int{1, 4}, 1, 9)` → `[1 9 4]` |
| `Equal(s1, s2 S) bool` | `[]E, []E → bool` | 长度和对应元素是否都相等 | `slices.Equal([]int{1, 2}, []int{1, 2})` → `true` |
| `Compare(s1, s2 S) int` | `[]E, []E → int` | 字典序比较，返回负数、`0` 或正数 | `slices.Compare([]int{1, 2}, []int{1, 3})` → `-1` |
| `Compact(s S) S` | `[]E → []E` | 合并连续重复元素 | `slices.Compact([]int{1, 1, 2})` → `[1 2]` |
| `CompactFunc(s S, eq func(E, E) bool) S` | `[]E, 相等函数 → []E` | 按自定义相等规则合并连续元素 | `slices.CompactFunc(words, strings.EqualFold)` |
| `SortFunc(x S, cmp func(E, E) int)` | `[]E, 比较函数 → 无返回值` | 按比较函数原地排序 | `slices.SortFunc(nums, func(a, b int) int { return b - a })` |

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

`cmp` 返回负数 / 0 / 正数，分别表示 `a` 排前面、二者相等、`b` 排前面；想倒序就把比较方向反过来。给区间按起点排序是 56 合并区间的前置技能：

```go
intervals := [][]int{{3, 4}, {1, 2}, {1, 5}, {2, 6}}
slices.SortFunc(intervals, func(a, b []int) int {
    if a[0] != b[0] {
        return a[0] - b[0] // 主关键字：起点升序
    }
    return a[1] - b[1] // 次关键字：终点升序
})
// [[1,2] [1,5] [2,6] [3,4]]
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
math：MinInt、MaxInt、Max、Min、Pow、Sqrt
```

完整方法签名可查阅 Go 官方文档：[strings](https://pkg.go.dev/strings)、[strconv](https://pkg.go.dev/strconv)、[sort](https://pkg.go.dev/sort)、[unicode](https://pkg.go.dev/unicode)、[slices](https://pkg.go.dev/slices)、[math](https://pkg.go.dev/math)。

### 7. `math`：数学常量与常用函数

刷题中 `math` 用得最多的不是复杂公式，而是**整数极值常量**（初始化 `ans`）和少量浮点函数。本专题的 53、560 都用到了 `math.MinInt` 初始化答案。

#### 整数极值（最常用）

| 常量 | 64 位平台上的值 | 用途 | 示例 |
|---|---|---|---|
| `math.MaxInt` | 9223372036854775807 | 求最小值时初始化 `ans` | `ans := math.MaxInt` |
| `math.MinInt` | -9223372036854775808 | 求最大值时初始化 `ans` | `ans := math.MinInt` |
| `math.MaxInt32` / `math.MinInt32` | ±2147483647 / -2147483648 | 题目范围是 32 位时 | `x := math.MinInt32` |
| `math.MaxInt64` / `math.MinInt64` | 64 位极值 | 显式指定位宽 | `x := math.MaxInt64` |

用法：

```go
ans := math.MinInt // 求最大值的问题（如 53 最大子数组和）
for _, x := range nums {
    ans = max(ans, x)
}

best := math.MaxInt // 求最小值的问题
for _, x := range nums {
    best = min(best, x)
}
```

注意：`math.MinInt` 随平台位数变化（64 位平台上就是 int64 的极值）。如果题目明确按 32 位计算，用 `math.MinInt32` / `math.MaxInt32`。

#### 浮点常量与常用函数

| 函数 / 常量 | 说明 | 示例 |
|---|---|---|
| `Inf(1)` / `Inf(-1)` | 正 / 负无穷（float64），浮点最值初始化 | `math.Inf(-1)` |
| `NaN()` | 非数字 | `math.NaN()` |
| `Max(x, y)` / `Min(x, y)` | **只接受 float64**，返回较大 / 较小值 | `math.Max(1.5, 2.5)` → `2.5` |
| `Abs(x)` | 绝对值（float64） | `math.Abs(-3.5)` → `3.5` |
| `Pow(x, y)` / `Sqrt(x)` | 幂 / 平方根（float64） | `math.Pow(2, 10)` → `1024`；`math.Sqrt(16)` → `4` |
| `Floor` / `Ceil` / `Round` / `Trunc` | 向下 / 向上 / 四舍五入 / 截断取整 | `math.Floor(2.7)` → `2` |
| `Mod(x, y)` | 浮点取模 | `math.Mod(7.5, 2)` → `1.5` |
| `Log` / `Log2` / `Log10` / `Exp` | 对数与指数 | `math.Log2(8)` → `3` |

#### 刷题最容易踩的坑

1. **`math.Max` / `math.Min` / `math.Abs` 只接受 `float64`**：传整数会编译报错。Go 1.21+ 的整数比较直接用内置 `max(a, b)` / `min(a, b)`；整数绝对值没有内置函数，自己写：
   ```go
   func abs(x int) int {
       if x < 0 {
           return -x
       }
       return x
   }
   ```
2. **`math.Pow` 返回 `float64`**：转回 `int` 可能因浮点精度丢精度。小整数幂可用，大整数幂优先用循环乘法。
3. **初始化和“比较方向”要配套**：求最大值用 `math.MinInt` 当起点，求最小值用 `math.MaxInt` 当起点；写反了答案可能整体偏移。
4. **`math.MaxInt` 需要 Go 1.17+**：LeetCode 当前 Go 版本（1.21+）没问题；老环境可以用 `math.MaxInt64` 或 `int(^uint(0) >> 1)`。

### 8. 刷题高频小抄：常用方法一行示例

把最常用的方法压成一行，方便抄：

| 场景 | 一行示例 |
|---|---|
| 去首尾空白 | `s = strings.TrimSpace(s)` |
| 按逗号拆分 | `parts := strings.Split(s, ",")` |
| 字符串切片连接 | `joined := strings.Join(parts, ",")` |
| 判断是否包含 | `strings.Contains(s, "go")` |
| 字符串转 int | `n, _ := strconv.Atoi(s)` |
| int 转字符串 | `s := strconv.Itoa(n)` |
| 升序排序 | `slices.Sort(nums)` |
| 降序排序 | `slices.SortFunc(nums, func(a, b int) int { return b - a })` |
| 按区间起点排序 | `slices.SortFunc(intervals, func(a, b []int) int { return a[0] - b[0] })` |
| 取最大 / 最小 | `slices.Max(nums)` / `slices.Min(nums)` |
| 相邻去重 | `nums = slices.Compact(nums)` |
| 反转 | `slices.Reverse(nums)` |
| 二分查找 | `i, ok := slices.BinarySearch(nums, target)` |
| 求最大值问题的起点 | `ans := math.MinInt` |
| 判断字母 / 数字 | `unicode.IsLetter(r)` / `unicode.IsDigit(r)` |

注意：`SortFunc` 里写 `b - a` 这类比较在值域极大时可能溢出，追求稳妥就用显式 `if` 比较（参考上文“给区间按起点排序”的写法）。

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

## 专题二：滑动窗口、前缀和与区间

### 1. 专题背景

专题二的目标是处理同一类问题：**连续子数组 / 连续子串 / 区间**。看到“连续”这个词，先问一句：这个区间是“活”的，还是要“算”的？

- 区间在**移动**，右端不断扩展、左端按条件收缩 → 滑动窗口。
- 区间要**求和 / 计数**，需要快速回答任意子数组的和 → 前缀和。
- 区间是**给定的一组线段**，要合并、判断重叠或覆盖 → 排序 + 扫描。

需要说明的是，hello-algo 并没有单独的“滑动窗口”或“前缀和”章节；这两者更像是把书中的基础结构“组合”出来的高频模式。本专题用到的底层内容分别来自：[数组](https://www.hello-algo.com/chapter_array_and_linkedlist/array/)（4.1）、[队列](https://www.hello-algo.com/chapter_stack_and_queue/queue/)（5.2）、[双向队列](https://www.hello-algo.com/chapter_stack_and_queue/deque/)（5.3）、[哈希表](https://www.hello-algo.com/chapter_hashing/hash_map/)（6.1）、[哈希优化策略](https://www.hello-algo.com/chapter_searching/replace_linear_by_hashing/)（10.4）、[排序算法](https://www.hello-algo.com/chapter_sorting/sorting_algorithm/)（11.1）、[动态规划](https://www.hello-algo.com/chapter_dynamic_programming/intro_to_dynamic_programming/)（14.1）与[贪心](https://www.hello-algo.com/chapter_greedy/greedy_algorithm/)（15.1）。

#### 1.1 数组：连续区间的地基

数组的元素在内存中连续排列，支持 \(O(1)\) 下标访问。滑动窗口的左右指针、前缀和的累计下标，本质都是在数组上维护一个“连续区间”。

一个连续区间可以由一对下标唯一确定：

\[
[l, r]
\]

子数组和子串都要求连续，这正是数组“连续存储”特性在算法层面的投影。链表也能表示逻辑上的连续，但没有 \(O(1)\) 随机访问，所以这类题目几乎总是给出数组或字符串。

#### 1.2 滑动窗口：让区间“滑”起来

滑动窗口维护一个连续的 `[left, right]` 区间，`right` 负责“扩展”，`left` 负责“收缩”。它的本质是把暴力枚举所有子区间 \(O(n^2)\) 变成一趟线性扫描 \(O(n)\)。

窗口可以看成队列：右端入队、左端出队。而题目 239 还需要同时取窗口最大值，普通队列只能拿到队首，无法淘汰“队内已经不可能成为最大值”的元素，这时要用双向队列维护单调递减的候选下标——这就是单调队列。

窗口的三种基本形态：

| 形态 | 窗口长度 | 收缩 / 维护方式 | 典型题目 |
|---|---|---|---|
| 变长窗口 | 不固定 | 约束被破坏时收缩 `left` | 3 无重复字符的最长子串 |
| 定长窗口 | 固定为 `k` | `right` 每走一步，`left` 同步走一步 | 438 字母异位词 |
| 单调队列 | 固定为 `k` | 维护单调性 + 淘汰过期下标 | 239 滑动窗口最大值 |

关键不变量：**窗口内始终是满足题意的合法连续区间**。`left` 移动的时机，就是“约束被破坏”的时刻。

#### 1.3 前缀和：把区间和变成两次减法

前缀和先做一次预处理：

\[
pre[i] = nums[0] + nums[1] + \cdots + nums[i-1]
\]

约定 \(pre[0]=0\)，则任意子数组的和可以写成：

\[
sum(l, r) = pre[r+1] - pre[l]
\]

这样“任意区间求和”从每次遍历 \(O(n)\) 变成 \(O(1)\)。但前缀和本身只是预处理，真正让题目 560 变快的，是配合哈希表记录“某个前缀和出现过多少次”——这正是 hello-algo 10.4 讲的**哈希优化策略**：用空间换时间，把内层查找从 \(O(n)\) 降为平均 \(O(1)\)。

#### 1.4 为什么 560 不能用普通滑动窗口

滑动窗口能保证 \(O(n)\) 的前提是：**窗口和随 `right` 扩展 / `left` 收缩具有单调性**，从而可以根据“当前和与 `target` 的大小”唯一决定移动方向。

当数组包含负数时，这个前提被破坏：`right` 扩展可能让和变小，`left` 收缩也可能让和变大，无法单调地逼近 `target`，普通滑动窗口会漏答案。因此“和为 K 的子数组”必须用前缀和 + 哈希。这是本专题面试最常被追问的点之一。

#### 1.5 两个“近亲”：DP/贪心与区间合并

- 题目 53 最大子数组和：求所有连续子数组的最大和，可以用[动态规划](https://www.hello-algo.com/chapter_dynamic_programming/intro_to_dynamic_programming/)定义“以 `i` 结尾的最大和”，也可以从[贪心](https://www.hello-algo.com/chapter_greedy/greedy_algorithm/)的角度理解“当前和何时重新开始”。
- 题目 56 合并区间：给定一组区间，先按起点[排序](https://www.hello-algo.com/chapter_sorting/sorting_algorithm/)，再逐个判断能否合并。它不再是对单个数组划窗口，而是对“区间集合”做一趟有序扫描。

这两道题放在本专题，是为了补全“连续区间”问题族的两端：一端是区间内部的**最值**，一端是区间之间的**合并**。

#### 1.6 看到题目先怎么选

| 题目信号 | 首选工具 | 关键问题 |
|---|---|---|
| 连续子串/子数组，求最长的合法区间 | 变长滑动窗口 | 约束被破坏时 `left` 如何移动 |
| 连续子串/子数组，长度固定为 `k` | 定长窗口 | 窗口计数如何维护 |
| 子数组和 = `k`，允许负数 | 前缀和 + 哈希 | 为什么不能用普通滑动窗口 |
| 连续子数组最值（最大和） | DP / 贪心 | 当前和何时重新开始 |
| 区间合并 / 重叠 / 覆盖 | 排序 + 扫描 | 合并条件和结果维护 |
| 定长窗口内的最大值 | 单调队列 | 队列中为什么要存下标 |

### 2. 本专题题目看板

题目来自当前学习清单，难度标记沿用截图中的 A/B 分组。

| 状态 | 分组 | 题号 | 题目　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 | 核心训练点　　　　　　　　　 | 笔记　　　　　　　　　　　　　　　　　　　　|
| :----:| :----:| -----:| ------------------------------------------------------------------------------------------------------| ------------------------------| ---------------------------------------------|
| ✅　　| A　　| 3　　| [无重复字符的最长子串](https://leetcode.cn/problems/longest-substring-without-repeating-characters/) | 变长滑动窗口、左指针移动时机 | [查看](#题目-3无重复字符的最长子串)　　　　 |
| ✅　　| A　　| 438　| [找到字符串中所有字母异位词](https://leetcode.cn/problems/find-all-anagrams-in-a-string/)　　　　　　| 定长窗口、窗口计数维护　　　 | [查看](#题目-438找到字符串中所有字母异位词) |
| ✅　　| A　　| 560　| [和为 K 的子数组](https://leetcode.cn/problems/subarray-sum-equals-k/)　　　　　　　　　　　　　　　 | 前缀和、哈希、负数场景　　　 | [查看](#题目-560和为-k-的子数组)　　　　　　|
| ✅　　| A　　| 53　 | [最大子数组和](https://leetcode.cn/problems/maximum-subarray/)　　　　　　　　　　　　　　　　　　　 | DP/贪心、当前和重置时机　　　| [查看](#题目-53最大子数组和)　　　　　　　　|
| ⬜　　| A　　| 56　 | [合并区间](https://leetcode.cn/problems/merge-intervals/)　　　　　　　　　　　　　　　　　　　　　　| 排序、合并条件与结果维护　　 | [查看](#题目-56合并区间)　　　　　　　　　　|
| ⬜　　| B　　| 239　| [滑动窗口最大值](https://leetcode.cn/problems/sliding-window-maximum/)　　　　　　　　　　　　　　　 | 单调队列、队列存下标的原因　 | [查看](#题目-239滑动窗口最大值)　　　　　　 |

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

### 题目 3：无重复字符的最长子串

#### 题目摘要

- **题目链接**：[LeetCode 3. 无重复字符的最长子串](https://leetcode.cn/problems/longest-substring-without-repeating-characters/)
- **输入**：字符串 `s`。
- **输出**：不含重复字符的最长子串的长度。
- **关键约束**：`s` 由英文字母、数字、符号和空格组成。
- **核心模式**：变长滑动窗口。
- **面试必须说清**：左指针何时移动，以及移动时窗口内维护的不变量。

#### 我的第一反应

> 最先想到的是暴力枚举：固定左端点 `i`，从 `j = i` 一直往右扫，遇到重复字符就停止并记录长度。思路直观但会超时，因为每个起点都要重新扫描、重新建哈希表。

#### 解法一：直觉 / 暴力解法

##### 我的思路

枚举所有子串起点 `i`，从 `j = i` 开始尽可能向右扩展，直到遇到重复字符；记录所有无重复子串的最大长度。

##### 代码

```go
func lengthOfLongestSubstring(s string) int {
    res := 0
    for i := 0; i < len(s); i++ {
        cnt := 0
        str := make(map[byte]bool)
        for j := i; j < len(s); j++ {
            if _, ok := str[s[j]]; !ok {
                str[s[j]] = true
                cnt++
            } else {
                break
            }
        }
        res = max(res, cnt)
    }
    return res
}
```

##### 复杂度

- **时间复杂度：\(O(n^2)\)**。最坏情况是没有重复字符（如 `"abcdefghij"`），每个起点都会扫到接近末尾，总扫描次数约为：
  \[
  n+(n-1)+\cdots+1=\frac{n(n+1)}{2}
  \]
- **空间复杂度：\(O(|\Sigma|)\)**。每个起点新建一个 `map`，最多保存该起点扫描到的不同字符。
- **超时原因**：\(n \le 5 \times 10^4\) 时，\(O(n^2)\) 在最坏情况下约需执行 \(10^9\) 次操作。

##### 主要关注点

暴力的浪费不在“判断重复”本身，而在换起点后把已经扫过的字符又扫了一遍：`i` 从 `0` 变到 `1` 时，`j` 从 `1` 重新开始，之前收集的信息全部丢弃。

#### 解法二：滑动窗口（哈希集合）

##### 优化突破口

暴力解法里 `i` 右移后很多字符会被重复扫描。滑动窗口用双指针维护一个**始终无重复字符**的窗口 `[left, right]`，这里有两个关键观察：

1. 如果窗口 `[left, right]` 内没有重复字符，那么**以 `right` 结尾**的最长合法子串就是整个窗口，长度是 `right-left+1`，窗口内更短的子串都不必再检查。
2. 当 `right` 遇到重复字符时，不需要回到 `right` 重新枚举，只需要收缩 `left`，直到窗口重新没有重复字符。

把两点组合起来：`right` 只向右走，`left` 也只向右走，每个字符至多“进窗口一次、出窗口一次”，整体就是一趟线性扫描。

##### 代码（我的写法）

```go
func lengthOfLongestSubstring(s string) int {
    rep := map[byte]bool{}
    left := 0
    ans := 0
    for right := 0; right < len(s); right++ {
        for rep[s[right]] { // 窗口内已有 s[right]，先收缩到重复字符被移出
            rep[s[left]] = false
            left++
        }
        rep[s[right]] = true
        ans = max(ans, right-left+1)
    }
    return ans
}
```

##### 逐行理解

- `rep`：布尔集合，记录**当前窗口内**出现过哪些字符。
- `left` / `right`：窗口的左右端点，窗口是闭区间 `[left, right]`。
- `for rep[s[right]]`：如果 `s[right]` 已经在窗口里，说明加入它会破坏“无重复”约束，必须先收缩。
- `rep[s[left]] = false; left++`：把左端字符移出窗口；当移出的恰好是窗口里那个旧的 `s[right]` 时，内层循环结束。
- `rep[s[right]] = true`：把新字符加入窗口。
- `ans = max(ans, right-left+1)`：窗口恢复合法后，用它更新最长长度。

##### 左指针何时移动（面试必须说清）

`left` 只在一种情况下移动：**`s[right]` 已经出现在窗口 `[left, right-1]` 中**。此时加入 `s[right]` 会产生重复，必须把窗口里那个旧的 `s[right]`（以及它左边的所有字符）一起移出去，才能保证窗口仍然是连续且无重复的区间。

收缩必须用 `for` 而不是 `if`：旧的重复字符不一定紧挨着 `left`，中间可能隔着多个字符，需要逐个让位。每移出一个字符就清空它在集合里的标记，直到 `rep[s[right]]` 重新为 `false`。

##### 完整运行示例：`s = "abcabcbb"`

| `right` | 字符 | 需要收缩？ | 收缩过程 | 收缩后窗口 | `ans` |
|---:|---|---|---|---|---|
| 0 | a | 否 | — | `a` | 1 |
| 1 | b | 否 | — | `ab` | 2 |
| 2 | c | 否 | — | `abc` | 3 |
| 3 | a | 是 | 移除 `a`，`left` 0→1 | `bca` | 3 |
| 4 | b | 是 | 移除 `b`，`left` 1→2 | `cab` | 3 |
| 5 | c | 是 | 移除 `c`，`left` 2→3 | `abc` | 3 |
| 6 | b | 是 | 移除 `a`、`b`，`left` 3→5 | `cb` | 3 |
| 7 | b | 是 | 移除 `c`、`b`，`left` 5→7 | `b` | 3 |

注意第 6、7 轮：收缩走了多步，这正是 `for` 而不是 `if` 的原因。

##### 复杂度

- **时间复杂度：\(O(n)\)**。`right` 走 `n` 步，`left` 至多也走 `n` 步，两者合计不超过 `2n` 次操作，因此内层虽然写成了 `for`，整体仍是线性。
- **空间复杂度：\(O(|\Sigma|)\)**。集合最多保存字符集大小的元素，本题为 ASCII，\(|\Sigma| \le 128\)。

##### 关键不变量

每轮循环结束时，窗口 `[left, right]` 内没有重复字符，且 `rep` 恰好记录窗口内字符的出现状态。正是这个不变量保证 `ans` 每次更新拿到的都是合法窗口的长度。

##### 参考写法一：计数数组（灵茶山艾府）

```go
func lengthOfLongestSubstring(s string) (ans int) {
    cnt := [128]int{} // 用数组代替 map，效率更高
    left := 0
    for right, c := range s {
        cnt[c]++
        for cnt[c] > 1 { // 窗口内有重复字母
            cnt[s[left]]-- // 移除窗口左端点字母
            left++         // 缩小窗口
        }
        ans = max(ans, right-left+1)
    }
    return
}
```

##### 参考写法二：布尔数组（灵茶山艾府）

```go
func lengthOfLongestSubstring(s string) (ans int) {
    window := [128]bool{}
    left := 0
    for right, c := range s {
        // 加入 c 之前，先移出窗口内已有的 c
        for window[c] {
            window[s[left]] = false
            left++
        }
        window[c] = true
        ans = max(ans, right-left+1)
    }
    return
}
```

##### 三种写法怎么选

| 写法 | 数据结构 | 判断重复 | 适用场景 |
|---|---|---|---|
| `map[byte]bool` | 哈希集合 | `rep[c]` 是否为 `true` | 字符集未知或较大 |
| `[128]bool` | 布尔数组 | `window[c]` | 已知 ASCII，常数更小 |
| `[128]int` | 计数数组 | `cnt[c] > 1` | 需要知道“出现几次”的扩展题 |

计数数组最通用：它不只回答“有没有重复”，还记录每个字符出现了几次。以后遇到“窗口内最多允许 `k` 个重复字符”这类变体，只需要把收缩条件改成 `cnt[c] > k`。

##### 写法三（可选）：记录上次出现下标，直接跳跃

另一种常见写法是用哈希表记录每个字符**上次出现的下标**，把逐步收缩改成直接跳跃：

```go
func lengthOfLongestSubstring(s string) int {
    last := map[byte]int{} // 字符 → 上次出现下标
    left := 0
    ans := 0
    for right := 0; right < len(s); right++ {
        if i, ok := last[s[right]]; ok && i >= left {
            left = i + 1 // 直接跳过窗口内这个重复字符
        }
        last[s[right]] = right
        ans = max(ans, right-left+1)
    }
    return ans
}
```

- 正确性依据：窗口内 `s[right]` 至多有一个旧位置，把它跳过之后，窗口左侧其余字符仍然互不重复。
- 面试价值：代码更短，但 `i >= left` 这个判断容易写漏。漏掉它，`left` 可能被跳回一个已经不在窗口内的旧位置，导致答案偏大。建议先把逐步收缩版练熟，再掌握跳跃版。

#### 对比与复盘

| 对比项 | 解法一：暴力枚举 | 解法二：滑动窗口 |
|---|---|---|
| 时间复杂度 | \(O(n^2)\) | \(O(n)\) |
| 空间复杂度 | \(O(|Σ|)\) | \(O(|Σ|)\) |
| 核心操作 | 每个起点重新扫描子串 | 每个字符至多进出窗口一次 |
| 优点 | 直观、不用思考收缩时机 | 一趟线性扫描、不超时 |
| 局限 | 换起点后重复扫描，超时 | 需要想清 `left` 的收缩时机 |

复盘：暴力的浪费在于“换起点后重复扫描”；滑动窗口让每个字符至多进出窗口一次。另外 `[128]bool` / `[128]int` 数组比 map 少一次哈希计算，常数更小。

#### 易错点

1. 收缩要用 `for` 而不是 `if`：窗口内可能连续多个字符需要让位，只收缩一次会留下重复。
2. 先收缩、再更新答案：`ans = max(ans, right-left+1)` 必须放在收缩完成之后。
3. `range s` 拿到的是 byte 索引，本题字符集是 ASCII 才能直接用 `[128]` 数组；字符集更大（如 Unicode）时要改用 `map[rune]bool` 或按字符处理。
4. 暴力写法里每个起点都新建 `map`，重复初始化的常数开销也会被 \(O(n^2)\) 放大。
5. 跳跃写法（写法三）容易漏掉 `i >= left` 判断，导致 `left` 回退、答案偏大。

#### 建议测试案例

```text
s = "abcabcbb" → 3   // 最长无重复子串是 "abc"
s = "bbbbb"    → 1   // 全是重复字符
s = "pwwkew"   → 3   // 是 "wke"，不是 "pwke"
s = "dvdf"     → 3   // "vdf"：重复字符出现在中间
s = "au"       → 2
s = " "        → 1   // 单个空格也算字符
s = ""         → 0   // 空串
```

#### 可迁移的规律

变长滑动窗口的通用三步模板：

```text
right 扩展（把新元素纳入统计）
→ 约束被破坏时，用 for 收缩 left，直到约束恢复
→ 收缩完成后更新答案
```

适用信号：求“最长 / 最短满足某约束的连续子串”。只要 `left` 单调右移，总复杂度就是 \(O(n)\)。本专题的 438（定长窗口）会在三步上做调整：长度固定后，`left` 每轮固定走一步，重点变成“窗口计数如何维护”。

#### 来源说明

- [LeetCode 3. 无重复字符的最长子串题解列表](https://leetcode.cn/problems/longest-substring-without-repeating-characters/solutions/)
- 参考视频：灵茶山艾府《一个视频讲透滑动窗口！附题单！》（滑动窗口【基础算法精讲 03】），哈希表 / 滑动窗口题单。

#### 重做记录

> 2026-08-11：暴力超时后改用滑动窗口一次通过；重做时重点检查 `left` 收缩用 `for` 的时机。

---

### 题目 438：找到字符串中所有字母异位词

#### 题目摘要

- **题目链接**：[LeetCode 438. 找到字符串中所有字母异位词](https://leetcode.cn/problems/find-all-anagrams-in-a-string/)
- **输入**：字符串 `s` 和模式串 `p`。
- **输出**：`s` 中所有 `p` 的字母异位词的起始下标数组。
- **关键约束**：只包含小写字母；子串长度固定为 `len(p)`。
- **核心模式**：定长滑动窗口。
- **面试必须说清**：窗口计数如何维护，以及如何用“计数相等”代替每次排序 / 比较。

#### 我的第一反应

> 一开始想用滑动窗口，但写着写着退回了暴力：把每个长度为 `len(p)` 的子串排序后，与排序后的 `p` 比较。思路本身没错，但有两个不舒服的地方：Go 的 `string` 不可变，排序比较必须转 `[]byte` 再转回 `string`；每个窗口都要排序一次，数据量大时一定会超时。

#### 解法一：直觉 / 暴力解法（排序 + 比较）

##### 我的思路

枚举 `s` 中所有长度为 `m = len(p)` 的子串，把子串排序后与排序后的 `p` 比较，相等就说明是异位词，记录起始下标。

##### 代码

```go
func findAnagrams(s string, p string) []int {
    cnt := len(p)
    res := []int{}
    pb := []byte(p)
    slices.Sort(pb)
    ori := string(pb)
    for right := 0; right <= len(s)-cnt; right++ {
        if slices.Contains([]byte(p), s[right]) {
            win := s[right : right+cnt]
            tmp := []byte(win)
            slices.Sort(tmp)
            new := string(tmp)
            if ori == new {
                res = append(res, right)
            }
        }
    }
    return res
}
```

##### 复杂度

记 \(n = len(s)\)，\(m = len(p)\)：

- **时间复杂度：\(O((n-m+1) \cdot m\log m)\)**。窗口数约 \(n-m+1\) 个，每个窗口都要排序一次。
- **空间复杂度：\(O(m)\)**。每个窗口拷贝一份 `[]byte` 用于排序，另有 `p` 的排序副本。
- **超时原因**：本题 \(n, m\) 均可到 \(3\times10^4\)，最坏情况接近 \(10^9\) 量级操作。

##### 主要关注点

1. **`string` 不可变**：不能像切片那样原地排序，必须 `[]byte(win)` → 排序 → `string(...)` 中转，比较起来很绕，这是这个解法别扭的根源。
2. **`[]byte(p)` 被反复创建**：`slices.Contains([]byte(p), s[right])` 每轮循环都会把 `p` 重新转成字节数组，应该提到循环外只转一次。
3. **`new` 遮蔽了内置标识符**：`new := string(tmp)` 虽然合法，但容易和内置 `new` 混淆，建议改名 `sortedWin`。
4. **`else` 分支不需要 `right++`**：`for` 循环的增量语句每轮自动执行，命中与否都会走到 `right++`；手动再加反而会跳过窗口。
5. **`slices.Contains` 只是预过滤**：窗口首字符不在 `p` 中时，整个窗口必然不是异位词。它不改变复杂度量级，去掉也正确。

#### 解法二：定长滑动窗口（两个计数数组）

##### 优化突破口

异位词的本质是“字母出现频次相同”，所以窗口的状态不需要保存字符串本身，只需要维护 26 个字母的频次。窗口长度固定为 `m`，`right` 每走一步，窗口整体右移一格，这就是定长滑窗。

##### 代码

```go
func findAnagrams(s, p string) (ans []int) {
    cntP := [26]int{} // p 的每种字母出现次数
    for _, c := range p {
        cntP[c-'a']++
    }

    cntS := [26]int{} // 当前窗口的每种字母出现次数
    for right, c := range s {
        cntS[c-'a']++ // ① 入：右端点字母进入窗口
        left := right - len(p) + 1
        if left < 0 { // 窗口长度还不足 len(p)
            continue
        }
        if cntS == cntP { // ② 判：两个频次表相同
            ans = append(ans, left)
        }
        cntS[s[left]-'a']-- // ③ 出：左端点字母离开窗口
    }
    return
}
```

##### 逐行理解

- 先统计 `p`：`cntP[c-'a']++`，得到目标频次表。
- `cntS` 始终维护当前窗口 `[right-len(p)+1, right]` 的频次（窗口未满时是 `[0, right]`）。
- 每轮循环做三件事，顺序固定：**入 → 判 → 出**。
  1. **入**：`cntS[s[right]]++`，新字母进入窗口。
  2. **判**：`left = right-len(p)+1`；`left < 0` 说明窗口还没满，跳过；满了就判断 `cntS == cntP` 是否命中。
  3. **出**：`cntS[s[left]]--`，把窗口最左边的字母移出去，为下一轮腾位置。
- **为什么出队放在判断之后**：如果先出后判，窗口就会变成 `[left+1, right]`，长度少 1，永远对不上。先判完当前完整窗口，再出队，下一轮 `right+1` 时窗口正好又是完整的。
- **为什么 `cntS == cntP` 可以直接写**：Go 的数组是值类型，`==` 会逐元素比较，`[26]int` 可以整体比较。切片 `[]int` 不能这样比较，这也是用数组而不是切片的原因之一。

##### 完整运行示例：`s = "cbaebabacd"`，`p = "abc"`

初始 `cntP = a1 b1 c1`，表中 `cntS` 用“字母+次数”表示，省略 0：

| `right` | 字符 | 入后 `cntS` | `left` | 命中？ | 出后 `cntS` |
|---:|---|---|---:|---|---|
| 0 | c | `c1` | -2 | 窗口未满 | — |
| 1 | b | `b1c1` | -1 | 窗口未满 | — |
| 2 | a | `a1b1c1` | 0 | ✅ | `a1b1` |
| 3 | e | `a1b1e1` | 1 | ❌ | `a1e1` |
| 4 | b | `a1b1e1` | 2 | ❌ | `b1e1` |
| 5 | a | `a1b1e1` | 3 | ❌ | `a1b1` |
| 6 | b | `a1b2` | 4 | ❌ | `a1b1` |
| 7 | a | `a2b1` | 5 | ❌ | `a1b1` |
| 8 | c | `a1b1c1` | 6 | ✅ | `a1c1` |
| 9 | d | `a1c1d1` | 7 | ❌ | `c1d1` |

答案：`[0, 6]`。

##### 复杂度

- **时间复杂度：\(O(26n + m)\)**。每轮 `cntS == cntP` 要逐元素比较 26 项。想去掉这个 26 的常数，可以额外维护一个 `diff` 计数器记录“还有几种字母没匹配上”，比较降为 \(O(1)\)，总复杂度降到 \(O(n+m)\)（思路同 LeetCode 76 最小覆盖子串）。
- **空间复杂度：\(O(26)\)**。两个定长数组。

##### 关键不变量

每轮循环结束时，`cntS` 恰好是窗口 `[right-len(p)+1, right]` 的频次（未满时是 `[0, right]`）。命中条件 `cntS == cntP` 等价于“窗口是 `p` 的异位词”。

#### 解法三：不定长滑动窗口（合并计数）

##### 优化突破口

解法二需要两个数组逐项比较。不定长滑窗把 `cntP` 和 `cntS` **合并成同一个数组**：

\[
cnt[x] = p\ 中\ x\ 的个数 - 窗口中\ x\ 的个数
\]

`cnt[x] >= 0` 表示窗口里 `x` 没超过 `p`；`cnt[x] < 0` 表示窗口里 `x` 太多了，需要收缩左端点。窗口不再固定长度，而是“先扩大、超了就缩”，所以叫不定长。

可以把 `cnt` 想成一张**买菜清单**：`p` 里的字母是需求（先 `+1`），窗口里的字母是已经买到手的（进来一个 `-1`）。`cnt[x] > 0` 表示 `x` 还缺，`= 0` 表示刚好，`< 0` 表示买多了，必须把窗口左边的字符“退回去”（计数加回来）。

##### 代码

```go
func findAnagrams(s, p string) (ans []int) {
    cnt := [26]int{}
    for _, c := range p {
        cnt[c-'a']++ // p 里的字母记为“需求”
    }

    left := 0
    for right, c := range s {
        c -= 'a'
        cnt[c]-- // ① 入：窗口多了一个 c，需求减一
        for cnt[c] < 0 { // ② 收缩：c 太多了
            cnt[s[left]-'a']++ // 左端点字母离开窗口，需求加一
            left++
        }
        if right-left+1 == len(p) { // ③ 判：长度对了就是异位词
            ans = append(ans, left)
        }
    }
    return
}
```

##### 逐行理解

- 初始化时 `cnt` 里是 `p` 的“需求”：`cnt[c-'a']++`。
- **入**：`cnt[c]--`，窗口每出现一个 `c`，就消耗掉一个 `c` 的需求。
- **收缩**：`cnt[c] < 0` 说明窗口里的 `c` 已经比 `p` 多了。把左端点字母放回窗外，等价于 `cnt[s[left]]++`，然后 `left++`。用 `for` 是因为可能连续多个字符都要让位。
- **判**：收缩结束后窗口合法，此时 `right-left+1 == len(p)` 就说明命中。

##### 为什么只需要检查刚进入的字母 `c`

进入 `c` 之前，窗口是合法的：所有 `cnt[x] >= 0`。入窗操作只把 `cnt[c]` 减 1，其它字母的计数完全不变，所以唯一可能变成负数的就是 `c`。因此收缩循环只需判断 `cnt[c] < 0`，不需要重新检查全部 26 个字母。

##### 为什么长度等于 `len(p)` 就一定是异位词

收缩结束后，对任意字母 \(x\) 都有 \(cnt[x] \ge 0\)。把所有字母的计数加起来：

\[
\sum_{x} cnt[x] = \left(\sum_{x} p 中 x 的个数\right) - \left(\sum_{x} 窗口中 x 的个数\right) = len(p) - 窗口长度
\]

如果窗口长度等于 \(len(p)\)，则 \(\sum cnt[x] = 0\)。而每一项都 \(\ge 0\)，总和为 0 只能说明每一项都等于 0，即窗口频次与 `p` 完全一致。反过来，如果频次完全一致，窗口长度必然是 \(len(p)\)。所以“窗口长度 == len(p)”和“是异位词”完全等价。

##### 为什么不会漏掉答案

如果某个异位词从下标 `i` 开始，那么当 `right` 走到 `i + len(p) - 1` 时，窗口正好是这段子串：每个字母的需求都刚好被满足，没有任何计数变负，不会触发收缩，而长度又恰好是 `len(p)`，所以一定会被记录。

收缩只发生在“某种字母超量”时，而合法的异位词窗口恰好不超量，因此它永远不会被收缩挤掉。

##### 为什么 `left` 右移不会把答案跳过

关键：`left` 移动不是“猜”，而是“排除”。

假设这一步进入了字母 `c`，且 `cnt[c]` 变成 -1，说明窗口 `[left, right]` 里 `c` 比 `p` 多一个。`left` 一直右移，直到把窗口里第一个 `c` 挤出去。那么被跳过的每个起点 `s`（从旧 `left` 到新 `left-1`），窗口 `[s, right]` 里仍然同时包含那个老的 `c` 和刚进来的 `c`——`c` 依然超量，所以这些起点在当前 `right` 下必然不可能是异位词，丢掉是安全的。

例如 `p = "aa"`、`s = "baa"`：`right = 0` 进来 `b` 后 `cnt[b] = -1`，`left` 直接从 0 跳到 1。被跳过的起点 0 对应窗口 `"baa"`，含 `b`，永远不可能是 `"aa"` 的异位词。

另一个角度：对每个 `right`，收缩停止后的窗口 `[left, right]` 是“以 `right` 结尾、所有计数都不为负”的最大窗口。如果以 `right` 结尾真的存在异位词，它不超量，所以它是这个最大窗口的一个后缀；而它的长度又恰好是 `len(p)`，因此最大窗口的长度也只能是 `len(p)`——两者是同一个窗口。所以只要 `right` 处有答案，就一定在这一轮被记录，不会漏。

##### 完整运行示例一：`s = "baab"`，`p = "ab"`（先看这个小例子）

目标长度 `m = 2`，初始清单 `cnt = a1 b1`。表中 `cnt` 用“字母+剩余需求”表示，省略 0：

| `right` | 字符 | 入窗后 `cnt` | 负数？ | 收缩 | 窗口 | 命中？ |
|---:|---|---|---|---|---|---|
| 0 | a | `a0 b1` | 无 | 无 | `a` | ❌（长度 1） |
| 1 | b | `a0 b0` | 无 | 无 | `ab` | ✅ 记录 0 |
| 2 | a | `a-1 b0` | a 多了 | 挤出 `a`，-1→0，`left` 0→1 | `ba` | ✅ 记录 1 |
| 3 | b | `a0 b-1` | b 多了 | 挤出 `b`，-1→0，`left` 1→2 | `ab` | ✅ 记录 2 |

答案 `[0, 1, 2]`。第 2 轮是理解不定长的关键：窗口先变成 `aba`，a 超量，挤掉一个 a 后缩成 `ba`，长度恰好为 2，命中。

##### 完整运行示例二：`s = "cbaebabacd"`，`p = "abc"`

初始 `cnt = a1 b1 c1`，只列关键轮次：

| `right` | 字符 | 入后变化 | 收缩过程 | 窗口 | 命中？ |
|---:|---|---|---|---|---|
| 2 | a | `a1→a0` | 无 | `cba` | ✅ |
| 3 | e | `e0→e-1` | `c b a e` 依次出窗，`left` 0→4 | 空 | ❌ |
| 6 | b | `b0→b-1` | `b` 出窗，`left` 4→5 | `ab` | ❌（长度 2） |
| 7 | a | `a0→a-1` | `a` 出窗，`left` 5→6 | `ba` | ❌（长度 2） |
| 8 | c | `c1→c0` | 无 | `bac` | ✅ |

第 3 轮最能体现“为什么收缩要用 `for`”：`e` 根本不在 `p` 里，需求直接变成 -1，必须把窗口里的 `c b a e` 全部移出去，`left` 连续走 4 步。

##### 复杂度

- **时间复杂度：\(O(n+m)\)**。`right` 走 \(n\) 步；`left` 至多右移 \(n\) 次，内层循环总执行次数不超过 \(n\)，整体线性。
- **空间复杂度：\(O(26)\)**。一个定长数组。

#### 对比与复盘

| 对比项 | 解法一：排序暴力 | 解法二：定长滑窗 | 解法三：不定长滑窗 |
|---|---|---|---|
| 时间复杂度 | \(O((n-m+1)\cdot m\log m)\) | \(O(26n + m)\) | \(O(n + m)\) |
| 空间复杂度 | \(O(m)\) | \(O(26)\) | \(O(26)\) |
| 核心操作 | 每个窗口排序后比较 | 两个频次表逐轮比较 | 需求-存量表，负值收缩 |
| 优点 | 最直观、不易写错 | 思路直白，Go 数组可直接 `==` | 线性时间、无逐项比较 |
| 局限 | 每窗排序，超时 | 每轮比较 26 项 | 需要理解负数收缩与长度证明 |

面试建议：先讲定长滑窗（容易说清），再补充不定长滑窗的线性优化，重点讲“为什么长度等于 `len(p)` 就是命中”。

#### 易错点

1. 定长滑窗的顺序必须是**入 → 判 → 出**：先出后判会让窗口永远少一个字符。
2. `left < 0` 时窗口还没满，只入不出，不能参与比较。
3. 不定长滑窗的收缩用 `for` 不是 `if`：进入的字母可能完全不在 `p` 里，要一直收缩到把它移出窗口。
4. 合并计数法里 `cnt` 的加减方向别搞反：`p` 的字母 +1（需求），窗口的字母 -1（消耗）。
5. 下标用 `c-'a'` 的前提是题目保证小写字母；字符集更大时要改用 `[256]int` 或 `map[rune]int`。
6. `[26]int` 可以整体 `==`，但切片 `[]int` 不能，别把数组换成切片后还直接比较。
7. 返回的是起始下标 `left`，不是窗口内容或结束下标。
8. 定长写法里 `range s` 的 `right` 是字节下标：本题只有小写 ASCII，字节下标与字符下标一致才成立。

#### 建议测试案例

```text
s = "cbaebabacd", p = "abc" → [0, 6]
s = "abab",       p = "ab"  → [0, 1, 2]     // 窗口重叠
s = "aaaa",       p = "aa"  → [0, 1, 2]
s = "baa",        p = "aa"  → [1]
s = "ab",         p = "abc" → []            // p 比 s 长
s = "",           p = "a"   → []
s = "aaaaaaaaaa", p = "aaaaaaaaaa" → [0]    // 整串命中
```

#### 可迁移的规律

- **异位词 = 频次相等**：看到“字母异位词”直接想计数数组，不要再排序比较。
- **定长滑窗模板**：入 → 判 → 出；窗口左端 `left = right - len + 1`，`left < 0` 时窗口未满。
- **不定长滑窗模板**：入 → 计数为负就收缩 → 长度达到目标时更新答案。
- 与题目 3 的对比：题目 3 的窗口长度不固定、靠“约束被破坏”收缩；438 定长版靠固定长度触发判断，不定长版靠“需求变负”收缩。

#### 来源说明

- [LeetCode 438. 找到字符串中所有字母异位词题解列表](https://leetcode.cn/problems/find-all-anagrams-in-a-string/solutions/)
- 参考视频：灵茶山艾府《题解两种方法：定长滑窗/不定长滑窗》，字符串 / 滑动窗口。

#### 重做记录

> 2026-08-11：先写了排序暴力（string 不可变、比较绕），后补定长/不定长两种滑窗；重做时重点检查入→判→出顺序、`cnt` 加减方向，以及不定长收缩用 `for`。

---

### 题目 560：和为 K 的子数组

#### 题目摘要

- **题目链接**：[LeetCode 560. 和为 K 的子数组](https://leetcode.cn/problems/subarray-sum-equals-k/)
- **输入**：整数数组 `nums` 和整数 `k`。
- **输出**：和为 `k` 的连续子数组个数。
- **关键约束**：`nums` 可能包含负数；子数组必须连续。
- **核心模式**：前缀和 + 哈希。
- **面试必须说清**：为什么不能用普通滑动窗口，以及 `pre[0] = 0` 为什么必须提前放进哈希表。

#### 我的第一反应

> 第一反应是枚举所有起点 `i` 和终点 `j` 算区间和，但这是 \(O(n^2)\)。随后想到滑动窗口，可数组里有负数，窗口和既不随 `right` 扩展单调增加、也不随 `left` 收缩单调减少，没法确定移动方向——这条路走不通。正确工具是前缀和 + 哈希表。

#### 前置背景：前缀和（这类题型的公共知识）

##### 定义

前缀和数组 `s` 的长度是 `n+1`：

\[
s[0] = 0,\quad s[i] = nums[0] + nums[1] + \cdots + nums[i-1]
\]

`s[i]` 表示**前 i 个元素**的和，`s[0]=0` 表示空前缀。

##### 核心公式（先死死记住）

\[
s[j] - s[i] = nums[i] + nums[i+1] + \cdots + nums[j-1]
\]

任意子数组 `nums[i .. j-1]` 的和，等于两个前缀和的差。有了 `s`，任意区间和都能 \(O(1)\) 得到，不用再遍历。

##### 什么时候想到前缀和

- 题目在问“连续子数组的**和**”或“任意区间和”。
- 需要频繁回答区间和查询。
- 模板题：[LeetCode 303. 区域和检索 - 数组不可变](https://leetcode.cn/problems/range-sum-query-immutable/)。
- 相关概念：差分是前缀和的逆运算，常用于区间批量加减。

#### 解法一：暴力枚举（超时）

##### 我的思路

枚举每个起点 `i`，从 `i` 开始向右累加，累加和等于 `k` 就计数。

##### 代码

```go
func subarraySum(nums []int, k int) int {
    n := len(nums)
    ans := 0
    for i := 0; i < n; i++ {
        sum := 0
        for j := i; j < n; j++ {
            sum += nums[j]
            if sum == k {
                ans++
            }
        }
    }
    return ans
}
```

##### 复杂度

- **时间复杂度：\(O(n^2)\)**。枚举所有子数组。
- **空间复杂度：\(O(1)\)**。
- **超时原因**：\(n \le 2\times10^4\)，\(O(n^2)\) 最坏约 \(4\times10^8\) 次累加。

#### 解法二：前缀和 + 哈希表（两次遍历）

##### 优化突破口：移项，把“算差”变成“找数”

把核心公式代入本题条件 \(s[j] - s[i] = k\)，移项得到：

\[
s[i] = s[j] - k
\]

问题从“枚举两个前缀和算差”变成：**枚举右端点 `j`，在左边的历史前缀和里找，有多少个等于 `s[j]-k`**。

每个满足条件的 `s[i]` 都和当前的 `s[j]` 配对成一个和为 `k` 的子数组。这是两数之和的“计数版”：两数之和问“补数在不在”，这里问“补数出现过几次”。

##### 代码（写法一：先建好前缀和数组）

```go
func subarraySum(nums []int, k int) (ans int) {
    s := make([]int, len(nums)+1)
    for i, x := range nums {
        s[i+1] = s[i] + x
    }

    cnt := make(map[int]int, len(s)) // key：前缀和的值；value：出现过几次
    for _, sj := range s {
        ans += cnt[sj-k] // ① 查：左边有多少个 s[i] = sj-k
        cnt[sj]++        // ② 记：把当前前缀和入档
    }
    return
}
```

##### 为什么哈希表是“边走边建”的（本题最关键的直觉）

先接受两个前提：

1. 我们要找的数是 `s[j]-k`，而 `s[j]` 每走一步都在变，所以**“要找的数”不是固定的**。
2. `i` 必须严格在 `j` 左边（子数组不能为空），所以能用来配对的，只有 `j` **之前**出现过的前缀和。

因此哈希表里永远只存“已经走过的前缀和”，每步做两件事，顺序固定：

- **先查**：`ans += cnt[sj-k]`，用当前目标去历史里找配对；
- **再记**：`cnt[sj]++`，把当前前缀和入档，供后面的 `j` 查询。

这就是“在找数字的过程中不断完善哈希表”：**查询目标每步在变，哈希表每步在长大，二者同步推进**。像爬山时沿途撒标记：每到一个新点，先回头数一数“之前有没有人撒过我要的标记”，数完再在自己脚下撒一个，让后来的人能数到你。

##### 为什么先查后记，顺序不能反

`i < j`，自己不能和自己配对。如果先记后查，`k = 0` 时会把自己也算进去。

反例：`nums = [2]`，`k = 0`，正确答案是 0。若先 `cnt[2]++` 再 `ans += cnt[2-0]`，就会把“自己和自己”错算成一个子数组，答案变成 1。

##### 为什么 `s[0] = 0` 必须在表里

子数组可能从下标 0 开始：`nums[0 .. j-1]` 的和是 `s[j] - s[0]`。没有 `s[0]=0` 这个“空前缀”，从头开始的子数组就没人能配对。

反例：`nums = [1]`，`k = 1`。遍历到 `s[1]=1` 时，要查 `cnt[0]`，`s[0]=0` 必须已经在表里，才能数出这一个子数组。

##### 为什么这样做不重不漏

暴力做法是外层枚举 `j`、内层枚举 `i`，判断 `s[j]-s[i]=k`。这里保留了外层“枚举 `j`”，只是把内层线性查找换成了哈希表查询。

对任意一对满足条件的 `(i, j)`：当循环走到 `j` 时，`s[i]` 一定已经入档（因为 `i < j`），所以这一对**恰好在这一步被数到一次**。`i = j` 或 `i > j` 的情况永远不会被数到，因为表里只有 `j` 之前的前缀和。因此不重不漏。

##### 完整运行示例：`nums = [1,1,-1,1,-1]`，`k = 1`

前缀和数组 `s = [0,1,2,1,2,1]`。表里列出每一步“要找的数、命中几个、入档后的哈希表”：

| `j` | `s[j]` | 要找的数 `s[j]-k` | 命中数 | 本步之后 `cnt` | 累计 `ans` |
|---:|---:|---:|---:|---|---:|
| 0 | 0 | -1 | 0 | `{0:1}` | 0 |
| 1 | 1 | 0 | 1（`s[0]`） | `{0:1, 1:1}` | 1 |
| 2 | 2 | 1 | 1（`s[1]`） | `{0:1, 1:1, 2:1}` | 2 |
| 3 | 1 | 0 | 1（`s[0]`） | `{0:1, 1:2, 2:1}` | 3 |
| 4 | 2 | 1 | 2（`s[1]`、`s[3]`） | `{0:1, 1:2, 2:2}` | 5 |
| 5 | 1 | 0 | 1（`s[0]`） | `{0:1, 1:3, 2:2}` | 6 |

答案 6。注意第 4 行：`s[1]` 和 `s[3]` 都等于 1，所以一步命中 2 个——这就是 value 存“次数”而不是“是否存在”的原因。

##### 复杂度

- **时间复杂度：\(O(n)\)**。建前缀和一遍，遍历哈希一遍。
- **空间复杂度：\(O(n)\)**。前缀和数组加哈希表。

#### 解法三：一次遍历（边算边查）

##### 优化突破口

前缀和 `s[i+1]` 只依赖 `s[i]`，不需要真的把整个数组存下来：用一个变量 `s` 滚动累加即可。区别只在于“什么时候把哪个前缀和放进哈希表”。

##### 写法二：预置 `cnt[0] = 1`

```go
func subarraySum(nums []int, k int) (ans int) {
    cnt := make(map[int]int, len(nums)+1)
    cnt[0] = 1 // s[0]=0 单独统计
    s := 0
    for _, x := range nums {
        s += x
        ans += cnt[s-k] // 先查
        cnt[s]++        // 再记
    }
    return
}
```

写法二就是写法一的压缩版：把“遍历前缀和数组”换成“边算边遍历”，少掉的那一次循环正是对 `s[0]=0` 的统计，所以开头手动 `cnt[0]=1`。

##### 写法三：每轮先记上一个前缀和

```go
func subarraySum(nums []int, k int) (ans int) {
    cnt := make(map[int]int, len(nums))
    s := 0
    for _, x := range nums {
        cnt[s]++ // 先记：把“还未包含 x 的前缀和”入档
        s += x   // 再算：前缀和推进一位
        ans += cnt[s-k] // 后查
    }
    return
}
```

写法三不初始化 `cnt[0]=1`，而是把“记”挪到每轮开头：进入第 `t` 轮时，`s` 还是前 `t` 个元素的前缀和 `s[t]`，先把它入档，再累加得到 `s[t+1]` 去查询。这样表里始终是“当前 `j` 之前”的前缀和，效果和写法二完全一样。

三种写法的顺序口诀：

```text
写法一：先建表 → 逐项【查 → 记】
写法二：【预置 cnt[0]=1】→ 每轮【加 → 查 → 记】
写法三：每轮【记旧的 s → 加 → 查】
```

##### 写法二和写法三到底差在哪

两版代码做的事完全一样：**保证查询的那一刻，表里恰好是 `j` 之前的所有前缀和**。区别只有两点：

- `s[0]=0` 什么时候进表：写法二在循环外预置 `cnt[0]=1`；写法三在第一轮开头的 `cnt[s]++` 里顺带入表。
- 每轮“记”的位置：写法二先 `s += x` 再记（记的是**新**前缀和）；写法三先记再 `s += x`（记的是**旧**前缀和）。

| 对比项 | 写法二（其一） | 写法三（其二） |
|---|---|---|
| 初始表 | 预置 `cnt[0]=1` | 空表 |
| 每轮顺序 | 加 → 查 → 记 | 记 → 加 → 查 |
| 每轮记的是 | 加 `x` 之后的新前缀和 | 加 `x` 之前的旧前缀和 |
| `s[0]=0` 何时入表 | 循环外手动 | 第一轮开头自动 |
| 查询时表里 | `S[0..t]` | `S[0..t]`（完全一样） |

用 `nums=[1,1,-1,1,-1]`、`k=1` 看前两轮：

```text
写法二（预置 {0:1}）：
第 0 轮：s 0→1，查 cnt[0]=1 → ans=1，记 cnt[1]
第 1 轮：s 1→2，查 cnt[1]=1 → ans=2，记 cnt[2]

写法三（空表）：
第 0 轮：记 cnt[0]=1，s 0→1，查 cnt[0]=1 → ans=1
第 1 轮：记 cnt[1]=1，s 1→2，查 cnt[1]=1 → ans=2
```

查询的那一刻，两版表里的内容一模一样（第 1 轮都是 `{0:1, 1:1}`），算出的 `ans` 也一模一样。区别只是“记”发生在“加”之前还是之后——写法二记新值，写法三记旧值。面试推荐写写法二（更直白），写法三作为技巧了解即可。

##### 复杂度

- **时间复杂度：\(O(n)\)**。一趟遍历。
- **空间复杂度：\(O(m)\)**，`m` 为不同前缀和的个数，最坏 \(O(n)\)。

#### 总结：前缀和 + 哈希表到底在干嘛

把这几轮反复绕的点收拢成一条完整链路：

1. **子数组和是“落差”，不是“高度”**：任意子数组的和 = 两个前缀和之差 `s[j]-s[i]`。所以“和为 k”=“找两对前缀和，差为 k”，不是在数组里找一个值等于 k 的段。
2. **移项，把“算差”变成“找数”**：`s[i] = s[j]-k`。站在 `j` 时，要找的历史值 = `s[j]-k`，这个目标每轮都在变（例如 `s=[0,1,3,6]`、`k=3` 时，目标依次是 -2、0、3）。
3. **历史表边走边建**：表里永远只有“已经走过的前缀和”。每轮两个动作，顺序固定：
   - 查：`ans += cnt[s[j]-k]`；
   - 记：`cnt[s[j]]++`。
4. **key 是前缀和的值，不是下标**：`cnt[s[i]]++` 表示“值 `s[i]` 出现次数 +1”。同一个值出现在不同位置会合并成一条记录（例如 `s=[0,1,0,3]` 中值 0 出现两次，`cnt[0]=2`）。
5. **value 是次数，不是是否存在**：同一个目标值可能对应多段子数组（例：`nums=[1,-1,3]`，最后一轮 `cnt[0]=2`，一步加 2）。
6. **先查后记**：保证 `i<j`；`k=0` 时不会把自己配成空子数组。
7. **`s[0]=0` 必须能查到**：从头开始的子数组（前缀本身）靠它配对。
8. **写法二/三只是“记的时机”不同**：一个记新值，一个记旧值，查询那一刻的表完全相同。

一句话版：**每轮用当前前缀和减去 k，去历史表里数这个值出现过几次；出现几次，就有几段以 j 结尾、和为 k 的子数组。**

#### 对比与复盘

| 对比项 | 解法一：暴力 | 解法二：两次遍历 | 解法三：一次遍历 |
|---|---|---|---|
| 时间复杂度 | \(O(n^2)\) | \(O(n)\) | \(O(n)\) |
| 空间复杂度 | \(O(1)\) | \(O(n)\) | \(O(m)\) |
| 核心操作 | 枚举所有子数组 | 建前缀和后查表 | 边算边查 |
| 优点 | 最直观 | 思路分两步、好讲 | 代码最短 |
| 局限 | 超时 | 多一个前缀和数组 | 顺序容易记混 |

面试建议：先讲“移项 + 枚举右、维护左”，再写一次遍历版本；重点把“先查后记”和 `s[0]=0` 两个点说清楚。

#### 易错点

1. **先查后记的顺序不能反**：`k = 0` 时先记后查会把空前缀错算成子数组。
2. **漏掉 `s[0]=0`**：从头开始的子数组（前缀本身）无法配对；写法二必须手动 `cnt[0]=1`。
3. **误用滑动窗口**：数组含负数时窗口和没有单调性，滑动窗口会漏答案；只有全非负的“恰好型”子数组才适合滑窗（如 930）。
4. **把计数写成存在性判断**：`ans += cnt[s-k]` 累加次数，不是 `if cnt[s-k] > 0 { ans++ }`。
5. **前缀和数组长度写错**：长度是 `n+1`，`s[0]=0`。
6. **以为 key 不能为负**：`nums[i]` 范围是 `[-1000, 1000]`，前缀和完全可能是负数，哈希表 key 允许负数。

#### 建议测试案例

```text
nums = [1,1,1]         k = 1 → 3
nums = [1,2,3]         k = 3 → 2          // [1,2] 和 [3]
nums = [1,1,-1,1,-1]   k = 1 → 6
nums = [1,-1,0]        k = 0 → 3          // [1,-1]、[0]、[1,-1,0]
nums = [-1,-1,1]       k = 0 → 1          // [-1,1]
nums = [2]             k = 0 → 0          // 先查后记的反例
nums = [1]             k = 1 → 1          // s[0]=0 的反例
```

#### 可迁移的规律

- **连续子数组和问题 → 前缀和**：任意区间和等于两个前缀和之差。
- **“找有多少对满足差为 k” → 枚举右、维护左 + 哈希表**：这是两数之和的计数版，value 存出现次数。
- **滑动窗口的边界**：只有窗口和具有单调性（通常要求元素非负）才能用滑动窗口；含负数时转向前缀和 + 哈希。
- **变形题**：[930. 和相同的二元子数组](https://leetcode.cn/problems/binary-subarrays-with-sum/)（只有 0/1，可滑窗）、[1248. 统计优美子数组](https://leetcode.cn/problems/count-number-of-nice-subarrays/)（奇数映射为 1）、[974. 和可被 K 整除的子数组](https://leetcode.cn/problems/subarray-sums-divisible-by-k/)（同余）。

#### 来源说明

- [LeetCode 560. 和为 K 的子数组题解列表](https://leetcode.cn/problems/subarray-sum-equals-k/solutions/)
- [LeetCode 303. 区域和检索 - 数组不可变（前置模板题）](https://leetcode.cn/problems/range-sum-query-immutable/)
- 参考视频：灵茶山艾府《前缀和+哈希表：从两次遍历到一次遍历，附变形题》，哈希表 / 前缀和。

#### 重做记录

> 2026-08-16：用灵茶山艾府三版写法完成；重做时重点检查先查后记顺序、`s[0]=0`，以及能否独立讲清“边走边建”的哈希表。
> 2026-08-16：补充“差值 vs 数值”、历史表建表过程与一次遍历两版写法区别的小结。

---

### 题目 53：最大子数组和

#### 题目摘要

- **题目链接**：[LeetCode 53. 最大子数组和](https://leetcode.cn/problems/maximum-subarray/)
- **输入**：整数数组 `nums`。
- **输出**：具有最大和的连续子数组的和。
- **关键约束**：子数组至少包含一个元素；`nums` 可能包含负数。
- **核心模式**：DP / 贪心。
- **面试必须说清**：当前和何时重新开始（何时丢弃之前的累计和）。

#### 我的第一反应

> 第一反应是前缀和：子数组和 = 两个前缀和的差，问题变成“找 `pre[i] - pre[j]` 的最大值”。固定 `pre[i]`，在左边找一个最小的 `pre[j]` 就能得到最大差值。但第一次写把“更新最小值”和“算差值”的顺序写反了，把空子数组算进了答案。动态规划一开始没看懂，本质是“续接或重开”。

#### 解法一：前缀和 + 贪心

##### 优化突破口

子数组和等于两个前缀和的差，所以求出前缀和后，问题就变成 [121. 买卖股票的最佳时机](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/)：把 `pre[j]` 当成买入价，`pre[i]` 当成卖出价（`i > j`），求最大利润。一边遍历计算前缀和，一边维护“最小的前缀和”（最低买入价），当前前缀和减去它，就是以当前元素结尾的最大子数组和。

##### 代码（正确版）

```go
func maxSubArray(nums []int) int {
    ans := math.MinInt
    minPreSum := 0 // 初始 pre[0]=0，空前缀
    preSum := 0
    for _, x := range nums {
        preSum += x // 当前的前缀和 pre[i]
        ans = max(ans, preSum-minPreSum)   // 先算：减去左边最小前缀和
        minPreSum = min(minPreSum, preSum) // 后更：维护最小前缀和
    }
    return ans
}
```

##### 为什么必须先算后更新（我踩过的坑）

`minPreSum` 是一个“池子”，专门放**减数候选人 j**，而 j 必须 < i。当前这个 `pre[i]` 只能给下一轮的 `i+1` 当 j，绝不能给自己当 j。

- **正确顺序**：先用池子里已有的旧数据算账，然后才把自己丢进池子，留给后面用。
- **错误顺序**：先把自己丢进池子，立刻就能拿自己减自己 → `j = i` → 空子数组（差值 0）混进答案。

我第一版就写反了：

```go
// 错误版：先更新最小值，再算差值
for _, v := range pre {
    cnt = min(v, cnt)    // ❌ 先入池
    ans = max(v-cnt, ans) // 再算账 → 空子数组混进答案
}
```

反例：`nums = [-1]`。若先 `minPreSum = min(0, -1) = -1` 再算 `-1-(-1) = 0`，答案变成 0；正确顺序先算 `-1-0 = -1`，答案才是 -1。

万能口诀：**旧数据先干活，干完活再把自己加入池子给后面用**。更短版：**先算账，再入池；先入池，必翻车。**

##### 为什么不能直接“最大前缀和 - 最小前缀和”

子数组必须右边的前缀和减左边的前缀和。如果最大前缀和出现在最小前缀和左边，二者相减不满足 `i > j`。例如 `nums=[1,-2]`：最大前缀和是 1（pre[1]），最小前缀和是 -1（pre[2]），直接相减得 2，正确答案是 1。

##### 完整运行示例：`nums = [-2,1,-3,4,-1,2,1,-5,4]`

| 元素 | 前缀和 | 最小前缀和 | 前缀和 - 最小前缀和 |
|---|---:|---:|---:|
| -2 | -2 | 0 | -2 |
| 1 | -1 | -2 | 1 |
| -3 | -4 | -2 | -2 |
| 4 | 0 | -4 | 4 |
| -1 | -1 | -4 | 3 |
| 2 | 1 | -4 | 5 |
| 1 | 2 | -4 | 6 |
| -5 | -3 | -4 | 1 |
| 4 | 1 | -4 | 5 |

“前缀和 - 最小前缀和”的最大值 = 6，即答案。

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(1)\)**。滚动一个前缀和变量，不需要前缀和数组。

#### 解法二：动态规划

##### 核心定义

\[
f[i] = 以 nums[i] 结尾的最大子数组和
\]

为什么用“以 i 结尾”而不是“前 i 个元素”？因为子数组必须连续：任何一个以 `nums[i]` 结尾的子数组，只有两种来源——从 i 这里**重新开始**，或者**接在**某个“以 nums[i-1] 结尾”的子数组后面。

##### 分类讨论

站在 i 这个位置，最好的“以 i 结尾”的子数组只能是：

1. 自己单独开一段：`f[i] = nums[i]`；
2. 接上 i-1 的最佳段：`f[i] = f[i-1] + nums[i]`。

两种情况取最大：

\[
f[i] = \max(nums[i],\; f[i-1]+nums[i]) = \max(f[i-1], 0) + nums[i]
\]

##### 为什么可以写成 `max(f[i-1], 0)`

`max(nums[i], f[i-1]+nums[i])` 等价于 `max(f[i-1], 0) + nums[i]`：

- `f[i-1] ≥ 0`：接上去只会加分，取 `f[i-1]+nums[i]`；
- `f[i-1] < 0`：接上去反而拖累，不如从 0 重新开始，取 `nums[i]`。

**“当前和何时重新开始”的答案：前一段的和是负数，就归零重开。**

##### 完整运行示例：`nums = [-2,1,-3,4,-1,2,1,-5,4]`

| i | nums[i] | 续：f[i-1]+x | 新开：x | f[i] | ans |
|---|---:|---:|---:|---:|---:|
| 0 | -2 | — | -2 | -2 | -2 |
| 1 | 1 | -1 | 1 | 1 | 1 |
| 2 | -3 | -2 | -3 | -2 | 1 |
| 3 | 4 | 2 | 4 | 4 | 4 |
| 4 | -1 | 3 | -1 | 3 | 4 |
| 5 | 2 | 5 | 2 | 5 | 5 |
| 6 | 1 | 6 | 1 | 6 | 6 |
| 7 | -5 | 1 | -5 | 1 | 6 |
| 8 | 4 | 5 | 4 | 5 | 6 |

i=2 时 `f[1]=1` 是正的，续出来 -2 比新开 -3 好，选续；i=3 时 `f[2]=-2` 是负的，新开 4 更好，于是从 4 重新开始。

##### 为什么答案不是 `f[n-1]`

`f[n-1]` 强制“以最后一个元素结尾”，但最大子数组可能根本不含最后一个元素。例如 `[1, -100]`：`f[1] = -99`，答案是 1（`f[0]`）。所以必须全程 `ans = max(ans, f)`。

##### 为什么不能用“选或不选”

“选或不选”适合**子序列**（可以不连续，如背包问题）。子数组要求连续：选了 `nums[i]` 和 `nums[i+2]` 却跳过 `nums[i+1]` 就断了。子数组只能用“续接或重开”的思路，这正是 f[i] 的定义来源。

##### 空间优化：滚动变量

`f[i]` 只依赖 `f[i-1]`，不需要数组：

```go
func maxSubArray(nums []int) int {
    ans := math.MinInt // 答案可以是负数，不能初始化成 0
    f := 0
    for _, x := range nums {
        f = max(f, 0) + x // 状态转移
        ans = max(ans, f)
    }
    return ans
}
```

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(1)\)**。滚动变量。

#### 两种方法其实是同一个 f[i]

“以 i 结尾的最大子数组和”用前缀和写出来是：

\[
f[i] = pre[i+1] - \min_{0 \le j \le i} pre[j]
\]

也就是“当前前缀和减去左边最小的前缀和”——前缀和法算的正是这个 f[i]。DP 的 `max(f[i-1],0)+nums[i]` 只是用滚动方式算同一个值，所以两种方法答案必然一致。区别在思维入口：前缀和法像“找最低买入点”，DP 法像“决定续接还是重开”。

#### 对比与复盘

| 对比项 | 前缀和 + 贪心 | 动态规划 |
|---|---|---|
| 状态 | 维护最小前缀和 | `f[i]` = 以 i 结尾的最大和 |
| 核心式子 | `pre - minPre` | `max(f, 0) + x` |
| 容易踩的坑 | 先更新 min 再算 → 空子数组 | 答案忘了全程取 max；ans 初始成 0 |
| 复杂度 | \(O(n)\) / \(O(1)\) | \(O(n)\) / \(O(1)\) |
| 思维入口 | 买卖股票（找最低点） | 续接或重开 |

#### 易错点

1. 前缀和法**必须先算后更新**：先更新最小值再算差值，会把空子数组（差值 0）算进答案。
2. 不能直接“最大前缀和 - 最小前缀和”：必须保证被减数在右边（`i > j`）。
3. DP 答案是 `max(f)`，不是 `f[n-1]`。
4. DP 的 `ans` 初始值不能是 0：全负数数组的答案也是负数，要用 `math.MinInt`。
5. 子数组必须连续，不能用“选或不选”的思路（那是子序列）。
6. 空输入边界：题目保证至少一个元素，但 `f[0] = nums[0]` 的写法要单独处理 i=0。

#### 建议测试案例

```text
nums = [-2,1,-3,4,-1,2,1,-5,4] → 6
nums = [1]                     → 1
nums = [5,4,-1,7,8]            → 23
nums = [-1]                    → -1
nums = [-2,-1]                 → -1
nums = [1,-100]                → 1        // 答案不是 f[n-1] 的反例
```

#### 可迁移的规律

- **连续子数组和 → 前缀和 或“以 i 结尾”的 DP**：两种视角殊途同归，可互相验证。
- **循环里维护“最值池子”时**：先想清楚当前元素能不能参与本轮计算；不能（`j < i` 约束）就“先算账，再入池”。
- **“以 i 结尾”的 DP 定义**适合一切有连续性约束的问题（子数组、子串、打家劫舍）。
- **变形题**：[121. 买卖股票的最佳时机](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/)（完全同构）、[918. 环形子数组的最大和](https://leetcode.cn/problems/maximum-sum-circular-subarray/)（max 与 min 结合）。

#### 来源说明

- [LeetCode 53. 最大子数组和题解列表](https://leetcode.cn/problems/maximum-subarray/solutions/)
- [LeetCode 121. 买卖股票的最佳时机（同构题）](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/)
- 参考视频：灵茶山艾府《两种方法：前缀和+贪心 / 动态规划，附变形题》，动态规划 / 前缀和。

#### 重做记录

> 2026-08-19：前缀和法先踩了“先入池再算账”的顺序坑，后用 DP 视角理解“续接或重开”；重做时重点检查先算后更新、答案全程取 max。

---

### 题目 56：合并区间

#### 题目摘要

- **题目链接**：[LeetCode 56. 合并区间](https://leetcode.cn/problems/merge-intervals/)
- **输入**：若干区间组成的数组 `intervals`，每个区间是 `[start, end]`。
- **输出**：合并所有重叠区间后的不重叠区间数组。
- **关键约束**：区间按输入顺序给出，不一定有序；重叠边界包含相等端点。
- **核心模式**：排序 + 区间扫描。
- **面试必须说清**：合并条件（`end >= nextStart`）和结果如何维护。

#### 我的第一反应

> 待补充：不看题解时，最先想到什么？

#### 解法一：直觉 / 暴力解法

> 待补充：思路、代码、复杂度。

#### 解法二：优化解法

> 待补充：优化突破口、代码、复杂度、关键不变量。

#### 对比与复盘

> 待补充：两种解法的时间 / 空间复杂度对比。

#### 易错点

> 待补充。

#### 可迁移的规律

> 待补充。

#### 重做记录

> 待补充。

---

### 题目 239：滑动窗口最大值

#### 题目摘要

- **题目链接**：[LeetCode 239. 滑动窗口最大值](https://leetcode.cn/problems/sliding-window-maximum/)
- **输入**：整数数组 `nums` 和窗口大小 `k`。
- **输出**：每个长度为 `k` 的滑动窗口中的最大值组成的数组。
- **关键约束**：窗口从左到右滑动；`1 <= k <= len(nums)`。
- **核心模式**：单调队列（双向队列）。
- **面试必须说清**：队列中存下标的原因（既要取最大值，又要淘汰过期元素）。

#### 我的第一反应

> 待补充：不看题解时，最先想到什么？

#### 解法一：直觉 / 暴力解法

> 待补充：思路、代码、复杂度。

#### 解法二：优化解法

> 待补充：优化突破口、代码、复杂度、关键不变量。

#### 对比与复盘

> 待补充：两种解法的时间 / 空间复杂度对比。

#### 易错点

> 待补充。

#### 可迁移的规律

> 待补充。

#### 重做记录

> 待补充。

### 5. 专题参考资料

- [Hello 算法：数组](https://www.hello-algo.com/chapter_array_and_linkedlist/array/)
- [Hello 算法：队列](https://www.hello-algo.com/chapter_stack_and_queue/queue/)
- [Hello 算法：双向队列](https://www.hello-algo.com/chapter_stack_and_queue/deque/)
- [Hello 算法：哈希表](https://www.hello-algo.com/chapter_hashing/hash_map/)
- [Hello 算法：哈希优化策略](https://www.hello-algo.com/chapter_searching/replace_linear_by_hashing/)
- [Hello 算法：排序算法](https://www.hello-algo.com/chapter_sorting/sorting_algorithm/)
- [Hello 算法：初探动态规划](https://www.hello-algo.com/chapter_dynamic_programming/intro_to_dynamic_programming/)
- [Hello 算法：贪心算法](https://www.hello-algo.com/chapter_greedy/greedy_algorithm/)
