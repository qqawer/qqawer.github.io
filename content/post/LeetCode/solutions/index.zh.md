---
title: "LeetCode 题解手记：从思路到复盘"
description: "持续记录 LeetCode 刷题过程中的原始思路、优化过程、关键不变量、复杂度分析和易错点。专题一：哈希与双指针；专题二：滑动窗口、前缀和与区间；专题三：链表；专题四：二叉树；专题五：图与回溯。"
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
    - Linked List
    - Binary Tree
    - Graph
    - Backtracking
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
    "maps"
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

### 6. `maps`：Map 工具函数

`maps` 从 Go 1.21 起进入标准库（1.23 起新增迭代器函数）。常用的有拷贝、批量删除、比较，以及配合 `for range` 的键/值遍历。

| 方法签名（简化） | 输入 → 输出 | 作用 | 示例 |
|---|---|---|---|
| `Keys(m map[K]V) iter.Seq[K]` | `map → 迭代器` | 遍历所有键（Go 1.23+） | `for k := range maps.Keys(m)` |
| `Values(m map[K]V) iter.Seq[V]` | `map → 迭代器` | 遍历所有值（Go 1.23+） | `for v := range maps.Values(m)` |
| `All(m map[K]V) iter.Seq2[K, V]` | `map → 键值迭代器` | 同时遍历键和值（Go 1.23+） | `for k, v := range maps.All(m)` |
| `Collect(seq iter.Seq2[K, V]) map[K]V` | `键值序列 → map` | 把键值对收集成 map（Go 1.23+） | `m := maps.Collect(maps.All(src))` |
| `Insert(m map[K]V, seq iter.Seq2[K, V])` | `map, 键值序列 → 无返回值` | 把键值对写入 map，同名键覆盖（Go 1.23+） | `maps.Insert(m, maps.All(src))` |
| `Clone(m map[K]V) map[K]V` | `map → map` | 浅拷贝 | `copyMap := maps.Clone(m)` |
| `Copy(dst, src map[K]V)` | `两个 map → 无返回值` | 把 src 全部键值写入 dst | `maps.Copy(dst, src)` |
| `DeleteFunc(m map[K]V, del func(K, V) bool)` | `map, 条件函数 → 无返回值` | 删除所有满足 `del` 的键值对 | `maps.DeleteFunc(m, func(k string, v int) bool { return v == 0 })` |
| `Equal(m1, m2 map[K]V) bool` | `两个 map → bool` | 长度和所有键值是否相同 | `maps.Equal(m1, m2)` → `true` |

```go
m := map[string]int{"go": 1, "java": 2, "python": 3}

// 遍历键 / 值 / 键值（Go 1.23+，顺序不固定）
for k := range maps.Keys(m) {
    fmt.Println(k)
}
for _, v := range maps.Values(m) {
    fmt.Println(v)
}
for k, v := range maps.All(m) {
    fmt.Println(k, v)
}

// 想拿到键切片：用 slices.Collect 收集
keys := slices.Collect(maps.Keys(m)) // []string

// 删除满足条件的键值对
maps.DeleteFunc(m, func(k string, v int) bool {
    return v == 1 // 删掉 go
})
// m 剩下 {"java": 2, "python": 3}

// 比较两个 map
same := maps.Equal(map[string]int{"a": 1}, map[string]int{"a": 1}) // true
```

注意：

- `Keys` / `Values` / `All` 返回**迭代器**，惰性求值，不会预先分配切片；需要切片时用 `slices.Collect` 收集。
- 遍历顺序不固定，和 `for k := range m` 一样，不能依赖顺序。
- `Clone` 是**浅拷贝**：值是引用类型（切片、map）时，内层仍然共享。
- 版本：`Clone` / `Copy` / `DeleteFunc` / `Equal` 需要 Go 1.21+；`Keys` / `Values` / `All` / `Collect` / `Insert` 需要 Go 1.23+。

### 7. `sort` 和 `slices` 怎么选

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
maps：Keys、Values、All、DeleteFunc、Equal
```

完整方法签名可查阅 Go 官方文档：[strings](https://pkg.go.dev/strings)、[strconv](https://pkg.go.dev/strconv)、[sort](https://pkg.go.dev/sort)、[unicode](https://pkg.go.dev/unicode)、[slices](https://pkg.go.dev/slices)、[math](https://pkg.go.dev/math)、[maps](https://pkg.go.dev/maps)。

### 8. `math`：数学常量与常用函数

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

### 9. 刷题高频小抄：常用方法一行示例

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
| 遍历 map 的键 | `for k := range maps.Keys(m)` |
| 收集键切片 | `keys := slices.Collect(maps.Keys(m))` |
| 删除满足条件的键值对 | `maps.DeleteFunc(m, func(k string, v int) bool { return v == 0 })` |
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

单调队列的三条规则（239 的前置知识）：

- **右边入**：新元素入队前，把队尾所有“不如它”的元素弹出（小于或等于新元素就裁掉）——它们比新元素小、又比新元素先过期，永远不可能再成为窗口最大值；
- **左边出**：队首下标滑出窗口时弹出。用 `if` 而不是 `while`：窗口每次只向右滑一格，同一轮最多只有一个元素过期；
- **队首即答案**：队列从队首到队尾单调递减，窗口最大值永远在队首。

为什么存**下标**而不是只存值：判单调要用下标去取队尾元素的值；判过期要用下标和窗口左端 `i-k+1` 比较。只存值的话，无法判断哪个元素已经滑出窗口。

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
| ✅　　| A　　| 56　 | [合并区间](https://leetcode.cn/problems/merge-intervals/)　　　　　　　　　　　　　　　　　　　　　　| 排序、合并条件与结果维护　　 | [查看](#题目-56合并区间)　　　　　　　　　　|
| ✅　　| B　　| 239　| [滑动窗口最大值](https://leetcode.cn/problems/sliding-window-maximum/)　　　　　　　　　　　　　　　 | 单调队列、队列存下标的原因　 | [查看](#题目-239滑动窗口最大值)　　　　　　 |

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

> 第一反应是“排序 + 贪心合并”：区间重叠问题，把区间按左端点排序后，一趟遍历边合并边产出。排序是前提——只有左端点单调不减，才能保证“合并出来的区间一定是原区间的连续一段”，贪心才不会漏。

#### 解法一：排序 + 合并（我的写法）

##### 优化突破口

为什么先按左端点排序：排序后左端点从左到右单调不减，于是“当前正在合并的区间”的**左端点已经确定**，只需关心右端点会不会被后面的区间撑大。遍历时只用判断一件事：新区间的左端点是否落在当前合并区间内。

##### 代码

```go
func merge(intervals [][]int) [][]int {
    ans := make([][]int, 0)
    slices.SortFunc(intervals, func(p, q []int) int { return p[0] - q[0] })
    for _, v := range intervals {
        m := len(ans)
        if m > 0 && v[0] <= ans[m-1][1] {
            ans[m-1][1] = max(ans[m-1][1], v[1])
        } else {
            ans = append(ans, v)
        }
    }
    return ans
}
```

##### 逐行理解

- `ans` 的**最后一个元素 = 当前正在合并的区间**（左端点已定、右端点待定）；`ans` 里前面的区间全部已经定型。
- `slices.SortFunc(intervals, func(p, q []int) int { return p[0] - q[0] })`：按左端点升序排序。比较器返回负数表示 `p` 排在前面。
- `m := len(ans)`：拿到当前合并区间在 `ans` 里的下标。
- 合并条件 `v[0] <= ans[m-1][1]`：新区间左端点 ≤ 当前右端点 → 相交或相接，可以合并。注意是 `<=`，因为题目认为 `[1,4]` 和 `[4,5]` 算重叠。
- `ans[m-1][1] = max(ans[m-1][1], v[1])`：合并后右端点取两者较大值。**左端点不用动**：排序保证 `v[0] ≥` 当前左端点。
- `else` 分支 `append(ans, v)`：不相交，当前合并区间定型，`v` 成为新的“当前合并区间”。

##### 为什么 `ans` 的最后一个元素一定是“当前合并区间”

区间已经按左端点排序，左端点单调不减。当前区间 `v` 只有两种归宿：要么并入最后一个合并区间（更新右端点），要么开启新区间（`append`）。已经定型的区间，左端点都 ≤ `v` 的左端点，**永远不可能再被后面的区间改变**，所以只需要盯着 `ans` 的最后一个元素。

##### 完整运行示例：`intervals = [[1,3],[2,6],[8,10],[15,18]]`

| 遍历到 | 判断 | 操作 | `ans` |
|---|---|---|---|
| `[1,3]` | 空 `ans` | `append` | `[[1,3]]` |
| `[2,6]` | `2 ≤ 3` | 合并，右端点取 `max(3,6)=6` | `[[1,6]]` |
| `[8,10]` | `8 > 6` | 新开 | `[[1,6],[8,10]]` |
| `[15,18]` | `15 > 10` | 新开 | `[[1,6],[8,10],[15,18]]` |

##### 复杂度

- **时间复杂度：\(O(n\log n)\)**。瓶颈在排序，扫描本身是 \(O(n)\)。
- **空间复杂度：\(O(1)\)**。不计返回值，只用了常数变量（排序的栈开销忽略）。

##### 写法二：显式 `left` / `right`（灵茶山艾府）

```go
func merge(intervals [][]int) (ans [][]int) {
    slices.SortFunc(intervals, func(p, q []int) int { return p[0] - q[0] })

    left, right := math.MaxInt, math.MinInt
    for i, p := range intervals {
        left = min(left, p[0])
        right = max(right, p[1])
        // 下一个区间与 [left, right] 不相交，或已到末尾：当前合并区间定型
        if i == len(intervals)-1 || intervals[i+1][0] > right {
            ans = append(ans, []int{left, right})
            left = math.MaxInt // right 不用重置，下一轮会被 max 覆盖且旧值更小
        }
    }
    return
}
```

思路和写法一相同，只是把“`ans` 的最后一个区间”换成 `left`、`right` 两个变量，当发现下一个区间与当前合并区间不相交（或已是最后一个）时才把 `[left, right]` 落地。

##### 答疑：能不能按右端点排序？

可以，但必须**倒着遍历**。按左端点排序正序遍历时，一旦新区间左端点 > 当前右端点，就能断定后面所有区间都不可能与当前区间相交（因为左端点只会更大）——这是按左端点排序带来的确定性。按右端点排序正着遍历做不到这种即时断定。

#### 解法二：差分数组（进阶，待细看）

##### 思路

把每个区间 `[start, end]` 在数轴上“点亮”连续整数下标（每个下标计数 +1），最后计数 > 0 的连续段就是合并后的区间。

##### Bug 与 ×2 技巧

直接对整数坐标 +1 会把 `[1,2]` 和 `[3,4]` 误判成连续（下标 2 和 3 在整数轴上相邻）。把端点 ×2：`[1,2]` → `[2,4]`、`[3,4]` → `[6,8]`，中间隔了坐标 5，就能区分“相邻但不相交”和“真正重叠”。最后把答案端点 ÷2 还原。

##### 代码

```go
func merge(intervals [][]int) (ans [][]int) {
    mx := 0
    for _, p := range intervals {
        mx = max(mx, p[1])
    }

    diff := make([]int, mx*2+2)
    for _, p := range intervals {
        // 把区间 [p[0]*2, p[1]*2] 增加 1（差分：起点 +1，终点后一位 -1）
        diff[p[0]*2]++
        diff[p[1]*2+1]--
    }

    sumD := 0
    start := -1 // -1 表示还没遇到合并后的区间左端点
    for i, d := range diff {
        sumD += d // 差分的前缀和就是当前下标的覆盖次数
        if sumD > 0 {
            if start < 0 {
                start = i // 合并后的区间左端点
            }
        } else if start >= 0 {
            // sumD 归零：i 是右端点后一位，除以 2 还原坐标
            ans = append(ans, []int{start / 2, i / 2})
            start = -1
        }
    }
    return
}
```

##### 复杂度

- **时间复杂度：\(O(n+U)\)**，`U = max(end)`。
- **空间复杂度：\(O(U)\)**。差分数组。
- **局限**：坐标值域很大时数组会爆，只适合值域可控的场景。

#### 解法三：扫描线（进阶，待细看）

##### 思路

把每个区间拆成两个事件：左端点 +1、右端点 -1。按坐标从左到右扫，用一个计数器 `cnt` 表示当前垂线与多少个区间相交：

- `cnt` 从 0 变非 0：一段新合并区间的**起点**；
- `cnt` 从非 0 变 0：这段合并区间的**终点**。

同一个坐标可能有多个左右端点，先用 `map` 聚合（`events[x]` 就是 x 处的净增量），再用 `maps.Keys` + `slices.Sorted` 得到有序坐标。

##### 代码

```go
func merge(intervals [][]int) (ans [][]int) {
    events := map[int]int{}
    for _, p := range intervals {
        events[p[0]]++ // 遇到左端点：计数器 +1
        events[p[1]]-- // 遇到右端点：计数器 -1
    }

    points := slices.Sorted(maps.Keys(events))
    cnt := 0
    start := 0
    for _, x := range points {
        if cnt == 0 { // 扫描线开始与区间相交
            start = x
        }
        cnt += events[x]
        if cnt == 0 { // 扫描线结束与区间相交
            ans = append(ans, []int{start, x})
        }
    }
    return
}
```

以 `[1,3]` 和 `[2,6]` 为例：事件为 `{1:+1, 2:+1, 3:-1, 6:-1}`，按序扫到 1（cnt 0→1，记起点 1）、2（cnt 1→2）、3（cnt 2→1）、6（cnt 1→0，产出 `[1,6]`）。

##### 复杂度

- **时间复杂度：\(O(n\log n)\)**。瓶颈在对坐标排序。
- **空间复杂度：\(O(n)\)**。事件表。

#### 对比与复盘

| 对比项 | 排序 + 合并 | 差分数组 | 扫描线 |
|---|---|---|---|
| 时间复杂度 | \(O(n\log n)\) | \(O(n+U)\) | \(O(n\log n)\) |
| 空间复杂度 | \(O(1)\) | \(O(U)\) | \(O(n)\) |
| 核心操作 | 排序后一次扫描 | 区间批量加减 + 前缀和 | 事件排序 + 计数器 |
| 优点 | 简单直观、面试首选 | 值域小时最快 | 通用性强，可扩展 |
| 局限 | 依赖排序 | 坐标值域大时爆内存 | 代码稍绕 |

面试建议：掌握解法一即可，差分数组和扫描线作为拓展了解。

#### 易错点

1. 合并条件用 `<` 而不是 `<=`：`[1,4]` 和 `[4,5]` 相接也算重叠。
2. 更新右端点要用 `max`，不能直接覆盖：之前的合并区间右端点可能更大。
3. 忘了排序，或比较器方向写反（`p[0]-q[0]` 是升序）。
4. 差分数组忘了 ×2：`[1,2]` 和 `[3,4]` 会被错误合并。
5. 扫描线必须先把事件坐标排序：`map` 遍历顺序不固定。
6. 空输入返回空切片，不要 panic。

#### 建议测试案例

```text
intervals = [[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]
intervals = [[1,4],[4,5]]               → [[1,5]]        // 相接算重叠
intervals = [[1,4],[2,3]]               → [[1,4]]        // 完全包含
intervals = [[1,2],[3,4]]               → [[1,2],[3,4]]  // 相邻但不相交
intervals = [[1,1]]                     → [[1,1]]        // 单点区间
intervals = []                          → []
```

#### 可迁移的规律

- **区间合并 / 重叠 / 覆盖 → 排序 + 扫描**：按左端点排序后，合并区间一定是原区间的连续一段，贪心成立。
- **差分数组**适合“区间批量加减 + 坐标值域不大”；**扫描线**是它的通用事件版，两者本质都是拆成端点事件。
- 排序比较器 `p[0]-q[0]` 在坐标值域极大时可能溢出，保守写法用显式比较。
- **变形题**：[252. 会议室](https://leetcode.cn/problems/meeting-rooms/)（判断能否参加全部会议）、[435. 无重叠区间](https://leetcode.cn/problems/non-overlapping-intervals/)、[763. 划分字母区间](https://leetcode.cn/problems/partition-labels/)。

#### 来源说明

- [LeetCode 56. 合并区间题解列表](https://leetcode.cn/problems/merge-intervals/solutions/)
- 参考视频：灵茶山艾府《三种方法：排序 / 差分数组 / 扫描线》，排序 / 扫描线。

#### 重做记录

> 2026-08-19：完成排序 + 合并版并逐行理解；差分数组和扫描线还没细看，下次目标是把 ×2 技巧和扫描线 cnt 的变化过程讲清楚。

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

> 第一反应是暴力：每个窗口扫一遍找最大值，\(O(nk)\) 超时。想到大顶堆能取最大，但“过期元素”还留在堆里，需要惰性删除。后来意识到单调队列更贴合滑动窗口：队列里只留“还可能成为最大值”的候选下标，右边入、左边出、队首即答案。写作时把“维护单调性”类比成单调栈，再叠加“过期出队”这一步。

#### 解法一：暴力枚举窗口（超时）

##### 我的思路

枚举每个窗口左端点，在窗口内线性扫描找最大值。

##### 代码

```go
func maxSlidingWindow(nums []int, k int) []int {
    ans := make([]int, 0, len(nums)-k+1)
    for i := 0; i+k-1 < len(nums); i++ {
        mx := math.MinInt
        for j := i; j < i+k; j++ {
            mx = max(mx, nums[j])
        }
        ans = append(ans, mx)
    }
    return ans
}
```

##### 复杂度

- **时间复杂度：\(O(nk)\)**。`n`、`k` 都可到 \(10^5\)，超时。
- **空间复杂度：\(O(1)\)**。不计返回值。

##### 顺带一提：大顶堆为什么不够好

堆能在 \(O(\log k)\) 取最大，但元素过期后还躺在堆里，只能在取答案时“惰性删除”：堆顶下标滑出窗口就弹出，直到堆顶合法。总复杂度 \(O(n\log k)\) 能过，但比单调队列多一个 log，还要额外处理“堆顶是否过期”。

#### 解法二：单调队列（推荐）

##### 优化突破口

窗口里的元素有一个性质：**新元素比旧元素大（或一样大）时，旧元素在窗口剩余寿命内永远不可能是最大值**——它更小，还会更早离开窗口。所以入队时把队尾这些“没用”的旧元素裁掉；队首的过期元素在滑出窗口时弹出。队列里剩下的候选下标从队首到队尾单调递减，队首就是当前窗口最大值。

一个比喻（灵茶山艾府）：新员工比老员工强（或一样强），把老员工裁掉；老员工到了 35 岁（滑出窗口），也裁掉；裁员后资历最老（最左边）的就是最强的员工。

##### 代码（我的写法）

```go
func maxSlidingWindow(nums []int, k int) []int {
    cnt := make([]int, 0) // 存下标
    ans := make([]int, 0)
    for i, v := range nums {
        // 1. 右边入：把队尾所有不如 v 的旧元素裁掉，维护单调递减
        for len(cnt) > 0 && v >= nums[cnt[len(cnt)-1]] {
            cnt = cnt[:len(cnt)-1]
        }
        cnt = append(cnt, i)

        // 2. 左边出：队首下标滑出窗口就弹出（if 即可，每轮最多一个过期）
        index := i - k + 1 // 当前窗口左端点
        if cnt[0] < index {
            cnt = cnt[1:]
        }

        // 3. 记录答案：队首就是窗口最大值
        if i >= k-1 {
            ans = append(ans, nums[cnt[0]])
        }
    }
    return ans
}
```

##### 逐行理解

1. **右边入**：`for len(cnt) > 0 && v >= nums[cnt[len(cnt)-1]]`——新元素 `v` 入队前，把队尾所有 ≤ `v` 的下标弹出。为什么敢裁：它们比 `v` 小（或一样大），又比 `v` 下标小（更早过期），`v` 活着的时候它们永远轮不到当最大值。用 `>=` 表示“一样强也裁掉”，保留更晚过期的新下标；用 `>` 也正确。
2. `cnt = append(cnt, i)`：存的是**下标**，不是值。
3. **左边出**：`if cnt[0] < index`——窗口左端是 `i-k+1`，队首下标小于它说明已经滑出窗口，弹出。用 `if` 而不是 `while`：窗口每次只滑一格，同一轮最多只有一个元素滑出，且过期的一定是队首（队列里下标递增）。
4. **记录答案**：`if i >= k-1` 窗口满了才记录，`nums[cnt[0]]` 就是当前窗口最大值。

##### 为什么存下标（面试必须说清）

两点缺一不可：

- **判单调**：要比较“队尾元素的值”和“新元素”，需要用队尾下标去取 `nums`；
- **判过期**：要判断队首是否滑出窗口，需要和窗口左端 `i-k+1` 比大小。

只存值的话，元素过期时不知道它是不是还在队列里，更不知道它下标够不够新。

##### 完整运行示例：`nums = [1,3,-1,-3,5,3,6,7]`，`k = 3`

表中 `q` 列出队列里的值（实际存的是下标）：

| i | nums[i] | 入队前弹出 | 入队后 q | 队首过期？ | 窗口 | ans |
|---|---:|---|---|---|---|---|
| 0 | 1 | 无 | `[1]` | 否（未满） | — | — |
| 1 | 3 | 弹出 1 | `[3]` | 否（未满） | — | — |
| 2 | -1 | 无 | `[3,-1]` | 否 | `[1,3,-1]` | 3 |
| 3 | -3 | 无 | `[3,-1,-3]` | 否 | `[3,-1,-3]` | 3 |
| 4 | 5 | 弹出 -3、-1、3 | `[5]` | 否 | `[-1,-3,5]` | 5 |
| 5 | 3 | 无 | `[5,3]` | 否 | `[-3,5,3]` | 5 |
| 6 | 6 | 弹出 3、5 | `[6]` | 否 | `[5,3,6]` | 6 |
| 7 | 7 | 弹出 6 | `[7]` | 否 | `[3,6,7]` | 7 |

答案 `[3,3,5,5,6,7]`。

再补一个会触发“左边出”的例子：`nums = [4,3,2,1]`，`k = 3`。

| i | nums[i] | 入队后 q | 队首过期？ | 窗口 | ans |
|---|---:|---|---|---|---|
| 0 | 4 | `[4]` | 否（未满） | — | — |
| 1 | 3 | `[4,3]` | 否（未满） | — | — |
| 2 | 2 | `[4,3,2]` | 否 | `[4,3,2]` | 4 |
| 3 | 1 | `[4,3,2,1]` | **是**（q[0]=0 < left=1，弹出 4） | `[3,2,1]` | 3 |

答案 `[4,3]`——第 4 行就是 `if cnt[0] < index` 生效的时刻。

##### 复杂度

- **时间复杂度：\(O(n)\)**。每个下标至多入队一次、出队一次，整体线性。
- **空间复杂度：\(O(k)\)**。队列最多同时存 `k` 个候选（更精确是 `O(min(k, U))`，`U` 为不同元素个数）。返回值不计入。

##### 参考写法：预分配答案数组（灵茶山艾府）

```go
func maxSlidingWindow(nums []int, k int) []int {
    ans := make([]int, len(nums)-k+1) // 窗口个数
    q := []int{}
    for i, x := range nums {
        for len(q) > 0 && nums[q[len(q)-1]] <= x {
            q = q[:len(q)-1]
        }
        q = append(q, i)
        left := i - k + 1
        if q[0] < left {
            q = q[1:]
        }
        if left >= 0 {
            ans[left] = nums[q[0]]
        }
    }
    return ans
}
```

和我的写法算法完全一样，只是 `ans` 预分配后用 `ans[left] = ...` 写入，而不是 `append`。

#### 对比与复盘

| 对比项 | 暴力 | 大顶堆 | 单调队列 |
|---|---|---|---|
| 时间复杂度 | \(O(nk)\) | \(O(n\log k)\) | \(O(n)\) |
| 空间复杂度 | \(O(1)\) | \(O(k)\) | \(O(k)\) |
| 核心操作 | 每窗扫描 | 取堆顶 + 惰性删除过期 | 右边入、左边出、队首即答案 |
| 优点 | 最直观 | 思路简单 | 线性时间，天然处理过期 |
| 局限 | 超时 | 多一个 log，过期处理绕 | 需要理解“淘汰无用候选” |

#### 易错点

1. **队列里存下标，不是值**：判单调、判过期都需要下标。
2. **入队弹出条件别写反**：队尾元素 ≤ 新元素才弹出，维持单调递减。
3. **过期用 `if` 而不是 `while`**：窗口每次只滑一格，最多一个元素过期，且过期的一定是队首。
4. **记录答案的时机**：窗口满了（`i >= k-1`）才记录，别提前。
5. **用堆时忘了惰性删除过期堆顶**，会把已离开窗口的元素当最大值。
6. **空输入 / `k > len(nums)`**：题目保证 `1 <= k <= len(nums)`，但防御式写法可先判空。

#### 建议测试案例

```text
nums = [1,3,-1,-3,5,3,6,7], k = 3 → [3,3,5,5,6,7]
nums = [1],                    k = 1 → [1]
nums = [1,-1],                 k = 1 → [1,-1]
nums = [9,11],                 k = 2 → [11]
nums = [4,3,2,1],              k = 3 → [4,3]      // 队首过期
nums = [1,3,1,2,0,5],          k = 3 → [3,3,2,5]
```

#### 可迁移的规律

- **定长窗口内的最值 → 单调队列**：三步模板“右边入 → 左边出 → 记录答案”。
- **单调队列 = 单调栈 + 滑动窗口**：维护单调性和单调栈一样（弹出队尾），多出来的“移除队首”就是窗口左移。
- **存下标**是“既要比大小、又要判过期”问题的通用手法。
- **变形题**：[862. 和至少为 K 的最短子数组](https://leetcode.cn/problems/shortest-subarray-with-sum-at-least-k/)（前缀和 + 单调队列）；灵茶山艾府思考题“求 `k=1..n` 的全部答案”。

#### 来源说明

- [LeetCode 239. 滑动窗口最大值题解列表](https://leetcode.cn/problems/sliding-window-maximum/solutions/)
- 参考视频：灵茶山艾府《降本增笑，秒懂单调队列！附题单！》（单调队列【基础算法精讲 27】），滑动窗口 / 单调队列。

#### 重做记录

> 2026-08-19：完成单调队列写法并逐行理解；重做时重点检查存下标的原因、过期用 `if` 而不是 `while`、以及“为什么敢淘汰队尾旧元素”。

### 5. 专题参考资料

- [Hello 算法：数组](https://www.hello-algo.com/chapter_array_and_linkedlist/array/)
- [Hello 算法：队列](https://www.hello-algo.com/chapter_stack_and_queue/queue/)
- [Hello 算法：双向队列](https://www.hello-algo.com/chapter_stack_and_queue/deque/)
- [Hello 算法：哈希表](https://www.hello-algo.com/chapter_hashing/hash_map/)
- [Hello 算法：哈希优化策略](https://www.hello-algo.com/chapter_searching/replace_linear_by_hashing/)
- [Hello 算法：排序算法](https://www.hello-algo.com/chapter_sorting/sorting_algorithm/)
- [Hello 算法：初探动态规划](https://www.hello-algo.com/chapter_dynamic_programming/intro_to_dynamic_programming/)
- [Hello 算法：贪心算法](https://www.hello-algo.com/chapter_greedy/greedy_algorithm/)

## 专题三：链表

### 1. 专题背景

链表题的核心是“画图 + 动 Next”：先在纸上画节点，再改指针；改 `cur.Next` 之前，先想清楚要保存哪个指针。本专题的底层内容来自 hello-algo 的[链表](https://www.hello-algo.com/chapter_array_and_linkedlist/linked_list/)章节和[代码随想录·链表理论基础](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/链表理论基础.md)。

#### 1.1 链表是什么（hello-algo 4.2）

链表（linked list）是一种线性数据结构，每个元素是一个节点（node）对象，节点之间通过“引用/指针”相连。它的设计让节点可以**分散存储在内存各处**，地址无须连续——这正是它和数组最本质的区别。

- 首个节点叫**头节点**，最后一个叫**尾节点**，尾节点指向 `nil`；
- 相同数据量下，链表比数组**占用更多内存**（每个节点都要额外存一个指针）；
- 在 Go 中，引用就是指针：

```go
type ListNode struct {
    Val  int
    Next *ListNode
}
```

#### 1.2 链表常用操作与复杂度（hello-algo 4.2.1）

| 操作 | 复杂度 | 原因 |
|---|---|---|
| 初始化链表 | \(O(n)\) | 逐个建节点、串指针 |
| 插入节点 | \(O(1)\) | 已知前驱/后继时，只需改两个指针 |
| 删除节点 | \(O(1)\) | 只需改一个指针（跳过被删节点） |
| 访问第 i 个节点 | \(O(n)\) | 必须从头节点逐个走 |
| 查找某个值 | \(O(n)\) | 线性遍历 |

关键直觉：**链表插入/删除快（改指针），访问/查找慢（只能从头走）**。改指针之前必须先保存旧指针——这正是 206、19 等题的核心动作。

#### 1.3 数组 vs 链表（hello-algo 4.2.2）

| 对比项 | 数组 | 链表 |
|---|---|---|
| 存储方式 | 连续内存空间 | 分散内存空间 |
| 容量扩展 | 长度不可变 | 可灵活扩展 |
| 内存效率 | 元素占用内存少，但可能浪费空间 | 元素占用内存多（额外指针） |
| 访问元素 | \(O(1)\) | \(O(n)\) |
| 添加元素 | \(O(n)\) | \(O(1)\) |
| 删除元素 | \(O(n)\) | \(O(1)\) |

两种数据结构采用相反的存储策略，因此性质和操作效率完全对立：数组“查得快、改得慢”，链表“改得快、查得慢”。

#### 1.4 常见链表类型与典型应用（hello-algo 4.2.3 / 4.2.4）

常见的三种类型：

| 类型 | 结构 | 特点 | 本专题相关 |
|---|---|---|---|
| 单向链表 | 节点只有 `Next` | 最基础，只能从头往后走 | 206、21、19、2 |
| 环形链表 | 尾节点指向头 | 任意节点都可视为头，没有尾 | 141、142 |
| 双向链表 | 有 `Prev` 和 `Next` | 可双向遍历，更灵活但更占内存 | 面试题较少直接考 |

典型应用：

- **单向链表**：实现栈/队列、哈希表链式地址（解决冲突）、图的邻接表；
- **双向链表**：LRU 缓存淘汰、浏览器前进/后退历史、红黑树/B 树中的父节点引用；
- **环形链表**：操作系统时间片轮转调度、音频/视频环形缓冲区——141/142 的“环”就来自这种结构。

#### 1.5 为什么链表题要先画图

改指针的本质是“重新接线”。纸上画出节点和箭头后，能直接看出：

- 改 `cur.Next` 前要保存哪个指针（否则旧后继丢了）；
- `dummy` 节点放在哪里；
- 快慢指针的起点和步长。

#### 1.6 链表题四大套路

1. **保存 Next 再改指针**：`next := cur.Next` 先备份，再动 `cur.Next`。
2. **dummy 头节点**：`dummy := &ListNode{Next: head}` 统一处理“删除头节点”和“空表”，最后返回 `dummy.Next`（19 题必需）。
3. **快慢指针**：141/142 的环检测、19 的倒数第 N 个节点，本质都是“两个指针不同步长”。
4. **迭代与递归双视角**：206 反转链表用迭代三指针最直观，递归是另一种理解方式。

#### 1.7 本地测试与验收（Day 3 要求）

测试辅助函数至少包含：

- `fromSlice([]int) *ListNode`：由切片建链表；
- `toSlice(*ListNode) []int`：链表转切片（顺便检测无环）；
- Floyd 成环检测：判断链表是否有环（快慢指针）。

所有链表测试都做成**表驱动**，并验证“输出无环”。当天验收标准：

- 206 和 19 各 12 分钟盲写；
- 不看资料完整推导 142（手绘距离式）；
- 所有链表测试表驱动 + 无环验证。

### 2. 本专题题目看板

题目来自 Day 3 执行清单，难度标记沿用 A/B 分组。

| 状态 | 分组 | 题号 | 题目 | 核心训练点 | 笔记 |
|:---:|:---:|---:|---|---|---|
| ✅ | A | 206 | [反转链表](https://leetcode.cn/problems/reverse-linked-list/) | 三指针迭代、保存 Next | [查看](#题目-206反转链表) |
| ✅ | A | 141 | [环形链表](https://leetcode.cn/problems/linked-list-cycle/) | 快慢指针、Floyd 环检测 | [查看](#题目-141环形链表) |
| ✅ | A | 142 | [环形链表 II](https://leetcode.cn/problems/linked-list-cycle-ii/) | 快慢指针 + 数学推导入口 | [查看](#题目-142环形链表-ii) |
| ✅ | A | 21 | [合并两个有序链表](https://leetcode.cn/problems/merge-two-sorted-lists/) | dummy、双指针归并 | [查看](#题目-21合并两个有序链表) |
| ✅ | A | 19 | [删除链表的倒数第 N 个结点](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/) | 快慢指针、dummy 删头 | [查看](#题目-19删除链表的倒数第-n-个结点) |
| ✅ | B | 2 | [两数相加](https://leetcode.cn/problems/add-two-numbers/) | 模拟加法、carry | [查看](#题目-2两数相加) |

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

### 题目 206：反转链表

#### 题目摘要

- **题目链接**：[LeetCode 206. 反转链表](https://leetcode.cn/problems/reverse-linked-list/)
- **输入**：单链表头节点 `head`。
- **输出**：反转后的链表头节点。
- **关键约束**：节点数 `0 <= n <= 5000`；可迭代可递归。
- **核心模式**：三指针迭代（`prev` / `cur` / `next`）或递归。
- **面试必须说清**：改 `cur.Next` 前保存哪个指针？循环结束后返回谁？
- **本地测试标准**：空、1/2/多节点；结果逆序且无环。

#### 我的第一反应

> 第一反应是迭代三指针：先保存 `next`，再改 `cur.Next` 指向前驱。写的时候盯住“改指针前先备份”这条纪律，避免丢失后继；循环结束后返回 `pre`。递归版一开始没看懂，本质是“递到末尾拿新头，归的路上往新链表末尾接”。

#### 解法一：迭代（头插法）

##### 优化突破口

反转 = 把每个节点依次“头插”到一个新链表。用 `pre` 保存已经反转好的部分，`cur` 指向当前要处理的节点，`nxt` 先保存 `cur` 的后继（否则改完 `cur.Next` 就找不到了）。

##### 代码（我的写法）

```go
func reverseList(head *ListNode) *ListNode {
    var pre, cur *ListNode = nil, head
    for cur != nil {
        nxt := cur.Next
        cur.Next = pre
        pre = cur
        cur = nxt
    }
    return pre
}
```

##### 逐行理解

- `pre`：已经反转好的链表的头（初始 `nil`，因为新链表最初是空的）；
- `cur`：当前要处理的节点（初始 `head`）；
- 每轮三步：
  1. `nxt := cur.Next`——先保存后继，不保存就丢了；
  2. `cur.Next = pre`——把 `cur` 插到 `pre` 链表头部（头插法）；
  3. `pre = cur`、`cur = nxt`——指针前进。
- 循环结束后 `cur == nil`，`pre` 指向反转后的头，返回 `pre`。

##### 完整运行示例：`1→2→3`

| 轮 | 处理前 | `nxt` | 接线后 | `pre` | `cur` |
|---|---|---|---|---|---|
| 1 | `cur=1, pre=nil` | 2 | `1→nil` | 1 | 2 |
| 2 | `cur=2, pre=1` | 3 | `2→1` | 2 | 3 |
| 3 | `cur=3, pre=2` | nil | `3→2` | 3 | nil |

结果 `3→2→1`。

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(1)\)**。

#### 解法二：递归（尾插法）

##### 核心思路

先“递”到链表末尾，把末尾节点作为新链表的头 `revHead`；再在“归”的过程中，把经过的每个节点依次插到新链表的末尾。

##### 代码

```go
func reverseList(head *ListNode) *ListNode {
    if head == nil || head.Next == nil {
        return head // 原链表的末尾 = 新链表的头
    }
    revHead := reverseList(head.Next) // 递：反转 head.Next 开头的子链表
    tail := head.Next                 // 归：head.Next 就是新链表的末尾
    tail.Next = head                  // 把 head 接到新链表末尾
    head.Next = nil                   // 断开旧指针，防止成环
    return revHead
}
```

##### 递的过程：一路走到末尾

`reverseList(head.Next)` 返回“以 `head.Next` 开头那段子链表反转后的新头”，也就是原链表的**尾节点**。最深一层 `head.Next == nil` 时返回 `head` 自己。

##### 归的过程：为什么 `head.Next` 就是新链表的末尾

当递归返回时，`head.Next` 开头的那段已经反转好：新头 = `revHead`，新尾 = `head.Next` 这个节点本身。所以：

- `tail := head.Next`——拿到新链表末尾；
- `tail.Next = head`——把当前节点接上去；
- `head.Next = nil`——断开旧指针，防止成环。

##### 完整运行示例：`1→2→3→4`

递：

```text
reverseList(1)
  └─ reverseList(2)
       └─ reverseList(3)
            └─ reverseList(4) → head.Next==nil，返回 4
```

归（每层 `revHead` 都是 4）：

```text
head=3：tail=4，4→3，3→nil → 4→3→nil
head=2：tail=3，3→2，2→nil → 4→3→2→nil
head=1：tail=2，2→1，1→nil → 4→3→2→1→nil
```

##### 为什么 `head.Next = nil` 不能省

省略后 `tail.Next = head` 让 4 指向 3，而 3 还指向 4，两个节点互相指，成环。判题机比对答案时要把链表转成字符串，环会让字符串无限增长，**先报“超出内存限制”**（不是超时，内存先爆）。

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(n)\)**。递归调用栈。

#### 对比与复盘

| 对比项 | 迭代（头插法） | 递归（尾插法） |
|---|---|---|
| 方向 | 从头往后 | 从尾往前 |
| 核心动作 | `cur.Next = pre` | `tail.Next = head` |
| 空间复杂度 | \(O(1)\) | \(O(n)\) 栈 |
| 优点 | 空间小、面试首选 | 代码短、思路优雅 |
| 局限 | 需要想清三个指针 | 链表很长时可能栈溢出 |

#### 本地测试（Day 3 要求：表驱动 + 无环验证）

```go
func TestReverseList(t *testing.T) {
    tests := []struct {
        name string
        in   []int
        want []int
    }{
        {"empty", []int{}, []int{}},
        {"one", []int{1}, []int{1}},
        {"two", []int{1, 2}, []int{2, 1}},
        {"multi", []int{1, 2, 3, 4}, []int{4, 3, 2, 1}},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := toSlice(reverseList(fromSlice(tt.in)))
            if !slices.Equal(got, tt.want) {
                t.Errorf("got %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 改 `cur.Next` 前不保存 `nxt`，后继丢失。
2. 循环结束后返回 `pre` 而不是 `cur`（`cur` 已是 `nil`）。
3. 递归里漏写 `head.Next = nil`，链表成环。
4. 空链表 / 单节点：两种解法都要能直接返回 `head`。
5. 递归终止条件只写 `head == nil` 不够：单节点时 `head.Next` 为 nil，还需要 `head.Next == nil`，否则会解引用空指针。

#### 建议测试案例

```text
[]           → []
[1]          → [1]
[1,2]        → [2,1]
[1,2,3]      → [3,2,1]
[1,2,3,4]    → [4,3,2,1]
```

#### 可迁移的规律

- **头插法 / 尾插法**：反转、重排链表问题的基础（25 K 个一组翻转、92 反转区间）。
- **“改指针前先保存”**是链表题的通用纪律。
- **递归“递到边界、归时接线”**的思路可迁移到树的前序/后续处理。

#### 来源说明

- [LeetCode 206. 反转链表题解列表](https://leetcode.cn/problems/reverse-linked-list/solutions/)
- [代码随想录：0206.翻转链表](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0206.翻转链表.md)
- 参考视频：灵茶山艾府《两种方法：递归 / 迭代，本质是尾插法和头插法》（基础算法精讲 06）。

#### 重做记录

> 2026-08-20：完成迭代头插 + 递归尾插；重做时重点检查递归里 `head.Next = nil` 的成环问题和返回 `pre`。

---

### 题目 141：环形链表

#### 题目摘要

- **题目链接**：[LeetCode 141. 环形链表](https://leetcode.cn/problems/linked-list-cycle/)
- **输入**：链表头节点 `head`。
- **输出**：是否存在环（`bool`）。
- **关键约束**：节点数 `[0, 10^4]`；测试中的 `pos` 只用于构造。
- **核心模式**：快慢指针（Floyd 判圈）。
- **面试必须说清**：快慢指针为何必相遇？循环条件怎样避免 `nil` 解引用？
- **本地测试标准**：无环、单点自环、尾连头/中间。

#### 我的第一反应

> 第一反应是哈希表：把走过的节点指针记下来，重复出现就是有环。后来想到快慢指针：一个走 1 步、一个走 2 步，有环必相遇，空间还能降到 O(1)。写的时候主要在想“为什么必相遇”和“循环条件怎么避免 nil 解引用”。

#### 解法一：哈希表（直观，O(n) 空间）

##### 思路

遍历链表，把访问过的**节点指针**存进 `map[*ListNode]bool`。如果某个节点已经出现过，说明绕回来了，有环。

##### 代码

```go
func hasCycle(head *ListNode) bool {
    seen := map[*ListNode]bool{}
    for head != nil {
        if seen[head] {
            return true
        }
        seen[head] = true
        head = head.Next
    }
    return false
}
```

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(n)\)**。哈希表存所有走过的节点。

哈希表思路正确但空间多花 \(O(n)\)，面试通常要求 O(1) 空间——这就是快慢指针的用武之地。

#### 解法二：快慢指针（Floyd 判圈）

##### 优化突破口：乌龟和兔子

想象乌龟和兔子在同一跑道：乌龟每轮走 1 步，兔子每轮走 2 步。如果跑道是环，兔子必然追上乌龟（套圈）。链表同理：`slow` 走 1 步、`fast` 走 2 步，有环必相遇，无环时 `fast` 先走到末尾。

##### 代码（我的写法）

```go
func hasCycle(head *ListNode) bool {
    slow, fast := head, head // 乌龟和兔子同时从起点出发
    for fast != nil && fast.Next != nil {
        slow = slow.Next      // 乌龟走一步
        fast = fast.Next.Next // 兔子走两步
        if slow == fast {     // 兔子追上乌龟（套圈），说明有环
            return true
        }
    }
    return false // fast 走到了链表末尾，无环
}
```

##### 为什么快慢指针必相遇（面试必须说清）

分两种情况：

- **无环**：`fast` 每轮走 2 步，会先到达 `nil`，循环退出，返回 `false`。
- **有环**：两个指针最终都会进入环。进入环后改用**相对速度**思考：把 `slow` 当作不动，`fast` 相对 `slow` 每轮只前进 1 步（`2 - 1 = 1`）。环长有限，两者的相对距离每轮减 1，从某个正数一路减到 0——**一定会“踩中”而不是跳过**，所以必然相遇。

##### 为什么循环条件不判断 `slow`

`slow` 走的路都是 `fast` 走过的：`fast` 每轮走 2 步，必然经过 `slow` 下一轮要走的节点。好比快人先探路，慢人走的是快人走过的路——只要 `fast` 不是 `nil`，`slow` 就肯定不是 `nil`。

`fast.Next != nil` 则是必须的：`fast` 每次要跳 2 步，需要先确认 `fast.Next` 存在，否则访问 `fast.Next.Next` 会 nil 解引用。

##### 比较的是地址，不是值

`slow == fast` 比较的是两个**指针是否指向同一个节点**（内存地址），不是节点的 `Val`。两个节点值相同但地址不同，不算相遇。

##### 完整运行示例：有环 `1→2→3→4→2`（入口是 2）

| 轮 | slow | fast | 相遇？ |
|---|---|---|---|
| 0 | 1 | 1 | 起点相同，不判 |
| 1 | 2 | 3 | 否 |
| 2 | 3 | 2 | 否 |
| 3 | 4 | 4 | ✅ 返回 true |

无环 `1→2→3→nil`：

| 轮 | slow | fast | 说明 |
|---|---|---|---|
| 1 | 2 | 3 | 本轮结束，`fast.Next == nil` |
| 2 | — | — | 循环条件不满足，退出 → false |

##### 复杂度

- **时间复杂度：\(O(n)\)**。无环时 `fast` 走完链表；有环时两者进入环后追及，总步数仍为 \(O(n)\)。
- **空间复杂度：\(O(1)\)**。只用两个指针。

#### 对比与复盘

| 对比项 | 哈希表 | 快慢指针 |
|---|---|---|
| 时间复杂度 | \(O(n)\) | \(O(n)\) |
| 空间复杂度 | \(O(n)\) | \(O(1)\) |
| 核心操作 | 记录访问过的节点 | 速度差 1，有环必相遇 |
| 优点 | 直观、好写 | 空间最优，可扩展到 142 找入口 |
| 局限 | 空间大 | 需要理解“相对速度”论证 |

#### 本地测试（Day 3 要求：表驱动 + 构造环）

`fromSlice` 只能建无环链表，还要一个造环的辅助函数：

```go
func makeCycle(vals []int, pos int) *ListNode {
    head := fromSlice(vals)
    if pos < 0 || head == nil {
        return head
    }
    var entry, tail *ListNode
    cur, i := head, 0
    for cur != nil {
        if i == pos {
            entry = cur
        }
        tail = cur
        cur = cur.Next
        i++
    }
    tail.Next = entry // 尾节点连回入口
    return head
}

func TestHasCycle(t *testing.T) {
    tests := []struct {
        name string
        vals []int
        pos  int
        want bool
    }{
        {"no-cycle", []int{1, 2, 3, 4}, -1, false},
        {"tail-to-head", []int{1, 2, 3}, 0, true},
        {"tail-to-middle", []int{1, 2, 3, 4}, 1, true},
        {"self-loop", []int{1}, 0, true},
        {"empty", []int{}, -1, false},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := hasCycle(makeCycle(tt.vals, tt.pos))
            if got != tt.want {
                t.Errorf("got %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 漏掉 `fast.Next != nil`：访问 `fast.Next.Next` 时 nil 解引用。
2. 把相遇判断写在移动之前：初始 `slow == fast == head`，会误判为有环。必须先移动再比较。
3. 比较写成 `slow.Val == fast.Val`：不同节点值相同会被误判。
4. 空链表 / 单节点无环：`fast == nil` 或 `fast.Next == nil`，不进循环，返回 false，正确。
5. 忘记“有环时 fast 一定不会越界”：环内 `fast.Next` 永远存在，循环条件天然成立。

#### 建议测试案例

```text
[]              → false
[1]             → false
[1,2,3,4]       → false
[1,2,3,4] 环在 1 → true   // 尾连头
[1,2,3,4] 环在 2 → true   // 尾连中间
[1]       自环    → true   // head.Next = head
```

#### 可迁移的规律

- **快慢指针三连**：141 判环 → 142 找入口 → 找环长度，都是同一套“相对速度”思想。
- **速度差为 1 保证必相遇且不会跳过**：相对距离每轮减 1，最终精确减到 0。
- **快指针先探路**：慢指针永远走在快指针走过的安全路径上。
- **变形题**：[876. 链表的中间结点](https://leetcode.cn/problems/middle-of-the-linked-list/)（快 2 慢 1，fast 到末尾时 slow 在中点）、[142. 环形链表 II](https://leetcode.cn/problems/linked-list-cycle-ii/)（相遇后再找入口）。

#### 来源说明

- [LeetCode 141. 环形链表题解列表](https://leetcode.cn/problems/linked-list-cycle/solutions/)
- [代码随想录：0141.环形链表](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0141.环形链表.md)
- 参考视频：灵茶山艾府《一个视频讲透快慢指针！》（基础算法精讲 07）。

#### 重做记录

> 2026-08-20：完成哈希表 + 快慢指针；重做时重点检查“为什么必相遇”的相对速度论证和 `fast.Next` 判空。

---

### 题目 142：环形链表 II

#### 题目摘要

- **题目链接**：[LeetCode 142. 环形链表 II](https://leetcode.cn/problems/linked-list-cycle-ii/)
- **输入**：链表头节点 `head`。
- **输出**：环入口节点；无环返回 `nil`。
- **关键约束**：节点数 `[0, 10^4]`。
- **核心模式**：快慢指针 + 距离式推导。
- **面试必须说清**：相遇后为何一个从头、一个从相遇点同速走会在入口相遇？
- **本地测试标准**：入口在头/中/尾部自环/无环；必须手绘距离式。

#### 我的第一反应

> 141 学会了快慢指针判环，142 自然想到组合拳：先让快慢指针相遇判环，然后「一个从头、一个从相遇点同速走」，再次相遇就是入口。代码写出来了，但「为什么同速走会在入口相遇」当时没想明白，是靠记住结论写的——这正是本题要补上的距离式推导。

#### 解法一：哈希表（直观，O(n) 空间）

##### 思路

遍历链表，把访问过的**节点指针**记录在哈希表里（官方用 `map[*ListNode]struct{}`，value 用零开销的 `struct{}`）。第一次遇到「已经出现过的节点」，这个节点就是环入口——因为它是绕了一圈之后第一个被重复访问的节点。

##### 代码（LeetCode 官方写法）

```go
func detectCycle(head *ListNode) *ListNode {
    seen := map[*ListNode]struct{}{}
    for head != nil {
        if _, ok := seen[head]; ok {
            return head // 第一次重复访问的节点就是入口
        }
        seen[head] = struct{}{}
        head = head.Next
    }
    return nil
}
```

##### 复杂度

- **时间复杂度：\(O(n)\)**。每个节点至多访问一次。
- **空间复杂度：\(O(n)\)**。哈希表存所有访问过的节点。

哈希表思路直观、正确，但空间多花 \(O(n)\)。面试通常会追问 O(1) 空间的做法——快慢指针。

#### 解法二：快慢指针 + 距离式推导（Floyd 判圈 + 找入口）

##### 优化突破口

沿用 141 的快慢指针判环：`slow` 走 1 步、`fast` 走 2 步，有环必相遇。关键的新问题是：**相遇点并不是入口**，怎么从相遇点再推出入口？

答案藏在距离式里：设出几个距离，用「fast 的路程 = 2 × slow 的路程」列方程，就能解出「从头走 \(a\) 步 = 从相遇点绕环走 \((L-b)\) 步」，两者落在同一个点——入口。

##### 代码（我的写法）

```go
func detectCycle(head *ListNode) *ListNode {
    slow, fast := head, head
    for fast != nil && fast.Next != nil {
        slow = slow.Next
        fast = fast.Next.Next
        if slow == fast { // 有环，slow 停在相遇点
            for slow != head { // 一个从头、一个从相遇点，同速走
                head = head.Next
                slow = slow.Next
            }
            return slow // 再次相遇 = 环入口
        }
    }
    return nil
}
```

##### LeetCode 官方写法

官方题解把「从头出发的指针」单独命名为 `p`，不直接改写形参 `head`；判环循环也写得不一样（循环条件只判 `fast != nil`，在循环体内兜底无环情况），但核心逻辑与我的写法完全一致：

```go
func detectCycle(head *ListNode) *ListNode {
    slow, fast := head, head
    for fast != nil {
        slow = slow.Next
        if fast.Next == nil {
            return nil // fast 走到链表末尾，无环
        }
        fast = fast.Next.Next
        if fast == slow { // 第一次相遇
            p := head
            for p != slow {
                p = p.Next
                slow = slow.Next
            }
            return p
        }
    }
    return nil
}
```

两种循环结构对比：

| | 我的写法 | 官方写法 |
|---|---|---|
| 判环循环条件 | `fast != nil && fast.Next != nil` | `fast != nil` |
| 无环兜底 | 循环条件天然退出 | 循环体内 `if fast.Next == nil { return nil }` |
| 移动顺序 | 先移动 `slow`/`fast`，再比较 | 先走 `slow`，兜底后走 `fast`，再比较 |
| 找入口指针 | 直接改写形参 `head` | 新变量 `p := head` |

两种结构完全等价：官方写法把「无环退出」写得更显式，我的写法把判空集中到循环条件上。面试时写哪一种都可以，关键是说清两者对应关系。

##### 距离式推导（面试必须说清，Day 3 要求手绘）

把链表抽象成「一段直线 + 一个环」：

```text
直线段 a 步:        head ──► 入口
环 L 步（从入口出发）: 入口 ──► …… ──► 相遇点 ──► …… ──► 回到入口
                          │◄─ b ─►│◄── L−b ──►│
```

定义三个量：

- \(a\)：头节点到环入口的距离（直线段长度）；
- \(b\)：从入口出发、沿前进方向到相遇点的距离；
- \(L\)：环的长度。

再设 `fast` 在环里比 `slow` 多跑了 \(n\) 整圈（\(n \ge 1\)，至少要追上必须多绕至少一圈）。相遇时：

- `slow` 走了 \(a + b\)；
- `fast` 走了 \(a + nL + b\)（直线段 + 完整的 \(n\) 圈 + 追上之前最后一段 \(b\)）。

`fast` 速度是 `slow` 的 2 倍，所以路程也是 2 倍：

\[
2(a + b) = a + nL + b
\]

移项：

\[
a = nL - b = (n-1)L + (L - b)
\]

这个式子就是答案：**从头走 \(a\) 步，等价于从相遇点沿前进方向绕 \((n-1)\) 圈后再走 \((L-b)\) 步**，两者落在同一个点。

- \(L - b\) 正好是「相遇点沿前进方向回到入口」的距离；
- 多绕的 \((n-1)L\) 只是整数圈，不改变落点。

所以：一个新指针（官方命名为 `p`）从头出发、`slow` 从相遇点出发，**同速、每次走 1 步**，走 \(a\) 步后必然同时到达环入口。

常见的 \(n=1\) 情形（`fast` 进环后第一圈就追上 `slow`）：式子简化为 \(a = L - b\)，更直观。

官方题解的记号略有不同：它把「相遇点沿前进方向回到入口的距离」记为 \(c\)（即 \(c = L - b\)），并把 fast 在环里多走的圈数记为 \(n\)，推导结果写为：

\[
a = c + (n-1)(b+c)
\]

与我的 \(a = (n-1)L + (L-b)\) 完全等价，只是把 \(L\) 拆成了 \(b+c\)。

##### 完整运行示例：`3→2→0→−4` 环在 1（入口是 2）

链表：`3 → 2 → 0 → −4 →(回)2`。这里 \(a=1\)（3→2），环 \(L=3\)（2→0→−4→2）。

第一阶段：判环。

| 轮 | slow | fast | 说明 |
|---|---|---|---|
| 0 | 3 | 3 | 起点相同，不判 |
| 1 | 2 | 0 | 未相遇 |
| 2 | 0 | 2 | 未相遇 |
| 3 | −4 | −4 | ✅ 相遇，进入第二阶段 |

第二阶段：找入口。`ptr` 从头出发，`slow` 从相遇点 −4 出发，同速走。

| 步 | ptr（head） | slow | 说明 |
|---|---|---|---|
| 0 | 3 | −4 | 起点不同 |
| 1 | 2 | 2 | ✅ 相遇，返回 2 = 入口 |

验证距离式：相遇点 −4，即 \(b=2\)（2→0→−4），\(L-b=1\)。从头走 \(a=1\) 步到 2；从 −4 沿前进方向走 1 步也到 2，符合 \(a = L-b\)（\(n=1\)）。

##### 逐行理解

- `slow, fast := head, head`：同一起点出发。
- `for fast != nil && fast.Next != nil`：判环循环条件（同 141，避免访问 `fast.Next.Next` 时解引用 nil）。
- `if slow == fast`：有环，此时 `slow` 停在相遇点。
- 内层 `for slow != head`：`head` 在这里兼职「从头出发的指针」，`slow` 从相遇点出发，两者一次都走 1 步；同速靠的就是距离式保证的「会在入口精确碰头」。
- `return slow`：内层循环结束时，`slow == head`，这个节点就是入口。距离式保证它一定会终止，所以内层不需要判 nil。
- 外层循环自然退出（`fast` 走到末尾）：无环，返回 `nil`。

一点代码风格提示：内层循环直接改写形参 `head` 在这个函数里没问题（此时已经不再需要原来的头节点），但为了可读性，官方写法另起 `p := head` 更清晰，也避免以后在函数尾部还想用 `head` 时发现它已经被改掉。

##### 复杂度

- **时间复杂度：\(O(n)\)**。判环阶段 slow 走过的距离不会超过链表总长度；找入口阶段走过的距离也不会超过链表总长度，合计 \(O(n) + O(n) = O(n)\)。
- **空间复杂度：\(O(1)\)**。只用了 `slow`、`fast`、`p` 三个指针。

##### 关键不变量

- 判环阶段：`fast` 的路程始终是 `slow` 的 2 倍。
- 找入口阶段：`p` 和 `slow` 速度相同，且由距离式保证相遇点唯一确定 = 入口。

#### 对比与复盘

| 对比项 | 哈希表 | 快慢指针 |
|---|---|---|
| 时间复杂度 | \(O(n)\) | \(O(n)\) |
| 空间复杂度 | \(O(n)\) | \(O(1)\) |
| 核心操作 | 记录访问过的节点 | 判环 + 距离式找入口 |
| 优点 | 直观，不需要数学推导 | 空间最优，面试标准答案 |
| 局限 | 空间大 | 需要完整推导距离式 |

#### 本地测试（Day 3 要求：表驱动 + 构造环 + 验证无环）

复用 141 的 `makeCycle`（尾节点连回 `pos` 位置的节点）：

```go
func TestDetectCycle(t *testing.T) {
    tests := []struct {
        name string
        vals []int
        pos  int
        want int // 期望入口节点的值；-1 表示期望 nil
    }{
        {"tail-to-middle", []int{3, 2, 0, -4}, 1, 2},
        {"tail-to-head", []int{1, 2}, 0, 1},
        {"self-loop", []int{1}, 0, 1},
        {"entry-middle", []int{1, 2, 3, 4}, 2, 3},
        {"no-cycle", []int{1, 2, 3}, -1, -1},
        {"empty", []int{}, -1, -1},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := detectCycle(makeCycle(tt.vals, tt.pos))
            if tt.want == -1 {
                if got != nil {
                    t.Errorf("got %v, want nil", got.Val)
                }
                return
            }
            if got == nil || got.Val != tt.want {
                t.Errorf("got %v, want entry value %d", got, tt.want)
            }
        })
    }
}
```

注意：测试用「入口节点的值」断言，依赖测试用例里节点值不重复。如果链表允许值重复（如 `[1,1]`），就要改用指针相等断言：构造环时把入口节点指针单独存下来，最后比 `got == entryNode`。

#### 易错点

1. 判环循环条件漏 `fast.Next != nil`：访问 `fast.Next.Next` 时 nil 解引用。
2. 相遇后直接返回 `slow`：那是**相遇点**不是入口。
3. 内层循环速度不一致：必须「同速」，否则会错过入口。
4. 距离式推导漏写 \(n\)：`fast` 可能绕了不止一圈，必须写 \(a = nL - b\) 再化简为 \((n-1)L + (L-b)\)。
5. 用值比较找入口：应该用**指针相等**（`p != slow` 比较的是节点地址），两个值相同的节点不算同一个节点。
6. 改写形参 `head` 后还想在函数里继续用原来的头：本函数没有后续使用所以安全，但养成「另起 `p`」的习惯更稳。

#### 建议测试案例

```text
[3,2,0,-4] 环在 1 → 返回节点 2     // 常见例子，入口在中间
[1,2]      环在 0 → 返回节点 1     // 尾连头，入口就是 head
[1]        环在 0 → 返回节点 1     // 单点自环，入口=头=相遇点
[1,2,3,4]  环在 2 → 返回节点 3     // 入口在更深处
[1,2,3]    无环   → nil
[]         无环   → nil
```

#### 可迁移的规律

- **141 → 142 是一套组合拳**：先判环（相对速度），再找入口（距离式）。
- **距离式的通用步骤**：设 \(a\) / \(b\) / \(L\) → 列「2 × slow 路程 = fast 路程」→ 移项得到「从头走的距离 = 从相遇点绕圈走的距离」。
- **环上追及问题的通法**：路程差 = 整数圈。
- **变形题**：找环的长度（相遇后 `slow` 原地绕一圈数步数）；[287. 寻找重复数](https://leetcode.cn/problems/find-the-duplicate-number/)（把数组下标当成链表节点，用同一套快慢指针找「环入口」）。

#### 来源说明

- [LeetCode 142. 环形链表 II 题解列表](https://leetcode.cn/problems/linked-list-cycle-ii/solutions/)
- 力扣官方题解《环形链表 II》（作者：力扣官方题解，2020.10.09）：哈希表 + 快慢指针两种方法，代码与推导按官方原文整理。
- [代码随想录：0142.环形链表](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0142.环形链表II.md)

#### 重做记录

> 2026-08-20：完成哈希表 + 快慢指针（含距离式推导）；重做时**不看资料**完整推导 \(a = (n-1)L + (L-b)\)，并解释「一个从头、一个从相遇点同速走为何在入口相遇」。


---

### 题目 21：合并两个有序链表

#### 题目摘要

- **题目链接**：[LeetCode 21. 合并两个有序链表](https://leetcode.cn/problems/merge-two-sorted-lists/)
- **输入**：两个升序链表 `list1`、`list2`。
- **输出**：合并后的升序链表头。
- **关键约束**：节点数 `[0, 50]`；可复用原节点。
- **核心模式**：dummy + 双指针归并。
- **面试必须说清**：`dummy` 和 `tail` 各代表什么？一条链表耗尽后怎么办？
- **本地测试标准**：两空、一空、重复、交错；输出有序且无环。

#### 我的第一反应

> 看到「合并两个有序链表」第一反应就是归并：两个指针各指一个链表的头，谁小接谁。写的时候最怕头节点特判，所以直接上 dummy 哨兵 + `cur` 尾指针，循环结束后把剩下的链表整段接上。比较时用了 `>=`，相等时取 `list2`，这也是合法的。

#### 解法一：迭代（尾插法）

##### 为什么需要 dummy（面试必须说清）

dummy 是**哨兵节点**，作为新链表头节点之前的占位节点。`cur` 从 dummy 开始，每轮把选中的节点接到 `cur.Next` 再前进。好处：

- 不需要单独讨论「第一个节点谁来当头」，最后统一返回 `dummy.Next`；
- 两个链表都为空时 `dummy.Next` 自然是 `nil`，不用特判。

##### 代码（我的写法）

```go
func mergeTwoLists(list1 *ListNode, list2 *ListNode) *ListNode {
    var dummy = ListNode{} // 哨兵节点
    cur := &dummy          // cur 指向新链表当前末尾（相当于 tail）
    for list1 != nil && list2 != nil {
        if list1.Val >= list2.Val {
            cur.Next = list2
            list2 = list2.Next
        } else {
            cur.Next = list1
            list1 = list1.Next
        }
        cur = cur.Next
    }
    if list1 == nil {
        cur.Next = list2
    } else if list2 == nil {
        cur.Next = list1
    }
    return dummy.Next
}
```

##### 灵茶山艾府写法（对照）

```go
func mergeTwoLists(list1, list2 *ListNode) *ListNode {
    dummy := ListNode{} // 哨兵节点
    cur := &dummy       // cur 指向新链表的末尾
    for list1 != nil && list2 != nil {
        if list1.Val < list2.Val {
            cur.Next = list1
            list1 = list1.Next
        } else { // 相等的情况加哪个节点都是可以的
            cur.Next = list2
            list2 = list2.Next
        }
        cur = cur.Next
    }
    if list1 != nil {
        cur.Next = list1
    } else {
        cur.Next = list2
    }
    return dummy.Next
}
```

唯一的区别在相等时：灵茶用 `<` 走 else 取 `list2`，我用 `>=` 直接并入 `list2`，效果完全一样。循环结束后的拼接：灵茶用 `if/else`，我用 `if/else if`，都覆盖了「list1 先耗尽」和「list2 先耗尽」两种情况。

##### 逐行理解

- `var dummy = ListNode{}`：哨兵节点（值类型），`cur := &dummy` 取它的地址，cur 指向新链表末尾。
- `for list1 != nil && list2 != nil`：只要还有一条链表没耗尽就继续——一旦某条耗尽，剩余部分可以**整体拼接**，不需要再逐节点比较。
- 每轮：比较两个当前节点的值，把较小的接到 `cur.Next`，并推进对应链表的指针；最后 `cur = cur.Next` 前进到新的末尾。
- 相等时取谁都行，两条分支保持一致即可。
- 循环结束后：`list1 == nil` 说明 list2 还剩，直接 `cur.Next = list2`；`list2 == nil` 同理。剩余部分本身有序、且值都大于等于已合并部分，整段接上不会破坏有序。
- `return dummy.Next`：跳过哨兵，返回真正的头节点。

##### 完整运行示例（逐轮表格）

`list1 = 1→2→4`，`list2 = 1→3→4`（LeetCode 示例）。

| 轮 | list1 当前 | list2 当前 | `list1.Val >= list2.Val` | 接入节点 | 更新后 list1 | 更新后 list2 |
|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 1>=1 ✅ | list2 的 1 | 1→2→4 | 3→4 |
| 2 | 1 | 3 | 1>=3 ❌ | list1 的 1 | 2→4 | 3→4 |
| 3 | 2 | 3 | 2>=3 ❌ | list1 的 2 | 4 | 3→4 |
| 4 | 4 | 3 | 4>=3 ✅ | list2 的 3 | 4 | 4 |
| 5 | 4 | 4 | 4>=4 ✅ | list2 的 4 | 4 | nil |

循环结束：`list1` 还剩 4，执行 `cur.Next = list1`。

结果：`1(来自 list2) → 1(来自 list1) → 2 → 3 → 4 → 4`，即 `[1,1,2,3,4,4]`。✅

##### 复杂度

- **时间复杂度：\(O(n+m)\)**。`n` 为 `list1` 长度、`m` 为 `list2` 长度，每个节点恰好被访问并接入一次。
- **空间复杂度：\(O(1)\)**。只用了 `dummy` 和 `cur` 两个额外变量（复用原节点，不新建）。

#### 解法二：递归（头插法）

##### 核心思路

直接把 `mergeTwoLists` 本身当递归函数：每次比较两个链表的当前节点，**较小的节点插在「递归合并结果」的前面**（所以叫头插法）。

- 递归边界：某条链表为空，直接返回另一条作为合并结果（两条都空则返回 `nil`）；
- 若 `list1.Val < list2.Val`：取出 `list1`，递归合并 `list1.Next` 和 `list2`，把返回的链表接到 `list1.Next` 上，返回 `list1`；
- 否则对称地处理 `list2`。

虽然叫「头插法」，但执行顺序是：**先递到底，归的时候从后往前**，把当前节点接到子结果的前面——和 206 递归反转链表的「递到边界、归时接线」是同一个结构。

##### 代码（灵茶山艾府）

```go
func mergeTwoLists(list1, list2 *ListNode) *ListNode {
    if list1 == nil {
        return list2 // 注：如果都为空则返回空
    }
    if list2 == nil {
        return list1
    }
    if list1.Val < list2.Val {
        list1.Next = mergeTwoLists(list1.Next, list2)
        return list1
    }
    list2.Next = mergeTwoLists(list1, list2.Next)
    return list2
}
```

##### 完整运行示例（递归调用树）

`list1 = 1→3`，`list2 = 2→4`：

```text
mergeTwoLists(1, 2)
  ├─ 1 < 2 → 1.Next = mergeTwoLists(3, 2)
  │            ├─ 2 < 3 → 2.Next = mergeTwoLists(3, 4)
  │            │            ├─ 3 < 4 → 3.Next = mergeTwoLists(nil, 4)
  │            │            │            └─ list1 == nil → 返回 4
  │            │            └─ 3.Next = 4 → 返回 3→4
  │            └─ 2.Next = 3→4 → 返回 2→3→4
  └─ 1.Next = 2→3→4 → 返回 1→2→3→4
```

结果 `[1,2,3,4]`。每一层的「返回 xxx」都是该子问题合并后的链表头。

##### 复杂度

- **时间复杂度：\(O(n+m)\)**。每层递归比较一对节点，总共比较 \(n+m\) 次。
- **空间复杂度：\(O(n+m)\)**。递归调用栈深度最多等于合并后的长度。

#### 对比与复盘

| 对比项 | 迭代（尾插法） | 递归（头插法） |
|---|---|---|
| 拼接方向 | 从头到尾逐个拼接 | 先递到底，再从尾到头接线 |
| 核心动作 | `cur.Next = 较小的节点` | `较小节点.Next = 递归结果` |
| 空间复杂度 | \(O(1)\) | \(O(n+m)\) 栈 |
| 优点 | 空间小、面试首选 | 代码极短、思路优雅 |
| 局限 | 需要维护 dummy/cur | 链表很长时可能栈溢出 |

#### 本地测试（表驱动 + 无环验证）

复用专题三的 `fromSlice` / `toSlice`（`toSlice` 遍历链表，如果结果意外成环会一直遍历直到超时，所以「能正常返回」本身就是无环验证；更严格可再用 Floyd 检测断言一次）：

```go
func TestMergeTwoLists(t *testing.T) {
    tests := []struct {
        name string
        a, b []int
        want []int
    }{
        {"both-empty", []int{}, []int{}, []int{}},
        {"a-empty", []int{}, []int{3, 4}, []int{3, 4}},
        {"b-empty", []int{1, 2}, []int{}, []int{1, 2}},
        {"duplicates", []int{1, 1, 2}, []int{1, 3}, []int{1, 1, 1, 2, 3}},
        {"interleaved", []int{1, 2, 4}, []int{1, 3, 4}, []int{1, 1, 2, 3, 4, 4}},
        {"single", []int{5}, []int{1, 2}, []int{1, 2, 5}},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := toSlice(mergeTwoLists(fromSlice(tt.a), fromSlice(tt.b)))
            if !slices.Equal(got, tt.want) {
                t.Errorf("got %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 返回 `dummy` 而不是 `dummy.Next`：dummy 是哨兵，不是链表头。
2. 循环结束只处理一种剩余情况：必须覆盖「list1 剩」和「list2 剩」两种（`if/else if` 或 `if/else`）。
3. 比较分支不一致：相等时取哪个节点都行，但两条分支要保持一致，别写出有时取 list1、有时取 list2 的混乱代码。
4. 忘记推进被选中链表的指针：会反复接入同一个节点，最终成环或死循环。
5. 递归忘记接线：必须 `list1.Next = mergeTwoLists(...)` 并把 `list1` 返回，只调用不赋值会丢掉子结果。
6. 递归边界少写一个：`list1 == nil` 返回 `list2` 已经同时覆盖「两个都空」（返回 nil），但两个边界都要写，否则空链表会 nil 解引用。

#### 建议测试案例

```text
[] + []           → []            // 两空
[] + [3,4]        → [3,4]         // 一边空
[1,2] + []        → [1,2]         // 另一边空
[1,1,2] + [1,3]   → [1,1,1,2,3]   // 重复值
[1,2,4] + [1,3,4] → [1,1,2,3,4,4] // 交错 + 相等
[5] + [1,2]       → [1,2,5]       // 单节点 + 多节点
```

#### 可迁移的规律

- **哨兵节点 dummy**：把「头节点特判」统一掉，迁移到 19（删除倒数第 N 个）、86（分隔链表）等需要处理头节点的题。
- **归并双指针**：88 合并两个有序数组（从后往前填）、23 合并 K 个升序链表（多路归并 + 优先队列）。
- **递归「递到边界、归时接线」**：和 206 递归反转链表同构，都是子问题返回后把当前节点接上去。

#### 来源说明

- [LeetCode 21. 合并两个有序链表题解列表](https://leetcode.cn/problems/merge-two-sorted-lists/solutions/)
- 灵茶山艾府《两种方法：迭代（尾插法）/ 递归（头插法）》（基础算法精讲 06：哨兵技巧；基础算法精讲 09：递归理解）

#### 重做记录

> 2026-08-22：完成迭代尾插 + 递归头插；重做时重点检查 `dummy.Next` 的返回、循环结束后剩余链表的拼接、递归返回值的接线。

> 待补充。

---

### 题目 19：删除链表的倒数第 N 个结点

#### 题目摘要

- **题目链接**：[LeetCode 19. 删除链表的倒数第 N 个结点](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/)
- **输入**：链表头 `head` 和整数 `n`。
- **输出**：删除倒数第 `n` 个节点后的链表头。
- **关键约束**：题目保证 `n` 合法（`1 <= n <= size`）。
- **核心模式**：快慢指针 + dummy。
- **面试必须说清**：为什么需要 `dummy`？快慢间隔是 `n` 还是 `n+1`？
- **本地测试标准**：删头/尾/单节点。

#### 我的第一反应

> 第一反应是「反转删除再反转」：先用 206 的迭代三指针把链表反转，这样倒数第 n 个就变成正数第 n 个，再用 dummy 删掉，最后反转回去。能 AC 但明显绕了远路——链表被反转了两次。看了灵茶的解法才意识到：前后指针（尺子）一次遍历才是正路，而且在「到达链表末尾的瞬间」就能知道倒数第 n 个节点。

#### 解法一：反转删除再反转（我的写法）

##### 思路

三步走：

1. 反转链表（206 的三指针迭代）——倒数第 n 个变成正数第 n 个；
2. 用 dummy + `cur` 找到正数第 n 个节点的前驱，执行 `cur.Next = cur.Next.Next` 删除；
3. 再把链表反转回来。

##### 代码（我的写法）

```go
func removeNthFromEnd(head *ListNode, n int) *ListNode {
    // 1. 反转删除再反转
    reverse := func(h *ListNode) *ListNode {
        var pre, cur *ListNode = nil, h
        for cur != nil {
            next := cur.Next
            cur.Next = pre
            pre = cur
            cur = next
        }
        return pre
    }
    reversedHead := reverse(head)
    dummy := &ListNode{}
    cur := dummy
    cur.Next = reversedHead
    for i := 0; i < n-1; i++ {
        cur = cur.Next
    }
    cur.Next = cur.Next.Next
    return reverse(dummy.Next)
}
```

##### 逐行理解

- `reverse` 闭包：206 的三指针反转，保存 `next` 再改 `cur.Next`，返回新头。
- `reversedHead := reverse(head)`：反转后，原链表倒数第 n 个节点变成了**正数第 n 个节点**，删除目标从「从后数」变成「从前数」。
- `dummy := &ListNode{}` + `cur.Next = reversedHead`：因为 n 可能等于链表长度（要删的是反转后的第一个节点 = 原链表尾节点），用 dummy 统一处理删头。
- `for i := 0; i < n-1; i++ { cur = cur.Next }`：走 n−1 步，让 `cur` 停在要删节点（正数第 n 个）的**前驱**。
- `cur.Next = cur.Next.Next`：跳过被删节点。
- `return reverse(dummy.Next)`：删除完成后**再反转回来**，这一步不能省。

##### 完整运行示例（逐轮表格）

`head = 1→2→3→4→5`，`n = 2`，期望输出 `1→2→3→5`。

| 阶段 | 链表状态 |
|---|---|
| 反转 | `1→2→3→4→5` → `5→4→3→2→1` |
| 找前驱 | `dummy→5→4→3→2→1`，cur 走 `n-1=1` 步停在节点 5（前驱） |
| 删除 | `cur.Next = cur.Next.Next`，删掉 4 → `dummy→5→3→2→1` |
| 再反转 | `1→2→3→5` ✅ |

##### 复杂度

- **时间复杂度：\(O(m)\)**。`m` 为链表长度：两次反转各 \(O(m)\)，找前驱 \(O(n)\)，合计 \(O(m)\)，但常数是「两个完整来回」。
- **空间复杂度：\(O(1)\)**。只用常数个指针。

##### 主要关注点

思路直白、复用 206 和 dummy，能过但常数大：每个节点被重连两次。面试时可以作为热身思路主动讲出来，然后立刻指出「前后指针一次遍历」更优，展示你会对比取舍。

#### 解法二：前后指针（尺子法，灵茶山艾府）

##### 优化突破口：一把长度固定的尺子

想象一把长度固定为 n 的尺子：右端点在正数第 n 个节点，左端点在链表头部。向右移动尺子，当右端点到达链表末尾时，左端点正好在倒数第 n 个节点。

因为要**删除**，需要的是倒数第 n 个节点的前驱（倒数第 n+1 个节点），所以把尺子拉开成「右端点在正数第 n+1 个节点」：右指针先走 n 步，然后左右一起走，右到末尾时左就在前驱上。

##### 为什么需要 dummy（面试必须说清）

如果 `n` 等于链表长度，要删的是头节点，此时不存在「正数第 n+1 个节点」。在头节点前插入哨兵节点 `dummy` 后，第 n+1 个节点始终存在，删头也被统一成普通删除，最后返回 `dummy.Next` 即可。

##### 代码（灵茶山艾府）

```go
func removeNthFromEnd(head *ListNode, n int) *ListNode {
    // 由于可能会删除链表头部，用哨兵节点简化代码
    dummy := &ListNode{Next: head}
    left, right := dummy, dummy
    for ; n > 0; n-- {
        right = right.Next // 右指针先向右走 n 步
    }
    for right.Next != nil {
        left = left.Next
        right = right.Next // 左右指针一起走
    }
    left.Next = left.Next.Next // 左指针的下一个节点就是倒数第 n 个节点
    return dummy.Next
}
```

##### 逐行理解

- `dummy := &ListNode{Next: head}`：哨兵节点，统一删头场景。
- `left, right := dummy, dummy`：尺子两端都从 dummy 出发。
- `for ; n > 0; n-- { right = right.Next }`：右指针先走 n 步，拉开尺子——此时 left 与 right 之间隔着 n 个节点。
- `for right.Next != nil`：右指针走到**最后一个节点**就停（判断 `right.Next` 而不是 `right`，就是为了停在末尾而不是越界）。
- 循环结束后，left 正好停在倒数第 n+1 个节点（要删节点的前驱）。
- `left.Next = left.Next.Next`：跳过倒数第 n 个节点，完成删除。
- `return dummy.Next`：跳过哨兵返回新头。

##### 为什么间隔是 n 而不是 n+1

left 从 dummy（第 0 个位置）出发，right 走 n 步后站在正数第 n 个节点。两者一起走，right 到达最后节点（正数第 m 个）时，left 在正数第 m−n 个节点，也就是**倒数第 n+1 个节点**——恰好是前驱。如果只想要倒数第 n 个节点本身（不删除），right 先走 n−1 步就行；删除需要前驱，所以先走 n 步。

##### 完整运行示例（逐轮表格）

`head = 1→2→3→4→5`（记 dummy 为 0），`n = 2`。

第一步：right 先走 2 步，`right = 2`，left 停在 dummy。

第二步：左右一起走。

| 轮 | left | right | right.Next |
|---|---|---|---|
| 初始 | 0 (dummy) | 2 | 3 |
| 1 | 1 | 3 | 4 |
| 2 | 2 | 4 | 5 |
| 3 | 3 | 5 | nil → 停 |

循环结束：left = 3，它的下一个节点 4 就是倒数第 2 个，执行 `left.Next = left.Next.Next` 删掉 4。

结果 `1→2→3→5` ✅。

##### 答疑：为什么算「一次遍历」？优点是什么？

节点其实会被两个指针各访问一次，但算法在**到达链表末尾的瞬间**就已经知道了倒数第 n 个节点，不需要先数一遍长度再走第二趟。优点是当 n 较小、节点分配有局部性时，前后指针的 cache miss 更少（相比「一个指针跑两趟」）。

##### 复杂度

- **时间复杂度：\(O(m)\)**。`m` 为链表长度：right 先走 n 步，再一起走 m−n 步，合计 \(m+1\) 步。
- **空间复杂度：\(O(1)\)**。只用 left/right/dummy 三个指针。

#### 对比与复盘

| 对比项 | 反转删除再反转 | 前后指针（尺子法） |
|---|---|---|
| 时间复杂度 | \(O(m)\)，常数大（反转两次） | \(O(m)\)，单趟 |
| 空间复杂度 | \(O(1)\) | \(O(1)\) |
| 遍历次数 | 反转 2 遍 + 查找 1 遍 | 1 遍（每节点至多被两个指针访问） |
| 核心技巧 | 206 反转 + dummy 删节点 | 尺子/快慢指针 + dummy |
| 优点 | 思路直白、复用已有代码 | 简洁、一次遍历、cache 友好 |
| 局限 | 多出两次反转，常数大 | 需要理解尺子的距离语义 |

#### 本地测试（Day 3 要求：表驱动）

复用专题三的 `fromSlice` / `toSlice`：

```go
func TestRemoveNthFromEnd(t *testing.T) {
    tests := []struct {
        name string
        in   []int
        n    int
        want []int
    }{
        {"remove-head", []int{1, 2, 3}, 3, []int{2, 3}},
        {"remove-tail", []int{1, 2, 3, 4, 5}, 1, []int{1, 2, 3, 4}},
        {"remove-middle", []int{1, 2, 3, 4, 5}, 2, []int{1, 2, 3, 5}},
        {"single-node", []int{1}, 1, []int{}},
        {"two-nodes-remove-head", []int{1, 2}, 2, []int{2}},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := toSlice(removeNthFromEnd(fromSlice(tt.in), tt.n))
            if !slices.Equal(got, tt.want) {
                t.Errorf("got %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 快慢间隔写错：right 先走 **n−1** 步会定位到倒数第 n 个节点**本身**；删除需要它的前驱，所以先走 **n** 步。
2. 忘记 dummy：`n` 等于链表长度时要删头，没有 dummy 就得特判。
3. 循环条件写成 `right != nil`：会多走一步，left 停在倒数第 n 个节点本身而不是前驱；要停在最后一个节点，必须判 `right.Next != nil`。
4. 反转法里 `cur` 走错步数：要删正数第 n 个节点，cur 只走 n−1 步停在它的前驱，多走/少走都会删错节点。
5. 反转法返回前忘了再反转，或返回了反转后的头。
6. 依赖先算链表长度：能 AC 但不如前后指针优雅，面试时先讲尺子法。

#### 建议测试案例

```text
[1,2,3]    n=3 → [2,3]      // 删头（n == 链表长度）
[1,2,3,4,5] n=1 → [1,2,3,4] // 删尾
[1,2,3,4,5] n=2 → [1,2,3,5] // 删中间
[1]        n=1 → []         // 单节点，删完为空
[1,2]      n=2 → [2]        // 删头且剩一个节点
```

#### 可迁移的规律

- **dummy 哨兵节点**：删头特判统一化（19、21、86 分隔链表都靠它）。
- **前后指针**：找「倒数第 k 个节点」的通用技巧；876 找链表中点、141/142 判环都是「两个指针不同步长」的变体。
- **反转再操作再反转**：偶尔能救命（如判断回文链表可以先找中点再反转后半段），但要意识到常数开销，面试要能指出更优解。
- **`while node` vs `while node.Next`**：要遍历到最后一个节点用 `node != nil`；要停在倒数第二个节点（前驱）用 `node.Next != nil`。

#### 来源说明

- [LeetCode 19. 删除链表的倒数第 N 个结点题解列表](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/solutions/)
- 灵茶山艾府《【视频讲解】前后指针，简洁写法》（基础算法精讲 08）。

#### 重做记录

> 2026-08-22：完成「反转删除再反转」+ 前后指针（尺子法）；重做时 12 分钟盲写，重点检查快慢间隔是 n 还是 n+1、dummy 解决删头、循环用 `right.Next != nil` 停在末尾。

---

### 题目 2：两数相加

#### 题目摘要

- **题目链接**：[LeetCode 2. 两数相加](https://leetcode.cn/problems/add-two-numbers/)
- **输入**：两个非空链表，表示两个逆序存储的非负整数。
- **输出**：两数之和的逆序链表。
- **关键约束**：数字可能非常大，不能整体转成整数计算。
- **核心模式**：模拟加法 + `carry`。
- **面试必须说清**：循环条件为何还要包含 `carry`？不同长度怎么统一？
- **本地测试标准**：长度不同、连续进位、最后新增位。

#### 我的第一反应

> 数字最低位在链表头，正好和手算加法一致：从个位开始逐位相加、满 10 进 1。第一反应就是迭代：dummy 哨兵 + `cur` 尾指针，循环条件写成 `l1 != nil || l2 != nil || carry != 0`，把最后一位可能多出的进位也一起算进去。写完对照灵茶题解，发现和它的迭代法几乎一模一样，说明思路已经到位。

#### 解法一：迭代（尾插法，我的写法）

##### 思路

模拟竖式加法：每轮取出 l1、l2 当前节点值和进位相加，`sum % 10` 是当前位，`sum / 10` 是新的进位。由于数字可能极大，**不能整体转成整数**，必须一位一位处理。

两个关键技巧：

- **dummy 哨兵**：第一次循环时还没有「新链表末尾」可以接节点，用 dummy 当初始空链表，最后返回 `dummy.Next`；
- **循环条件三合一**：`l1 != nil || l2 != nil || carry != 0`，三条链表都耗尽且无进位才算完。

##### 代码（我的写法）

```go
func addTwoNumbers(l1 *ListNode, l2 *ListNode) *ListNode {
    dummy := &ListNode{}
    cur := dummy
    carry := 0
    for l1 != nil || l2 != nil || carry != 0 {
        sum := 0
        if l1 != nil {
            sum += l1.Val
            l1 = l1.Next
        }
        if l2 != nil {
            sum += l2.Val
            l2 = l2.Next
        }
        sum += carry
        carry = sum / 10
        cur.Next = &ListNode{Val: sum % 10}
        cur = cur.Next
    }
    return dummy.Next
}
```

灵茶山艾府的迭代写法与本代码完全一致（只把 `carry = sum/10` 放在创建节点之后，顺序不影响结果）。这说明模拟加法的迭代写法是「标准答案」级别的共识。

##### 逐行理解

- `dummy := &ListNode{}`：哨兵节点，避免「第一次循环无末尾可接」的特判。
- `cur := dummy`：尾指针，每次把新节点接到 `cur.Next` 再前进。
- `carry := 0`：进位，初始为 0。
- 循环条件：l1、l2 还有节点，或者进位还没消化完，都要继续——**`carry != 0` 不能省**，否则 `5 + 5` 会丢掉最高位的 1。
- 每轮累加：`carry` + l1 当前值（若有）+ l2 当前值（若有）；取过的节点要推进指针，否则死循环。
- `carry = sum / 10`、`cur.Next = &ListNode{Val: sum % 10}`：商是进位、余数是当前位，位置顺序无关（sum 是局部变量）。
- `return dummy.Next`：跳过哨兵，返回真正的头节点。

##### 完整运行示例（逐轮表格）

`l1 = 2→4→3`（342），`l2 = 5→6→4`（465），期望 `7→0→8`（807）。

| 轮 | l1 当前 | l2 当前 | carry | sum | 当前位 `sum%10` | 新 carry `sum/10` |
|---|---|---|---|---|---|---|
| 1 | 2 | 5 | 0 | 7 | 7 | 0 |
| 2 | 4 | 6 | 0 | 10 | 0 | 1 |
| 3 | 3 | 4 | 1 | 8 | 8 | 0 |

结果 `7→0→8` ✅。注意第 3 轮 l1/l2 都没有值了，但 carry=1 还在，所以循环继续，这正是 `carry != 0` 存在的意义。

##### 复杂度

- **时间复杂度：\(O(n)\)**。`n = max(len(l1), len(l2))`，最多再多处理一次最后进位，仍是 \(O(n)\)。
- **空间复杂度：\(O(1)\)**。只用了 dummy/cur/carry 等常数变量（返回值不计入）。

#### 解法二：递归（灵茶山艾府）

##### 核心思路

把加法看成子问题：**每一层只算当前位的和，剩下部分交给递归**。当前位 = `(carry + l1.Val + l2.Val) % 10`，新进位 = `(carry + l1.Val + l2.Val) / 10`，递归参数换成 `l1.Next`、`l2.Next` 和新进位。

##### 写法一：创建新节点（不修改原链表）

```go
// l1 和 l2 为当前遍历的节点，carry 为进位
func addTwo(l1 *ListNode, l2 *ListNode, carry int) *ListNode {
    if l1 == nil && l2 == nil && carry == 0 { // 递归边界
        return nil
    }
    s := carry
    if l1 != nil {
        s += l1.Val
        l1 = l1.Next
    }
    if l2 != nil {
        s += l2.Val
        l2 = l2.Next
    }
    return &ListNode{s % 10, addTwo(l1, l2, s/10)}
}

func addTwoNumbers(l1 *ListNode, l2 *ListNode) *ListNode {
    return addTwo(l1, l2, 0)
}
```

逐行理解：

- 边界 `l1 == nil && l2 == nil && carry == 0`：所有位都处理完，返回 nil；
- `s := carry` 先带上进位，再累加两个节点值（空节点跳过）；
- `return &ListNode{s % 10, addTwo(l1, l2, s/10)}`：**当前节点指向子问题的结果**——和 21 递归合并链表、206 递归反转是同一个「递到边界、归时接线」的结构。

##### 写法二：原地修改（省空间、简化代码）

```go
func addTwo(l1, l2 *ListNode, carry int) *ListNode {
    if l1 == nil && l2 == nil { // 递归边界
        if carry != 0 {
            return &ListNode{Val: carry} // 如果进位了，就额外创建一个节点
        }
        return nil
    }
    if l1 == nil { // 如果 l1 是空的，那么此时 l2 一定不是空节点
        l1, l2 = l2, l1 // 交换 l1 与 l2，保证 l1 非空，从而简化代码
    }
    sum := carry + l1.Val
    if l2 != nil {
        sum += l2.Val
        l2 = l2.Next
    }
    l1.Val = sum % 10 // 直接修改原链表节点
    l1.Next = addTwo(l1.Next, l2, sum/10)
    return l1
}
```

两个简化技巧：

- **边界拆开**：`carry` 从边界条件里拿出来单独处理——l1/l2 都空时如果还有进位，单独补一个节点；
- **交换 l1/l2**：`if l1 == nil { l1, l2 = l2, l1 }` 保证 l1 非空，后面就不用再判 `l1 != nil`。

代价是**会修改原链表节点**（`l1.Val = ...`），如果面试要求不破坏输入，要主动说明这一点。

##### 完整运行示例（递归调用树）

`l1 = 2→4→3`，`l2 = 5→6→4`（以写法一为例）：

```text
addTwo(2, 5, 0)
  ├─ s=7  → 返回 7 → addTwo(4, 6, 0)
  │            ├─ s=10 → 返回 0 → addTwo(3, 4, 1)
  │            │            ├─ s=8 → 返回 8 → addTwo(nil, nil, 0)
  │            │            │            └─ 边界 → 返回 nil
  │            │            └─ 8 → nil
  │            └─ 0 → 8 → nil
  └─ 7 → 0 → 8 → nil
```

结果 `7→0→8` ✅。每一层「返回 xxx」都是该子问题的结果头节点。

##### 复杂度

- **时间复杂度：\(O(n)\)**。每层处理一个节点，`n = max(len(l1), len(l2))`。
- **空间复杂度：\(O(n)\)**。递归调用栈深度 O(n)。

#### 对比与复盘

| 对比项 | 迭代（尾插法） | 递归 |
|---|---|---|
| 时间复杂度 | \(O(n)\) | \(O(n)\) |
| 空间复杂度 | \(O(1)\) | \(O(n)\) 栈 |
| 构建方式 | 从头到尾逐个尾插 | 递到底，再从尾到头接线 |
| 是否修改原链表 | 否（创建新节点） | 写法二原地修改 |
| 优点 | 空间小、面试首选 | 代码短、子问题边界清晰 |
| 局限 | 需要维护 dummy/cur | 长链表可能栈溢出 |

#### 本地测试（表驱动）

用 `fromSlice` 把逆序数字切片建成链表，`toSlice` 转回切片比对：

```go
func TestAddTwoNumbers(t *testing.T) {
    tests := []struct {
        name string
        a, b []int // 逆序数字，最低位在前
        want []int
    }{
        {"simple", []int{2, 4, 3}, []int{5, 6, 4}, []int{7, 0, 8}},
        {"different-length", []int{9, 9, 9, 9, 9, 9, 9}, []int{9, 9, 9, 9}, []int{8, 9, 9, 9, 0, 0, 0, 1}},
        {"final-carry", []int{5}, []int{5}, []int{0, 1}},
        {"carry-chain", []int{9, 9, 9}, []int{1}, []int{0, 0, 0, 1}},
        {"zero", []int{1, 8}, []int{0}, []int{1, 8}},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := toSlice(addTwoNumbers(fromSlice(tt.a), fromSlice(tt.b)))
            if !slices.Equal(got, tt.want) {
                t.Errorf("got %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 循环条件漏掉 `carry != 0`：最高位的最终进位被丢掉（`5+5` 得到 `[0]` 而不是 `[0,1]`）。
2. 取过节点后忘记推进 `l1`/`l2`：同一节点反复累加，死循环。
3. 空节点直接取 `.Val`：必须先判 `l1 != nil` / `l2 != nil` 再累加。
4. 当前位和进位写反：当前位是 `sum % 10`，进位是 `sum / 10`。
5. 返回 `dummy` 而不是 `dummy.Next`：dummy 是哨兵，不是结果头。
6. 递归边界漏 `carry == 0`（写法一）：最后一位进位会触发无限递归；写法二把 carry 单独处理成新节点。
7. 原地修改版会破坏原链表：如果之后还要用 l1/l2，要提前说明或改用创建新节点的写法。

#### 建议测试案例

```text
[2,4,3] + [5,6,4]          → [7,0,8]       // 342 + 465 = 807，中间有进位
[9,9,9,9,9,9,9] + [9,9,9,9] → [8,9,9,9,0,0,0,1] // 长度不同 + 连续进位 + 最后新增位
[5] + [5]                  → [0,1]         // 最后新增一位进位
[9,9,9] + [1]              → [0,0,0,1]     // 全 9 连续进位
[1,8] + [0]                → [1,8]         // 一个数是 0
```

#### 可迁移的规律

- **dummy 哨兵 + 尾插**：链表「从空开始构建结果」的通用框架（21 合并、19 删除、2 加法都用它）。
- **模拟竖式加法**：最低位在链表头时正好免去反转，逐位相加 + 进位即可。
- **递归子问题化**：每层只处理一位，剩余交给子调用——和 21 递归合并、206 递归反转同构。
- **思考题**：如果数字从最高位开始存储（[445. 两数相加 II](https://leetcode.cn/problems/add-two-numbers-ii/)），需要先反转链表，或把两个链表补成等长再从低位对齐。

#### 来源说明

- [LeetCode 2. 两数相加题解列表](https://leetcode.cn/problems/add-two-numbers/solutions/)
- 灵茶山艾府《【动画】简洁写法！从递归到迭代！》（基础算法精讲 06：链表遍历与哨兵；基础算法精讲 09：递归理解）。

#### 重做记录

> 2026-08-22：完成迭代尾插 + 递归两种写法；重做时重点检查循环条件包含 `carry`、`sum%10` 当前位与 `sum/10` 进位、最后一位进位的节点。

### 5. 专题参考资料

- [Hello 算法：链表](https://www.hello-algo.com/chapter_array_and_linkedlist/linked_list/)
- [代码随想录：链表理论基础](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/链表理论基础.md)
- [代码随想录：0206.翻转链表](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0206.翻转链表.md)
- [LeetCode-Go：链表题解对照](https://github.com/halfrost/LeetCode-Go)

---

## 专题四：二叉树

### 1. 专题背景

二叉树是“分治”和“递归”思想的最佳载体：一棵树的问题，天然可以拆成“左子树问题 + 右子树问题”。本专题的底层内容来自 hello-algo 第七章《树》的[二叉树](https://www.hello-algo.com/chapter_tree/binary_tree/)、[二叉树遍历](https://www.hello-algo.com/chapter_tree/binary_tree_traversal/)、[二叉搜索树](https://www.hello-algo.com/chapter_tree/binary_search_tree/)三节，以及[代码随想录·二叉树的递归遍历](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/二叉树的递归遍历.md)。本专题的核心纪律只有一条：**写任何递归函数前，先说明“这个递归函数返回什么”**。

#### 1.1 二叉树定义与术语（hello-algo 7.1）

二叉树（binary tree）是一种非线性数据结构，代表“祖先”与“后代”之间的派生关系，体现“一分为二”的分治逻辑。基本单元是节点，每个节点包含值、左子节点引用和右子节点引用：

```go
type TreeNode struct {
    Val   int
    Left  *TreeNode
    Right *TreeNode
}
```

常用术语：

- **根节点**：位于顶层、没有父节点的节点；
- **叶节点**：没有子节点的节点，左右指针均为 `nil`；
- **边**：连接两个节点的指针；
- **层**：从顶到底递增，根节点在第 1 层；
- **度**：子节点数量，二叉树中为 0/1/2；
- **高度 / 深度**：经过的**边**的数量（有些题目按“节点数”定义，此时要 +1）；
- **左子树 / 右子树**：某节点左/右子节点及其以下所有节点。

#### 1.2 常见二叉树类型与退化（hello-algo 7.1.3 / 7.1.4）

| 类型 | 定义 | 特点 |
|---|---|---|
| 完美二叉树 | 所有层都填满 | 高度 h 时节点数 \(2^{h+1}-1\)，理想结构 |
| 完全二叉树 | 只允许最底层不填满，且从左到右连续 | 可用数组存储（堆的底层） |
| 完满二叉树 | 除叶节点外所有节点都有两个子节点 | 没有度为 1 的节点 |
| 平衡二叉树 | 任意节点左右子树高度差不超过 1 | 保证操作接近 \(O(\log n)\) |

当二叉树每层都填满时达到理想结构；当所有节点偏向一侧时退化为“链表”，操作复杂度退化到 \(O(n)\)——这正是 104 最大深度、543 直径等题要测试“偏斜树”的原因。

#### 1.3 遍历：DFS 与 BFS（hello-algo 7.2）

- **层序遍历 = BFS**：借助队列，从顶到底、每层从左到右访问。时间复杂度 \(O(n)\)，空间最差 \(O(n)\)（满二叉树时队列中最多约 \(n/2\) 个节点）。102 题的关键细节：**每层的节点数要在处理该层前先固定**，否则队列边出边进会串层。
- **前序 / 中序 / 后序遍历 = DFS**：通常用递归实现，分为“递”（访问下一个节点）和“归”（函数返回）两个阶段。三种遍历只是**访问根节点的时机**不同：根-左-右 / 左-根-右 / 左-右-根。
- **递归栈空间与树高的关系**：递归深度 = 树高。平衡树是 \(O(\log n)\)，退化成链表的树是 \(O(n)\)——94 题要能讲清这一点。
- **迭代遍历**：用显式栈模拟递归。中序迭代的难点是“先把左链一路压栈，弹栈时访问节点，再转向右子树”。

#### 1.4 二叉搜索树 BST（hello-algo 7.4）

BST 满足：左子树所有节点值 < 根 < 右子树所有节点值，且左右子树也是 BST。关键性质：

- **中序遍历序列升序**——98 验证 BST 的两种标准做法（中序前值、上下界）都源于此；
- 查找/插入/删除在平衡时 \(O(\log n)\)，退化后 \(O(n)\)；
- 验证时**只比较父子节点不够**：深层节点可能违背祖先的上下界，必须携带上界/下界，或记录中序前值。

#### 1.5 本专题套路与本地测试约定（Day 4 要求）

套路：

1. **先写递归契约**：写代码前说清“这个函数返回什么”（94 返回数组、104 返回高度、543 的辅助函数返回高度）；
2. **空树是天然边界**：递归函数几乎都要处理 `node == nil`；
3. **子树视角**：翻转、深度、直径都以“左子树 + 右子树”为子问题；
4. **对拍验证**：递归 vs 迭代、DFS vs BFS，用随机树对拍。

本地测试约定：

- 二叉树测试辅助：层序建树 `fromSlice`（用 `nil` 占位空子节点）、层序转切片 `toSlice`、按需的“树转中序数组”；
- 表驱动测试：空树、单点、左右偏斜、非满树、深层违规；
- 当天验收：从空白写 DFS 三遍历和 BFS；每题先说递归契约；随机树让递归/迭代参考实现对拍。

#### 1.6 五个通用算法骨架

树题可以剥掉题目外壳，套进下面 5 个骨架。每个骨架只需要填三样东西：**递归契约（函数返回什么）、空节点返回什么、访问/组合逻辑放在哪个位置**。

**骨架一：递归遍历 / 分治（DFS 万能骨架）**

```go
func dfs(node *TreeNode) 返回类型 {
    if node == nil { // 空节点边界，先想好返回什么
        return 空值
    }
    // 【前序位置】进入 node 时要做的事（访问根、判断状态）

    left := dfs(node.Left)   // 左子树子问题
    right := dfs(node.Right) // 右子树子问题

    // 【后序位置】左右都算完了，用 left/right/node.Val 组合答案
    return 组合结果
}
```

前序 = 结果在前序位置组装；中序 = 插在 left 和 right 之间；后序 = 放后序位置。访问时机就是模板唯一的开关。

**骨架二：迭代模拟递归（显式栈）**

```go
stack := []*TreeNode{}
cur := root
for cur != nil || len(stack) > 0 {
    for cur != nil { // 一路压左链
        // 【前序位置】压栈时访问
        stack = append(stack, cur)
        cur = cur.Left
    }
    cur = stack[len(stack)-1]
    stack = stack[:len(stack)-1]
    // 【中序位置】弹栈时访问
    cur = cur.Right // 转向右子树
}
```

想变后序就调整“访问时机”和压栈顺序，骨架不变。

**骨架三：BFS 层序（队列）**

```go
q := []*TreeNode{root}
for len(q) > 0 {
    size := len(q) // 固定本层长度
    for i := 0; i < size; i++ {
        node := q[0]
        q = q[1:]
        // 访问 node（需要分层就按 size 归组）
        if node.Left != nil {
            q = append(q, node.Left)
        }
        if node.Right != nil {
            q = append(q, node.Right)
        }
    }
}
```

**骨架四：返回子树信息 + 全局答案（后序分治）**

```go
var ans 答案类型

func dfs(node *TreeNode) 子树信息 {
    if node == nil {
        return 空信息
    }
    l := dfs(node.Left)
    r := dfs(node.Right)
    // 用 l、r 更新全局 ans（直径、最长路径、最大和……）
    return 由 l、r 组合出的本节点信息 // 返回给父节点用
}
```

**骨架五：带状态传递的自上而下**

```go
func dfs(node *TreeNode, 状态 状态类型) {
    if node == nil {
        return
    }
    // 前序位置：用当前状态判断/更新（路径、上下界、深度……）
    dfs(node.Left, 新状态(node.Val, 状态))
    dfs(node.Right, 新状态(node.Val, 状态))
}
```

对应到本专题：94 → 骨架一/二；102 → 骨架三；104 → 骨架一（返回高度）；226 → 骨架一（交换写在调用左右之前）；543 → 骨架四；98 → 骨架五（上下界状态）或骨架一（中序前值）。

#### 1.7 前序 / 中序 / 后序的应用场景

三种 DFS 遍历的差别只在“访问根的时机”，这个时机决定了它适合解决什么问题：

| 遍历 | 顺序 | 适用场景 | 本专题相关 |
|---|---|---|---|
| 前序 | 根-左-右 | “先处理自己，再处理子树”：从根向下的状态传递、复制/序列化树 | 226 翻转（先交换再递归） |
| 中序 | 左-根-右 | 需要“左子树信息 → 当前节点 → 右子树信息”的顺序：BST 升序性质 | 94 中序遍历、98 验证 BST |
| 后序 | 左-右-根 | “先算完子树，再汇总到根”：自底向上合并答案，依赖子树结果 | 104 深度、543 直径 |

选择口诀：

- **要“向下传”就用前序**：翻转树先交换再递归、带上下界验证 BST、统计路径和——信息从根流向叶子；
- **要“按大小/顺序”就用中序**：BST 的中序天然升序，所以“验证 BST”“第 k 小”“前驱后继”都是中序；
- **要“向上收”就用后序**：深度、直径、最大路径和、最近公共祖先——父节点要等两个子树都算完才能决定，所以先递归左右、在后序位置组合；
- **不确定时先写骨架一**：把“访问”放前序位置先跑通，再看是否需要后序汇总。

迭代版补充：骨架二默认是中序；前序迭代更简单（先访问根、先压右再压左）；后序迭代需要额外处理（或按“根-右-左”遍历后反转结果）。

### 2. 本专题题目看板

题目来自 Day 4 执行清单，难度标记沿用 A/B 分组。

| 状态 | 分组 | 题号 | 题目 | 核心训练点 | 笔记 |
|:---:|:---:|---:|---|---|---|
| ✅ | A | 94 | [二叉树的中序遍历](https://leetcode.cn/problems/binary-tree-inorder-traversal/) | 递归契约、迭代显式栈 | [查看](#题目-94二叉树的中序遍历) |
| ✅ | A | 102 | [二叉树的层序遍历](https://leetcode.cn/problems/binary-tree-level-order-traversal/) | BFS 队列、每层固定长度 | [查看](#题目-102二叉树的层序遍历) |
| ✅ | A | 104 | [二叉树的最大深度](https://leetcode.cn/problems/maximum-depth-of-binary-tree/) | 递归契约、DFS/BFS 对拍 | [查看](#题目-104二叉树的最大深度) |
| ✅ | A | 226 | [翻转二叉树](https://leetcode.cn/problems/invert-binary-tree/) | 前序/后序、中序陷阱 | [查看](#题目-226翻转二叉树) |
| ✅ | A | 543 | [二叉树的直径](https://leetcode.cn/problems/diameter-of-binary-tree/) | 返回高度、全局答案 | [查看](#题目-543二叉树的直径) |
| ✅ | A | 98 | [验证二叉搜索树](https://leetcode.cn/problems/validate-binary-search-tree/) | 中序升序、上下界 | [查看](#题目-98验证二叉搜索树) |

状态说明：

- ⬜ 未开始
- 🟡 已完成首次提交，尚未复盘
- ✅ 已完成题解与复盘
- 🔁 已独立重做

### 3. 每道题的记录模板

以后新增题目时复制下面这段：

```markdown
### 题目 X：题目名称

#### 题目摘要

- **题目链接**：
- **输入**：
- **输出**：
- **关键约束**：
- **核心模式**：
- **面试必须说清**：
- **本地测试标准**：

#### 我的第一反应

> 记录最初思路、踩过的坑（即使后来发现不对，也保留）。

#### 解法一：直觉 / 暴力解法

##### 我的思路
##### 代码
##### 复杂度
##### 主要关注点

#### 解法二：优化解法

##### 优化突破口
##### 代码
##### 逐行理解
##### 完整运行示例（逐轮表格）
##### 复杂度
##### 关键不变量

#### 对比与复盘

| 对比项 | 解法一 | 解法二 |
|---|---|---|
| 时间复杂度 |  |  |
| 空间复杂度 |  |  |
| 核心操作 |  |  |
| 优点 |  |  |
| 局限 |  |  |

#### 本地测试（表驱动）

#### 易错点

#### 建议测试案例

#### 可迁移的规律

#### 来源说明

#### 重做记录
```

---

### 题目 94：二叉树的中序遍历

#### 题目摘要

- **题目链接**：[LeetCode 94. 二叉树的中序遍历](https://leetcode.cn/problems/binary-tree-inorder-traversal/)
- **输入**：二叉树根节点 `root`。
- **输出**：中序遍历（左-根-右）的节点值数组。
- **关键约束**：节点数 `[0, 100]`。
- **核心模式**：DFS 递归；迭代用显式栈。
- **面试必须说清**：递归栈空间与树高关系？迭代栈何时压左、何时访问？
- **本地测试标准**：空、单点、左右偏斜；递归和迭代结果对拍。

#### 我的第一反应

> 第一反应就是递归三遍历模板（1.6 骨架一）：闭包 `dfs`，左-根-右，空节点直接返回。看完灵茶题解才知道中序还有两个进阶版本：迭代显式栈（Day 4 要求讲清“何时压左、何时访问”）和空间 O(1) 的 Morris 线索遍历。

#### 解法一：递归（我的写法）

##### 递归契约（面试必须说清）

`dfs(node)` 的作用是：**把以 node 为根的子树按中序遍历顺序追加到 ans**。空节点不产生任何值，直接返回。递归深度 = 树高 h：平衡树是 \(O(\log n)\)，退化成链表的树是 \(O(n)\)——这就是“递归栈空间与树高关系”的答案。

##### 代码（我的写法）

```go
func inorderTraversal(root *TreeNode) (ans []int) {
    var dfs func(root *TreeNode)
    dfs = func(node *TreeNode) {
        if node == nil {
            return
        }
        dfs(node.Left)              // 左
        ans = append(ans, node.Val) // 根：放中间才是中序
        dfs(node.Right)             // 右
    }
    dfs(root)
    return
}
```

灵茶山艾府的递归版与本代码完全一致（只在注释里标了“这行移到前面就是前序，移到后面就是后序”），说明这个写法就是标准答案。

##### 完整运行示例（逐轮表格）

树：

```text
    1
   / \
  2   3
 / \
4   5
```

中序遍历结果：`4, 2, 5, 1, 3`。

| 步 | 动作 | ans |
|---|---|---|
| 1 | dfs(1)：进入左子树 dfs(2) | [] |
| 2 | dfs(2)：进入左子树 dfs(4) | [] |
| 3 | dfs(4)：左空，访问 4，返回 | [4] |
| 4 | 回到 dfs(2)，访问 2 | [4, 2] |
| 5 | dfs(2)：进入右子树 dfs(5)，访问 5，返回 | [4, 2, 5] |
| 6 | 回到 dfs(1)，访问 1 | [4, 2, 5, 1] |
| 7 | dfs(1)：进入右子树 dfs(3)，访问 3 | [4, 2, 5, 1, 3] |

##### 复杂度

- **时间复杂度：\(O(n)\)**。`n` 为节点个数，每个节点访问一次。
- **空间复杂度：\(O(h)\)**。`h` 为树高，递归栈最多压一条根到叶路径。

#### 解法二：迭代（显式栈）

##### 思路（回答“迭代栈何时压左、何时访问”）

用显式栈模拟递归（1.6 骨架二）：**进入节点时先把整条左链一路压栈（此时不访问），弹栈时才访问节点（中序位置），然后转向右子树**。口诀：压左链不访问，弹栈才访问。

##### 代码

```go
func inorderTraversalIter(root *TreeNode) (ans []int) {
    stack := []*TreeNode{}
    cur := root
    for cur != nil || len(stack) > 0 {
        for cur != nil { // 一路压左链
            stack = append(stack, cur)
            cur = cur.Left
        }
        cur = stack[len(stack)-1]
        stack = stack[:len(stack)-1]
        ans = append(ans, cur.Val) // 弹栈才访问
        cur = cur.Right            // 转向右子树
    }
    return
}
```

##### 完整运行示例（逐轮表格）

同一棵树（`1` 左 `2`[左 4 右 5]，右 3）：

| 轮 | 压栈后（栈底→栈顶） | 弹栈访问 | cur（弹栈后转向） | ans |
|---|---|---|---|---|
| 0 | [1, 2, 4] | — | nil | [] |
| 1 | [1, 2] | 4 | nil | [4] |
| 2 | [1] | 2 | 5 | [4, 2] |
| 3 | [1, 5] | — | nil | [4, 2] |
| 4 | [1] | 5 | nil | [4, 2, 5] |
| 5 | [] | 1 | 3 | [4, 2, 5, 1] |
| 6 | [3] | — | nil | [4, 2, 5, 1] |
| 7 | [] | 3 | nil | [4, 2, 5, 1, 3] |

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(h)\)**。栈中最多同时存在一条根到叶路径的节点，最差（偏斜树）\(O(n)\)。

#### 解法三：Morris 遍历（灵茶山艾府，线索二叉树）

##### 核心思想

能不能做到 O(1) 空间？不能写递归，也不能用栈模拟递归——递归和栈都用了 O(h) 空间。Morris 的办法是：利用“中序前驱没有右子树”的特点，把前驱的 `Right` 临时指向当前节点（**线索**），用线索代替栈记住“回去的路”，遍历完再把线索拆掉、恢复原树。

找前驱：从 `root.Left` 开始一直往右走，直到走到尽头（`pre.Right == nil`）或遇到指向 root 的线索（`pre.Right == root`）。

两种情况：

- `pre.Right == nil`：左子树还没访问 → 建线索 `pre.Right = root`，`root` 进入左子树；
- `pre.Right == root`：左子树访问完毕 → 断线索，访问 `root`，`root` 进入右子树（没有右子树就沿线索回去）。

##### 代码（灵茶山艾府）

```go
func inorderTraversalMorris(root *TreeNode) (ans []int) {
    for root != nil {
        if root.Left != nil {
            // 找 root 的中序前驱 pre：从 root.Left 一直向右走到尽头，或走到指向 root 的线索
            pre := root.Left
            for pre.Right != nil && pre.Right != root {
                pre = pre.Right
            }

            if pre.Right == nil { // 左子树尚未访问
                pre.Right = root // 建立线索（相当于把 pre.Right 当作栈）
                root = root.Left // 访问左子树
                continue
            }

            pre.Right = nil // 左子树访问完毕，去掉线索，恢复原样
        }

        ans = append(ans, root.Val) // 左子树访问完毕，记录当前节点
        root = root.Right           // 有右子树就访问右子树，没有就顺着线索回去
    }
    return
}
```

##### 逐行理解

- `for root != nil`：遍历结束条件是 root 走到 nil（沿线索回去后最终会到 nil）。
- `if root.Left != nil`：只有存在左子树才需要找前驱、建线索；没有左子树就直接访问。
- 找 `pre` 的循环条件必须带 `pre.Right != root`：否则第二次遇到线索时会绕圈死循环。
- 建线索后 `continue`：不能漏，否则会跳过左子树直接访问当前节点。
- 第二次遇到同一节点时 `pre.Right == root`，说明左子树已经通过线索完整走完，断线索、访问、向右。
- `pre.Right = nil` 这行如果确定遍历后不再使用这棵二叉树，可以省略，但省略后原树会被线索污染。

##### 完整运行示例（逐轮表格）

同一棵树：

| 步 | root | pre（前驱） | 动作 | ans |
|---|---|---|---|---|
| 0 | 1 | 5 | 建线索 5→1，root=2 | [] |
| 1 | 2 | 4 | 建线索 4→2，root=4 | [] |
| 2 | 4 | — | 左空，访问 4，root 沿线索到 2 | [4] |
| 3 | 2 | 4 | pre.Right==root，断线索，访问 2，root=5 | [4, 2] |
| 4 | 5 | — | 左空，访问 5，root 沿线索到 1 | [4, 2, 5] |
| 5 | 1 | 5 | pre.Right==root，断线索，访问 1，root=3 | [4, 2, 5, 1] |
| 6 | 3 | — | 左空，访问 3，root=nil 结束 | [4, 2, 5, 1, 3] |

##### 复杂度

- **时间复杂度：\(O(n)\)**。虽然写了二重循环，但每条边至多访问三次（第一次找前驱、遍历、第二次找前驱），总循环次数 \(O(n)\)。
- **空间复杂度：\(O(1)\)**。只用了 `pre` 一个额外变量（返回值不计入）。

##### 关键不变量

- 线索只建立在“前驱的右指针为空”的节点上；
- 每条线索被建立一次、拆除一次，断线索后树恢复原样；
- 访问顺序始终满足“左-根-右”，与递归/迭代完全一致。

#### 对比与复盘

| 对比项 | 递归 | 迭代（显式栈） | Morris |
|---|---|---|---|
| 时间复杂度 | \(O(n)\) | \(O(n)\) | \(O(n)\) |
| 空间复杂度 | \(O(h)\) | \(O(h)\) | \(O(1)\) |
| 核心动作 | 函数调用栈 | 压左链、弹栈访问 | 线索代替栈 |
| 是否修改原树 | 否 | 否 | 临时加线索（会拆掉） |
| 实现难度 | 最简单 | 中等 | 较难，需理解前驱 |
| 面试定位 | 首选 | Day 4 必讲 | 进阶加分项 |

#### 本地测试（表驱动 + 三实现对拍）

先定义树测试辅助（层序建树，`nil` 占位空子节点）：

```go
func intPtr(v int) *int { return &v }

// 层序建树：nil 表示空子节点，如 [1, nil, 2, nil, 3] 表示 1→右2→右3
func treeFromSlice(vals []*int) *TreeNode {
    if len(vals) == 0 || vals[0] == nil {
        return nil
    }
    root := &TreeNode{Val: *vals[0]}
    q := []*TreeNode{root}
    for i := 1; i < len(vals) && len(q) > 0; {
        node := q[0]
        q = q[1:]
        if vals[i] != nil { // 左孩子
            node.Left = &TreeNode{Val: *vals[i]}
            q = append(q, node.Left)
        }
        i++
        if i < len(vals) && vals[i] != nil { // 右孩子
            node.Right = &TreeNode{Val: *vals[i]}
            q = append(q, node.Right)
        }
        i++
    }
    return root
}
```

表驱动测试：三种实现跑同一批用例，互相就是“对拍”：

```go
func TestInorderTraversal(t *testing.T) {
    tests := []struct {
        name string
        vals []*int
        want []int
    }{
        {"empty", nil, []int{}},
        {"single", []*int{intPtr(1)}, []int{1}},
        {"left-skew", []*int{intPtr(3), intPtr(2), nil, intPtr(1)}, []int{1, 2, 3}},
        {"right-skew", []*int{intPtr(1), nil, intPtr(2), nil, intPtr(3)}, []int{1, 2, 3}},
        {"normal", []*int{intPtr(1), intPtr(2), intPtr(3)}, []int{2, 1, 3}},
        {"complex", []*int{intPtr(1), intPtr(2), intPtr(3), intPtr(4), intPtr(5)}, []int{4, 2, 5, 1, 3}},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := inorderTraversal(treeFromSlice(tt.vals)); !slices.Equal(got, tt.want) {
                t.Errorf("递归 got %v, want %v", got, tt.want)
            }
            if got := inorderTraversalIter(treeFromSlice(tt.vals)); !slices.Equal(got, tt.want) {
                t.Errorf("迭代 got %v, want %v", got, tt.want)
            }
            if got := inorderTraversalMorris(treeFromSlice(tt.vals)); !slices.Equal(got, tt.want) {
                t.Errorf("Morris got %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 递归忘写空节点边界：`node == nil` 时直接访问 `node.Val` 会 panic。
2. 访问根的位置放错：放左右递归之前是前序，放中间才是中序，放后面是后序。
3. 迭代版在压左链时访问：那是前序；中序必须在弹栈时访问。
4. 迭代版弹栈后忘了 `cur = cur.Right`：会反复弹同一个节点，死循环。
5. Morris 找前驱时循环条件漏 `pre.Right != root`：第二次碰到线索时绕圈，死循环。
6. Morris 建线索后漏 `continue`：会跳过左子树，访问顺序变成前序。
7. Morris 断线索只判断 `pre.Right == root`：左子树没走完之前不能断。
8. 空间复杂度记混：递归/迭代都是 \(O(h)\)，只有 Morris 是 \(O(1)\)。

#### 建议测试案例

```text
[]                → []
[1]               → [1]
[3,2,nil,1]       → [1,2,3]       // 左偏斜
[1,nil,2,nil,3]   → [1,2,3]       // 右偏斜
[1,2,3]           → [2,1,3]       // 普通树
[1,2,3,4,5]       → [4,2,5,1,3]   // 对应逐轮示例的树
```

#### 可迁移的规律

- **递归三遍历骨架（1.6 骨架一）**：访问根的位置决定前/中/后序，一个模板三处开关。
- **迭代显式栈（骨架二）**：模拟递归的通用方法，中序 = 压左链 → 弹栈访问 → 转右。
- **Morris 线索化**：O(1) 空间遍历的进阶技巧，可以推广到前序/后序 Morris；面试加分项，能画出“建线索/断线索”即可。
- **BST 中序升序**：94 是 98 验证 BST 的前置知识。

#### 来源说明

- [LeetCode 94. 二叉树的中序遍历题解列表](https://leetcode.cn/problems/binary-tree-inorder-traversal/solutions/)
- 灵茶山艾府《【图解】Morris 遍历（线索二叉树），一图秒懂！》（递归版 + Morris 版）。
- [代码随想录：二叉树的迭代遍历](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/二叉树的迭代遍历.md)

#### 重做记录

> 2026-08-22：完成递归 + 迭代栈 + Morris 三解法；重做时重点检查：递归栈空间与树高的关系、迭代“压左链不访问、弹栈才访问”、Morris 建/拆线索与 `pre.Right != root` 防死循环。

---

### 题目 102：二叉树的层序遍历

#### 题目摘要

- **题目链接**：[LeetCode 102. 二叉树的层序遍历](https://leetcode.cn/problems/binary-tree-level-order-traversal/)
- **输入**：二叉树根节点 `root`。
- **输出**：按层分组的节点值二维数组。
- **关键约束**：节点数 `[0, 2000]`。
- **核心模式**：BFS + 队列。
- **面试必须说清**：每层长度为何要在循环前固定？
- **本地测试标准**：空、单点、非满树；二维切片比较。

#### 我的第一反应

> 第一反应是 BFS 分层：把当前层节点收集到一个切片，逐层推进。第一次写踩了三个坑：切片创建语法写错、用 `cur != nil` 当循环条件导致死循环、把左右孩子判断写成 `else if` 漏掉右孩子。改成 `len(cur) > 0` 和两个独立 `if` 后通过；后来又按灵茶的「一个队列 + 固定 size」重写了一遍，两种写法等价。

#### 解法一：两个数组（cur/nxt 分层，我的写法）

##### 思路

用 `cur` 存当前层节点，`nxt` 收集下一层节点；处理完 `cur` 后整体替换成 `nxt`。因为 `cur` 本身就是某一层的完整集合，所以不需要“固定 size”的技巧，天然不会串层。

##### 代码（我的写法，已修正）

```go
func levelOrderCurNxt(root *TreeNode) (ans [][]int) {
    cur := []*TreeNode{}
    if root == nil {
        return
    }
    cur = append(cur, root)
    for len(cur) > 0 {
        vals := make([]int, 0)
        nxt := []*TreeNode{}
        for _, v := range cur {
            vals = append(vals, v.Val)
            if v.Left != nil {
                nxt = append(nxt, v.Left)
            }
            if v.Right != nil {
                nxt = append(nxt, v.Right)
            }
        }
        cur = nxt
        ans = append(ans, vals)
    }
    return
}
```

##### 我踩过的三个坑（错误分析）

| 错误写法 | 为什么错 | 正确写法 |
|---|---|---|
| `cur := make(*TreeNode{}, 0)` | `make` 第一个参数必须是**类型**（如 `[]*TreeNode`）；`*TreeNode{}` 是复合字面量表达式，不是类型 | `cur := make([]*TreeNode, 0)` 或 `cur := []*TreeNode{}` |
| `for cur != nil { ... }` | 切片判空不能看 `!= nil`：`nxt := []*TreeNode{}` 是非 nil 的**空切片**，`cur = nxt` 后 `cur != nil` 永远成立，死循环 | `for len(cur) > 0 { ... }` |
| `if v.Left != nil { ... } else if v.Right != nil { ... }` | `else if` 把两个**独立**条件耦合了：Left 非空时整个 `else` 分支被跳过，右孩子永远不会入队 | 两个独立的 `if`，左右互不影响 |

##### 完整运行示例（逐轮表格）

树：`3` 左 `9` 右 `20`（左 `15` 右 `7`），即 LeetCode 示例 `[3,9,20,nil,nil,15,7]`。

| 轮 | cur | vals | nxt | ans |
|---|---|---|---|---|
| 0 | [3] | [3] | [9, 20] | [[3]] |
| 1 | [9, 20] | [9, 20] | [15, 7] | [[3], [9, 20]] |
| 2 | [15, 7] | [15, 7] | [] | [[3], [9, 20], [15, 7]] |

`len(cur) > 0` 不成立时循环结束，输出三层。

##### 复杂度

- **时间复杂度：\(O(n)\)**。每个节点恰好被处理一次。
- **空间复杂度：\(O(n)\)**。满二叉树最后一层约 \(n/2\) 个节点，两个切片最坏各存 \(O(n)\)。

#### 解法二：一个队列（固定 size，我的写法）

##### 思路（回答“每层长度为何要在循环前固定”）

单队列边出边进：处理当前层时，下一层的孩子会被 append 进同一个队列。**如果不先固定 size，新入队的下一层节点会被当成当前层一起处理，串层**。所以在每层循环开始前先记下 `size := len(que)`，内层循环只处理这 size 个节点，刚入队的下一层节点留到下一轮。

##### 代码（我的写法）

```go
func levelOrderQueue(root *TreeNode) (ans [][]int) {
    que := []*TreeNode{}
    if root == nil {
        return
    }
    que = append(que, root)
    for len(que) > 0 {
        vals := make([]int, 0)
        size := len(que) // 固定本层长度，防止串层
        for i := 0; i < size; i++ {
            v := que[0]
            que = que[1:]
            vals = append(vals, v.Val)
            if v.Left != nil {
                que = append(que, v.Left)
            }
            if v.Right != nil {
                que = append(que, v.Right)
            }
        }
        ans = append(ans, vals)
    }
    return
}
```

灵茶山艾府的队列版与本代码逻辑一致，只有一处优化：`vals := make([]int, n)` 预分配空间，再用下标 `vals[i] = node.Val` 赋值，省去反复扩容。

##### 完整运行示例（逐轮表格）

同一棵树：

| 轮 | 处理前 que | size | 本层 vals | 处理后 que |
|---|---|---|---|---|
| 0 | [3] | 1 | [3] | [9, 20] |
| 1 | [9, 20] | 2 | [9, 20] | [15, 7] |
| 2 | [15, 7] | 2 | [15, 7] | [] |

##### 复杂度

- **时间复杂度：\(O(n)\)**。每个节点入队出队各一次。
- **空间复杂度：\(O(n)\)**。队列中最多同时存在约 \(n/2\) 个节点（满二叉树底层）。

##### 关键不变量

`size` 固定后，本层循环结束时队列里恰好全是**下一层**的节点；`size` 就是“本层还剩多少节点没处理”。

#### Go 队列语法补充（用切片当队列）

- **创建**：`var q []*TreeNode`（nil 切片）、`q := []*TreeNode{}`（空切片）、`q := make([]*TreeNode, 0)`、带容量 `make([]*TreeNode, 0, n)`。最常用的是直接初始化：`q := []*TreeNode{root}`。
- **入队**：`q = append(q, node)`，追加到末尾。
- **出队**：`node := q[0]; q = q[1:]`——切片头指针后移，是 O(1) 操作；代价是底层数组仍被引用，LeetCode 场景可忽略。
- **判空**：永远用 `len(q) > 0`，不要用 `q != nil`（nil 切片和空切片都能 append，空切片 `!= nil`，会误判非空）。
- **预分配**：知道容量时用 `make([]int, 0, n)`（配合 append）或 `make([]int, n)`（配合下标赋值）；注意 `make([]int, n)` 后不能再 append，否则前 n 位全是 0。
- **严格队列**：需要真正可释放内存/双向操作的队列时可用 `container/list`，或维护 `head` 下标；刷题用切片即可。

#### 对比与复盘

| 对比项 | 两个数组（cur/nxt） | 一个队列（固定 size） |
|---|---|---|
| 时间复杂度 | \(O(n)\) | \(O(n)\) |
| 空间复杂度 | \(O(n)\) | \(O(n)\) |
| 分层方式 | cur/nxt 整体替换 | size 固定后逐层消化 |
| 核心技巧 | 两切片轮换 | 每层前先记 `len(q)` |
| 优点 | 语义直观，天然不串层 | 只维护一个队列，写法统一 |
| 局限 | 每层新建两个切片 | 需要理解“固定 size”的原因 |

#### 本地测试（表驱动 + 两实现对拍）

复用 94 的 `treeFromSlice`（层序建树、nil 占位）；二维切片比较用 `reflect.DeepEqual`：

```go
func TestLevelOrder(t *testing.T) {
    tests := []struct {
        name string
        vals []*int
        want [][]int
    }{
        {"empty", nil, [][]int{}},
        {"single", []*int{intPtr(1)}, [][]int{{1}}},
        {"leetcode-example", []*int{intPtr(3), intPtr(9), intPtr(20), nil, nil, intPtr(15), intPtr(7)}, [][]int{{3}, {9, 20}, {15, 7}}},
        {"non-full", []*int{intPtr(1), intPtr(2), intPtr(3), intPtr(4)}, [][]int{{1}, {2, 3}, {4}}},
        {"right-skew", []*int{intPtr(1), nil, intPtr(2), nil, intPtr(3)}, [][]int{{1}, {2}, {3}}},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := levelOrderCurNxt(treeFromSlice(tt.vals)); !reflect.DeepEqual(got, tt.want) {
                t.Errorf("两数组 got %v, want %v", got, tt.want)
            }
            if got := levelOrderQueue(treeFromSlice(tt.vals)); !reflect.DeepEqual(got, tt.want) {
                t.Errorf("单队列 got %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 切片判空用 `len(q) > 0`，不要用 `q != nil`：空切片不是 nil，会死循环。
2. `make` 语法：`make([]*TreeNode, 0)`，不是 `make(*TreeNode{}, 0)`。
3. 左右孩子是两个独立条件，不能 `else if`：Left 非空会跳过 Right。
4. 单队列不固定 size：下一层节点混进当前层，输出错层。
5. 出队只读 `q[0]` 不更新 `q = q[1:]`：同一个节点反复处理。
6. `make([]int, n)` 后直接 append：得到 n 个 0 再加真实值；要么按下标赋值，要么用 `make([]int, 0, n)`。

#### 建议测试案例

```text
[]                       → []
[1]                      → [[1]]
[3,9,20,nil,nil,15,7]    → [[3],[9,20],[15,7]]   // LeetCode 示例
[1,2,3,4]                → [[1],[2,3],[4]]       // 非满树
[1,nil,2,nil,3]          → [[1],[2],[3]]         // 右偏斜
```

#### 可迁移的规律

- **BFS 模板（1.6 骨架三）**：队列 + 固定 size，是层序遍历的标准骨架。
- **“按层处理”的题**：199 二叉树的右视图、637 层平均值、116 填充每个节点的下一个右侧节点指针，都是这个模板换“访问动作”。
- **两数组 vs 单队列**：等价写法；面试写单队列更简洁，两数组用来讲“为什么需要固定 size”更直观。

#### 来源说明

- [LeetCode 102. 二叉树的层序遍历题解列表](https://leetcode.cn/problems/binary-tree-level-order-traversal/solutions/)
- 灵茶山艾府《BFS 为什么要用队列？一个视频讲透！》（基础算法精讲 13）。

#### 重做记录

> 2026-08-22：完成两数组 + 单队列两解法；重做时重点检查：切片判空用 `len`、左右孩子两个独立 `if`、单队列固定 size 后再遍历。

---

### 题目 104：二叉树的最大深度

#### 题目摘要

- **题目链接**：[LeetCode 104. 二叉树的最大深度](https://leetcode.cn/problems/maximum-depth-of-binary-tree/)
- **输入**：二叉树根节点 `root`。
- **输出**：最大深度（根到最远叶节点的节点数）。
- **关键约束**：节点数 `[0, 10^4]`。
- **核心模式**：DFS 递归 / BFS。
- **面试必须说清**：`maxDepth(node)` 返回值精确定义？空树返回什么？
- **本地测试标准**：空、单点、偏斜；DFS 与 BFS 对拍。

#### 我的第一反应

> 第一反应是**自底向上**递归：空树返回 0，否则 `1 + max(左子树深度, 右子树深度)`——这就是 1.6 骨架一的标准用法，写起来几乎是背模板。看完灵茶题解才知道还有**自顶向下**的写法（带 depth 参数，前序位置更新答案），以及 Day 4 要求的 BFS 对拍（层数即深度）。

#### 解法一：自底向上（我的写法）

##### 递归契约（面试必须说清）

`maxDepth(node)` 的返回值精确定义：**以 node 为根的子树的最大深度（从根到最远叶节点的节点数）**。空树没有任何节点，返回 0；单点树返回 `0 + 1 = 1`。子树的深度算出来后，当前节点还要把自己这一层加进去，所以 `return max(l, r) + 1`。

##### 代码（我的写法）

```go
func maxDepthBU(root *TreeNode) int {
    if root == nil {
        return 0
    }
    lDepth := maxDepthBU(root.Left)
    rDepth := maxDepthBU(root.Right)
    return max(lDepth, rDepth) + 1
}
```

灵茶山艾府的自底向上写法与本代码完全一致。

##### 逐行理解

- 空树返回 0：递归的“地基”，保证叶节点的深度正确（0+1=1）；
- 先递归左、右子树：**后序位置**拿到两个子树的深度；
- `max(lDepth, rDepth) + 1`：左右取更深的那边，再算上当前节点自己这一层。

##### 完整运行示例（逐轮表格）

树：`3` 左 `9` 右 `20`（左 `15` 右 `7`）。自底向上先算叶子，再逐层向上汇总：

| 节点 | 左子树深度 | 右子树深度 | 返回 |
|---|---|---|---|
| 9 | 0 | 0 | 1 |
| 15 | 0 | 0 | 1 |
| 7 | 0 | 0 | 1 |
| 20 | 1（来自 15） | 1（来自 7） | 2 |
| 3 | 1（来自 9） | 2（来自 20） | 3 |

答案 3。

##### 复杂度

- **时间复杂度：\(O(n)\)**。每个节点访问一次。
- **空间复杂度：\(O(n)\)**。最坏（偏斜成链）递归栈深度为 n；平衡树是 \(O(\log n)\)。

#### 解法二：自顶向下（灵茶山艾府）

##### 思路

和自底向上相反，**深度信息从根往下传**：`dfs(node, depth)` 把“当前节点的深度”作为参数带下去，每进一层 `depth++`，在前序位置用 `ans = max(ans, depth)` 更新全局答案。它不依赖子树的返回值，只需要当前路径上的状态。

##### 代码（灵茶山艾府）

```go
func maxDepthTD(root *TreeNode) (ans int) {
    var dfs func(*TreeNode, int)
    dfs = func(node *TreeNode, depth int) {
        if node == nil {
            return
        }
        depth++
        ans = max(ans, depth)
        dfs(node.Left, depth)
        dfs(node.Right, depth)
    }
    dfs(root, 0)
    return
}
```

##### 逐行理解

- `dfs(root, 0)`：根节点还没计数，深度从 0 开始；
- 进入非空节点先 `depth++`：把“从根到当前节点”的深度算出来；
- `ans = max(ans, depth)`：前序位置更新全局最大深度；
- 左右子树带着**同一份 depth**（值传递，互不影响）继续下传。

##### 完整运行示例（逐轮表格）

同一棵树：

| 访问节点 | 进入时 depth | ans |
|---|---|---|
| 3 | 1 | 1 |
| 9 | 2 | 2 |
| 20 | 2 | 2 |
| 15 | 3 | 3 |
| 7 | 3 | 3 |

答案 3。

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(n)\)**。最坏递归栈 O(n)。

#### 解法三：BFS（层数即深度，对拍用）

##### 思路

层序遍历每处理完一层，深度 +1——**层数就是深度**。借用 102 的队列模板（1.6 骨架三），不需要递归。

##### 代码

```go
func maxDepthBFS(root *TreeNode) int {
    if root == nil {
        return 0
    }
    q := []*TreeNode{root}
    depth := 0
    for len(q) > 0 {
        size := len(q)
        for i := 0; i < size; i++ {
            node := q[0]
            q = q[1:]
            if node.Left != nil {
                q = append(q, node.Left)
            }
            if node.Right != nil {
                q = append(q, node.Right)
            }
        }
        depth++ // 一层处理完，深度加一
    }
    return depth
}
```

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(n)\)**。队列最坏存满二叉树底层约 n/2 个节点。

#### 对比与复盘

| 对比项 | 自底向上 | 自顶向下 | BFS |
|---|---|---|---|
| 信息流向 | 子树结果向上汇总 | 深度参数向下传 | 层数计数 |
| 核心位置 | 后序（return 处） | 前序（进节点时） | 每层结束 |
| 时间/空间 | \(O(n)\) / \(O(n)\) | \(O(n)\) / \(O(n)\) | \(O(n)\) / \(O(n)\) |
| 是否用递归 | 是 | 是 | 否（迭代队列） |
| 优点 | 代码最短、直觉 | 可顺便统计“每层状态” | 无爆栈风险、可对拍 |

#### 本地测试（表驱动 + DFS/BFS 对拍）

复用 `treeFromSlice` / `intPtr`，三种实现跑同一批用例：

```go
func TestMaxDepth(t *testing.T) {
    tests := []struct {
        name string
        vals []*int
        want int
    }{
        {"empty", nil, 0},
        {"single", []*int{intPtr(1)}, 1},
        {"left-skew", []*int{intPtr(3), intPtr(2), nil, intPtr(1)}, 3},
        {"right-skew", []*int{intPtr(1), nil, intPtr(2), nil, intPtr(3)}, 3},
        {"leetcode-example", []*int{intPtr(3), intPtr(9), intPtr(20), nil, nil, intPtr(15), intPtr(7)}, 3},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := maxDepthBU(treeFromSlice(tt.vals)); got != tt.want {
                t.Errorf("自底向上 got %d, want %d", got, tt.want)
            }
            if got := maxDepthTD(treeFromSlice(tt.vals)); got != tt.want {
                t.Errorf("自顶向下 got %d, want %d", got, tt.want)
            }
            if got := maxDepthBFS(treeFromSlice(tt.vals)); got != tt.want {
                t.Errorf("BFS got %d, want %d", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 空树返回 0 而不是 1：单点树深度是 1，由 0+1 得到；返回 1 会把空树也算成 1。
2. 忘记 `+1`：只取左右较大值会漏掉当前节点自己这一层。
3. 自顶向下先更新 `ans` 再 `depth++`：根节点的深度会被记成 0。
4. 自顶向下左右递归必须传**同一份 depth**（值传递），不能在左子树里改了再传给右子树。
5. BFS 的 `depth++` 位置：每层结束加一次，不是每个节点加一次。
6. 偏斜树递归栈 O(n)：超深树可能栈溢出，面试可以主动提 BFS 迭代方案。

#### 建议测试案例

```text
[]                      → 0
[1]                     → 1
[3,9,20,nil,nil,15,7]   → 3   // 普通树
[3,2,nil,1]             → 3   // 左偏斜
[1,nil,2,nil,3]         → 3   // 右偏斜
```

#### 可迁移的规律

- **自底向上（后序汇总）**：需要“子树结果”的题——543 直径、110 平衡二叉树、236 最近公共祖先。
- **自顶向下（前序 + 参数）**：只需要“当前路径状态”的题——98 上下界、112 路径总和、二叉树所有路径。
- **选择口诀**：要子树信息就自底向上；只传状态就自顶向下；都不想要递归就 BFS。
- **BFS 层数即深度**：111 二叉树的最小深度（BFS 找到第一个叶子即可）。

#### 来源说明

- [LeetCode 104. 二叉树的最大深度题解列表](https://leetcode.cn/problems/maximum-depth-of-binary-tree/solutions/)
- 灵茶山艾府《【视频讲解】让你对递归的理解更上一层楼！》（基础算法精讲 09）。

#### 重做记录

> 2026-08-22：完成自底向上 + 自顶向下 + BFS；重做时重点检查：递归契约（空树返回 0）、自顶向下 `depth++` 的位置、DFS/BFS 三种实现对拍。

---

### 题目 226：翻转二叉树

#### 题目摘要

- **题目链接**：[LeetCode 226. 翻转二叉树](https://leetcode.cn/problems/invert-binary-tree/)
- **输入**：二叉树根节点 `root`。
- **输出**：翻转后的根节点（每个节点的左右子树互换）。
- **关键约束**：节点数 `[0, 100]`。
- **核心模式**：递归前序/后序。
- **面试必须说清**：为什么前序/后序可，中序直接照搬会交换两次？
- **本地测试标准**：空、单点、不对称树；翻转两次恢复原树。

#### 我的第一反应

> 第一反应就是“整棵树左右对称翻转”：对每个节点交换左右子树，再递归处理子树。我写的是**后序**（先递归左右、再交换），和灵茶山艾府的写法一完全一致；灵茶还给了**前序**写法（先交换、再递归）。写完后追问了一句：中序为什么不能直接照搬？——因为交换后递归的“右子树”其实是被翻过一次的左子树，会翻两次。

#### 解法一：后序（先递归再交换，我的写法）

##### 递归契约

`invertTree(node)` 返回：**以 node 为根的子树的根，且该子树已完成左右翻转**。空节点返回 nil。子问题与原问题同构——“翻转左子树、翻转右子树、交换”，正是递归的两个特征。

##### 代码（我的写法）

```go
func invertTree(root *TreeNode) *TreeNode {
    if root == nil {
        return nil
    }
    left := invertTree(root.Left)  // 翻转左子树
    right := invertTree(root.Right) // 翻转右子树
    root.Left = right              // 交换左右儿子
    root.Right = left
    return root
}
```

灵茶山艾府的写法一与本代码完全一致。

##### 逐行理解

- 空节点返回 nil：递归边界，也是叶节点的自然结果；
- `left := invertTree(root.Left)`：先拿到左子树翻转后的根；
- `right := invertTree(root.Right)`：同理拿到右子树翻转后的根；
- 交换：`root.Left = right`、`root.Right = left`——左右儿子互换；
- `return root`：当前节点作为翻转后子树的根返回给父节点。

##### 完整运行示例（逐轮表格）

树：`[4,2,7,1,3,6,9]`（LeetCode 示例）。自底向上逐层翻转：

| 节点 | 递归左结果 | 递归右结果 | 交换后 Left / Right |
|---|---|---|---|
| 1 | nil | nil | L=nil, R=nil |
| 3 | nil | nil | L=nil, R=nil |
| 2 | 1 | 3 | L=3, R=1 |
| 6 | nil | nil | L=nil, R=nil |
| 9 | nil | nil | L=nil, R=nil |
| 7 | 6 | 9 | L=9, R=6 |
| 4 | 2（已翻转） | 7（已翻转） | L=7, R=2 |

结果层序：`[4,7,2,9,6,3,1]` ✅。

##### 复杂度

- **时间复杂度：\(O(n)\)**。每个节点访问一次。
- **空间复杂度：\(O(n)\)**。最坏偏斜成链，递归栈 O(n)。

#### 解法二：前序（先交换再递归，灵茶山艾府）

##### 思路

把“交换左右儿子”提前到递归之前：交换完再递归处理左、右子树。两种写法的结果完全一样，只是“交换”和“递归”的先后顺序不同。

##### 代码（灵茶山艾府）

```go
func invertTree(root *TreeNode) *TreeNode {
    if root == nil {
        return nil
    }
    root.Left, root.Right = root.Right, root.Left // 交换左右儿子
    invertTree(root.Left)                         // 翻转左子树
    invertTree(root.Right)                        // 翻转右子树
    return root
}
```

##### 完整运行示例（逐轮表格）

同一棵树：

| 节点 | 交换后 Left / Right | 递归左 | 递归右 |
|---|---|---|---|
| 4 | L=7, R=2 | invertTree(7) | invertTree(2) |
| 7 | L=9, R=6 | invertTree(9) | invertTree(6) |
| 2 | L=3, R=1 | invertTree(3) | invertTree(1) |

结果与解法一相同：`[4,7,2,9,6,3,1]`。

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(n)\)**。

#### 为什么前序/后序可以，中序直接照搬会交换两次（面试必须说清）

中序的顺序是“左-根-右”，如果照搬成“递归左 → 交换 → 递归右”：

1. 先递归左子树，左子树被翻好；
2. 交换左右儿子——此时 `root.Right` 指向的是**已经被翻过的原左子树**；
3. 再递归右子树——等于把原左子树**再翻一次**（翻回原样），而**原右子树从头到尾没被处理过**。

结果：原左子树被翻两次（白翻），原右子树没翻，整棵树是错的。

如果一定要用中序，第二次递归要改为处理**新的左子树**（也就是原右子树）：

```go
invertTree(root.Left)                            // 翻转左子树
root.Left, root.Right = root.Right, root.Left    // 交换
invertTree(root.Left)                            // 现在的左子树 = 原右子树，翻转它
```

口诀：**前序/后序随便选，中序要“处理两次左”**；面试直接说“中序照搬会交换两次，所以用前序或后序”即可。

#### 对比与复盘

| 对比项 | 后序（先递归再交换） | 前序（先交换再递归） |
|---|---|---|
| 访问根的位置 | 后序（return 前） | 前序（进入即交换） |
| 核心动作 | 拿左右结果再交换 | 交换完再递归 |
| 时间/空间 | \(O(n)\) / \(O(n)\) | \(O(n)\) / \(O(n)\) |
| 可读性 | 先想子问题，逻辑清晰 | 代码更短（一行交换） |
| 中序陷阱 | 无 | 无 |

#### 本地测试（表驱动 + 翻转两次恢复原树）

需要一个新的辅助：层序转切片（nil 占位、去掉末尾连续 nil）：

```go
// 层序转切片：nil 占位空子节点，末尾连续 nil 省略
func treeToSlice(root *TreeNode) []*int {
    if root == nil {
        return nil
    }
    res := []*int{}
    q := []*TreeNode{root}
    for len(q) > 0 {
        node := q[0]
        q = q[1:]
        if node == nil {
            res = append(res, nil)
            continue
        }
        v := node.Val
        res = append(res, &v)
        q = append(q, node.Left, node.Right)
    }
    for len(res) > 0 && res[len(res)-1] == nil {
        res = res[:len(res)-1]
    }
    return res
}
```

表驱动 + “翻转两次恢复原树”：

```go
func TestInvertTree(t *testing.T) {
    tests := []struct {
        name string
        vals []*int
        want []*int
    }{
        {"empty", nil, nil},
        {"single", []*int{intPtr(1)}, []*int{intPtr(1)}},
        {"asymmetric", []*int{intPtr(4), intPtr(2), intPtr(7), intPtr(1), intPtr(3), intPtr(6), intPtr(9)}, []*int{intPtr(4), intPtr(7), intPtr(2), intPtr(9), intPtr(6), intPtr(3), intPtr(1)}},
        {"left-skew", []*int{intPtr(1), intPtr(2), nil, intPtr(3)}, []*int{intPtr(1), nil, intPtr(2), nil, intPtr(3)}},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := treeToSlice(invertTree(treeFromSlice(tt.vals)))
            if !reflect.DeepEqual(got, tt.want) {
                t.Errorf("got %v, want %v", got, tt.want)
            }
        })
    }
}

func TestDoubleInvert(t *testing.T) {
    vals := []*int{intPtr(4), intPtr(2), intPtr(7), intPtr(1), intPtr(3), intPtr(6), intPtr(9)}
    root := treeFromSlice(vals)
    if got := treeToSlice(invertTree(invertTree(root))); !reflect.DeepEqual(got, vals) {
        t.Errorf("翻转两次应恢复原树, got %v, want %v", got, vals)
    }
}
```

#### 易错点

1. 递归边界漏 `root == nil`：空树 / 叶节点的 nil 子节点会 nil 解引用。
2. 忘记 `return root`：父节点拿不到翻转后的子树。
3. 中序照搬“递归左 → 交换 → 递归右”：原左子树被翻两次、原右子树没翻（面试必考）。
4. 用值比较验证翻转结果：应该比较整棵树的结构（层序），而不是只看根的值。
5. 前序写法交换后仍递归左右：交换的是左右儿子，递归目标是**交换后的**左右子树，不要写错变量。

#### 建议测试案例

```text
[]                                    → []
[1]                                   → [1]
[4,2,7,1,3,6,9]                       → [4,7,2,9,6,3,1]   // 不对称树
[1,2,nil,3]                           → [1,nil,2,nil,3]   // 左偏斜变右偏斜
任意树翻转两次                         → 恢复原树
```

#### 可迁移的规律

- **“交换 + 递归”的两种时机**：先交换（前序）或后交换（后序）都正确，中序要“处理两次左”；
- **递归返回新根**：`return root` 让父节点能接上子问题的结果（206 反转链表、21 合并链表同款模式）；
- **变形题**：[101. 对称二叉树](https://leetcode.cn/problems/symmetric-tree/)（翻转后与另一棵比）、[951. 翻转等价二叉树](https://leetcode.cn/problems/flip-equivalent-binary-trees/)。

#### 来源说明

- [LeetCode 226. 翻转二叉树题解列表](https://leetcode.cn/problems/invert-binary-tree/solutions/)
- 灵茶山艾府《两种递归写法》（基础算法精讲 09：深入理解递归）。

#### 重做记录

> 2026-08-22：完成后序 + 前序两种递归；重做时重点检查：递归契约（返回翻转后的根）、中序照搬为何交换两次、翻转两次恢复原树的验证。

---

### 题目 543：二叉树的直径

#### 题目摘要

- **题目链接**：[LeetCode 543. 二叉树的直径](https://leetcode.cn/problems/diameter-of-binary-tree/)
- **输入**：二叉树根节点 `root`。
- **输出**：任意两节点之间路径上的最大边数。
- **关键约束**：节点数 `[0, 10^4]`。
- **核心模式**：递归返回高度 + 全局答案。
- **面试必须说清**：递归返回高度，为什么不能直接返回直径？边数与节点数如何换算？
- **本地测试标准**：空、单点、最长路不过根；与小树穷举路径对拍。

#### 我的第一反应

> 第一反应是树形 DP（1.6 骨架四）：辅助函数返回“链长/高度”，全局 `ans` 维护“直径”。写完对照灵茶题解，发现就是他的写法二。自己当时困惑的两个点：为什么必须拆一个辅助函数、为什么不能直接 `return dfs(root)`——因为递归需要的是**链长**，而题目要的是由**两条链拼接**成的直径，两个是不同的量。

#### 解法一：树形 DP（写法二：空节点返回 0，我的写法）

##### 两个关键概念（面试必须说清）

设 node 是二叉树中的任意节点：

- **链**：从 node 子树中的某个叶子到 node 的路径。`dfs(node)` 的返回值 = node 子树中最长链的长度；
- **直径**：由**两条链拼接**而成的路径。枚举每个 node，假设直径在这里“拐弯”，用 `左链 + 右链` 更新全局答案。

两个 ⚠：

- **直径可能在 root 下面的某个节点拐弯，不一定会经过 root**；
- **`dfs(node)` 返回的是链长，不是直径**——如果返回直径，父节点拿到的就不是“可拼接的链”，拼出来的东西没有意义。

##### 代码（我的写法）

```go
func diameterOfBinaryTree(root *TreeNode) (ans int) {
    var dfs func(node *TreeNode) int
    dfs = func(node *TreeNode) int {
        if node == nil {
            return 0
        }
        lHeight := dfs(node.Left)  // 左子树的最大链长
        rHeight := dfs(node.Right) // 右子树的最大链长
        ans = max(ans, lHeight+rHeight) // 两条链在这里拼接成路径
        return max(lHeight, rHeight) + 1 // 返回当前子树的最大链长
    }
    dfs(root)
    return
}
```

灵茶山艾府的写法二与本代码完全一致。

##### 逐行理解

- 空节点返回 0：叶子节点的链长为 1（0+1），是计数的地基；
- `lHeight` / `rHeight`：后序位置先拿左右子树的链长；
- `ans = max(ans, lHeight+rHeight)`：**当前节点把左链和右链拼成一条路径**，更新全局直径；
- `return max(lHeight, rHeight) + 1`：向上返回的是“更长的那条链 + 当前节点”，供父节点继续拼接。

##### 完整运行示例（逐轮表格）

树：`1` 左 `2`（左 `4` 右 `5`）右 `3`，即 `[1,2,3,4,5]`，期望直径 3（路径 `4→2→1→3` 有 3 条边）。

| 节点 | 左链长 | 右链长 | ans 更新 | 返回（链长） |
|---|---|---|---|---|
| 4 | 0 | 0 | max(0, 0)=0 | 1 |
| 5 | 0 | 0 | max(0, 0)=0 | 1 |
| 2 | 1 | 1 | max(0, 2)=2 | 2 |
| 3 | 0 | 0 | max(2, 0)=2 | 1 |
| 1 | 2 | 1 | max(2, 3)=3 | 3 |

最终 `ans = 3` ✅。

##### 复杂度

- **时间复杂度：\(O(n)\)**。每个节点访问一次。
- **空间复杂度：\(O(h)\)**。`h` 为树高，最坏偏斜成链时 \(O(n)\)。

#### 解法二：写法一（空节点返回 -1，灵茶山艾府）

##### 思路

严格按“链 = 叶子到 node 的路径”来定义：一条链经过的**边数**才是它的长度，所以空节点返回 -1，这样叶子算出来的链长是 `-1 + 1 = 0`。

##### 代码（灵茶山艾府）

```go
func diameterOfBinaryTree(root *TreeNode) (ans int) {
    // 返回 node 子树的最大链长（边数）
    var dfs func(*TreeNode) int
    dfs = func(node *TreeNode) int {
        if node == nil {
            return -1 // 对于叶子来说，链长就是 -1+1=0
        }
        lLen := dfs(node.Left) + 1  // 左子树最大链长 +1
        rLen := dfs(node.Right) + 1 // 右子树最大链长 +1
        ans = max(ans, lLen+rLen)   // 两条链拼成路径
        return max(lLen, rLen)      // 当前子树最大链长
    }
    dfs(root)
    return
}
```

##### 两种写法等价

| | 写法二（我的写法） | 写法一（-1 边界） |
|---|---|---|
| 空节点返回 | 0 | -1 |
| 链长计数 | 节点数（叶子=1） | 边数（叶子=0） |
| 父节点取链 | `dfs(child)` 直接用 | `dfs(child) + 1` |
| 拼接路径 | `lHeight + rHeight` | `lLen + rLen` |
| 结果 | 都是边的数量 | 都是边的数量 |

选哪种看习惯；面试时讲清“返回值是链长不是直径”即可。

#### 什么时候需要辅助函数，为什么不能直接 return dfs(root)（面试必须说清）

判断标准一句话：**递归子问题返回的东西，和题目要求的答案，是不是同一个量**。

- 是同一个量（如 104 最大深度）：`maxDepth(node)` 返回的就是“以 node 为根的深度”，可以直接在原函数上递归并 `return`；
- 不是同一个量（如 543）：递归需要的是“链长”，题目要的是“直径”。直径由两条链拼接而成，父节点需要的是**子树的链长**而不是子树的直径，所以必须拆一个辅助函数 `dfs` 返回链长，再配一个全局 `ans` 维护直径——这就是 1.6 骨架四。

为什么不能直接 `return dfs(root)`？因为 `dfs(root)` 返回的是整棵树的**最大链长（高度）**，而直径是“两条链拼接”的最大值，可能在任意节点拐弯、不一定经过根，数值上也不等于根的高度。

反例：一条左链 `1→2→3→4`（`[1,2,nil,3,nil,4]`），写法二里 `dfs(root)` 返回 4（节点数链长），但直径是 3（边数）。直接返回 `dfs(root)` 就错了；正确答案来自遍历中 `ans = max(ans, lHeight+rHeight)` 的更新。

再比如直径不过根的树：`1` 只有左子树，最长路径 `5→3→2→4→7` 在左子树内部拐弯、完全不经过 root 1——这种情况下更不可能用根的高度当直径。

**通用规律**：以后遇到“答案由两个子树结果组合而成”的题（110 平衡二叉树、124 二叉树中的最大路径和、687 最长同值路径），都用这个模式：辅助函数返回子树信息，全局变量维护答案。

#### 对比与复盘

| 对比项 | 写法二（0 边界） | 写法一（-1 边界） |
|---|---|---|
| 空节点返回 | 0 | -1 |
| 链长含义 | 节点数 | 边数 |
| 核心动作 | `ans=max(ans,l+r); return max(l,r)+1` | `ans=max(ans,l+r); return max(l,r)`（l/r 已 +1） |
| 时间/空间 | \(O(n)\) / \(O(h)\) | \(O(n)\) / \(O(h)\) |
| 可读性 | 更直观、面试常用 | 严格贴合“链=边”定义 |

#### 本地测试（表驱动）

复用 `treeFromSlice` / `intPtr`：

```go
func TestDiameterOfBinaryTree(t *testing.T) {
    tests := []struct {
        name string
        vals []*int
        want int
    }{
        {"empty", nil, 0},
        {"single", []*int{intPtr(1)}, 0},
        {"leetcode-example", []*int{intPtr(1), intPtr(2), intPtr(3), intPtr(4), intPtr(5)}, 3},
        {"not-through-root", []*int{intPtr(1), intPtr(2), nil, intPtr(3), intPtr(4), intPtr(5), intPtr(6), intPtr(7), intPtr(8)}, 4},
        {"left-chain", []*int{intPtr(1), intPtr(2), nil, intPtr(3), nil, intPtr(4)}, 3},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := diameterOfBinaryTree(treeFromSlice(tt.vals)); got != tt.want {
                t.Errorf("got %d, want %d", got, tt.want)
            }
        })
    }
}
```

用例说明：`not-through-root` 的最长路径 `5→3→2→4→7`（4 条边）不经过根节点 1；`left-chain` 用来验证“不能直接 return dfs(root)”——链长 4 而直径 3。

#### 易错点

1. `dfs` 返回直径而不是链长：父节点拿不到可拼接的链，结果错乱。
2. 忘记更新全局 `ans`：只在返回值里算，根节点拼出来的不是全局最大。
3. 直径可能在子树内部拐弯：别只算“经过根”的路径。
4. 边界返回值记混：写法二空节点 0，写法一空节点 -1；混用会整体偏移。
5. 直接把 `return dfs(root)` 当答案：返回的是链长/高度，不是直径。
6. 链长计数和边数换算不清：无论哪种写法，`左链 + 右链` 最终都等于路径**边数**。

#### 建议测试案例

```text
[]                        → 0        // 空树
[1]                       → 0        // 单点
[1,2,3,4,5]               → 3        // 经过根的路径 4-2-1-3
[1,2,nil,3,4,5,6,7,8]     → 4        // 最长路 5-3-2-4-7 不过根
[1,2,nil,3,nil,4]         → 3        // 左链：dfs(root)=4（链长）≠ 直径 3
```

#### 可迁移的规律

- **树形 DP 模板（骨架四）**：辅助函数返回子树信息（链长/高度/和），全局变量维护答案（直径/最大和）。
- **“返回子问题值 + 全局答案”的判断**：答案由两个子树结果组合而成时就用这个模式——110 平衡二叉树、124 最大路径和、687 最长同值路径。
- **什么时候不需要辅助函数**：递归返回值本身就是答案（104 深度、226 翻转），直接写原函数即可。

#### 来源说明

- [LeetCode 543. 二叉树的直径题解列表](https://leetcode.cn/problems/diameter-of-binary-tree/solutions/)
- 灵茶山艾府《【视频】彻底掌握直径 DP，从二叉树到一般树》（树形 DP，基础算法精讲 23）。

#### 重做记录

> 2026-08-23：完成树形 DP 两种写法；重做时重点检查：dfs 返回链长而不是直径、全局 ans 的更新、直径不过根的情况、不能直接 return dfs(root)。

---

### 题目 98：验证二叉搜索树

#### 题目摘要

- **题目链接**：[LeetCode 98. 验证二叉搜索树](https://leetcode.cn/problems/validate-binary-search-tree/)
- **输入**：二叉树根节点 `root`。
- **输出**：是否为有效 BST（`bool`）。
- **关键约束**：节点数 `[1, 10^4]`；节点值可能触及 `int` 极值。
- **核心模式**：中序升序 / 上下界递归。
- **面试必须说清**：为什么只比较父子不够？中序前值/上下界如何处理极值？
- **本地测试标准**：深层违规、重复、MinInt/MaxInt；不使用不安全哨兵。

#### 我的第一反应

> 第一反应是**前序上下界**：`dfs(node, left, right)` 把“从根到当前节点的路径约束”往下传，当前值必须在 `(left, right)` 内。后来写了**中序前值**版：BST 中序严格升序，`pre` 记录上一个值，`<= pre` 即违规。**后序版当时没写出来**——不知道子树该返回什么；看完题解才明白：后序要自底向上，子树返回自己的 `(min, max)`，父节点用 `x > 左子树最大值 && x < 右子树最小值` 判断。

#### 解法一：前序遍历（上下界，我的写法）

##### 怎么想的

BST 的定义是“左子树所有节点 < 根 < 右子树所有节点”，这个约束在往下走的过程中会不断收紧：往左走，右边界变成当前值；往右走，左边界变成当前值。所以用**前序位置**检查当前节点是否在 `(left, right)` 区间内，再把收紧后的区间传给左右子树。

为什么只比较父子不够？因为深层节点可能违背**祖先**的界限——比如 5 的右子树里出现 3，3 比父节点 4 小、但它还在 5 的右子树里，必须用从根传下来的下界 5 才能抓住它。

##### 代码（我的写法）

```go
func isValidBSTPre(root *TreeNode) bool {
    var dfs func(node *TreeNode, left, right int) bool
    dfs = func(node *TreeNode, left, right int) bool {
        if node == nil {
            return true
        }
        num := node.Val
        return left < num && num < right &&
            dfs(node.Left, left, num) &&
            dfs(node.Right, num, right)
    }
    return dfs(root, math.MinInt, math.MaxInt)
}
```

灵茶山艾府的前序写法与本代码完全一致。

##### 逐行理解

- 空节点返回 true：空树 / 叶子没有违反任何约束；
- `left < num && num < right`：当前值必须在开区间内（严格不等）；
- `dfs(node.Left, left, num)`：左子树的所有值还要大于 left，且**小于当前值**（上界收紧）；
- `dfs(node.Right, num, right)`：右子树的所有值还要大于当前值（下界收紧），且小于 right；
- 短路求值：一旦某个条件失败，后面的递归不再执行。

##### 完整运行示例（逐轮表格）

合法树 `[2,1,3]`：

| 节点 | left | right | 判断 |
|---|---|---|---|
| 2 | MinInt | MaxInt | MinInt < 2 < MaxInt ✅ |
| 1 | MinInt | 2 | MinInt < 1 < 2 ✅ |
| 3 | 2 | MaxInt | 2 < 3 < MaxInt ✅ |

非法树 `[5,1,4,nil,nil,3,6]`（3 在 5 的右子树却小于 5）：

| 节点 | left | right | 判断 |
|---|---|---|---|
| 5 | MinInt | MaxInt | ✅ |
| 1 | MinInt | 5 | ✅ |
| 4 | 5 | MaxInt | 5 < 4 ❌ → 返回 false |

节点 4 本身在 `(5, MaxInt)` 之外，前序在这里就返回了——**不需要递归到叶子**。

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(n)\)**。最坏偏斜成链，递归栈 O(n)。

#### 解法二：中序遍历（前值，我的写法）

##### 怎么想的

BST 的中序遍历 = **严格递增的有序数组**（hello-algo 7.4）。判断数组是否升序，只需要比较相邻元素；对应到树上就是：中序位置检查 `node.Val > pre`，然后更新 `pre`。这个思路利用 BST 性质，需要维护的状态最少。

##### 代码（我的写法）

```go
func isValidBSTIn(root *TreeNode) bool {
    pre := math.MinInt
    var dfs func(node *TreeNode) bool
    dfs = func(node *TreeNode) bool {
        if node == nil {
            return true
        }
        if !dfs(node.Left) { // 左
            return false
        }
        if node.Val <= pre { // 中：必须严格大于前值
            return false
        }
        pre = node.Val
        return dfs(node.Right) // 右
    }
    return dfs(root)
}
```

灵茶山艾府的中序写法与本代码完全一致。

##### 逐行理解

- 先递归左子树：左子树先被“摊平”成有序序列的前半段；
- `node.Val <= pre`：中序位置比较相邻元素，等于也算违规（BST 不允许重复）；
- `pre = node.Val`：更新前值，给右子树里的节点比较；
- 左右任一处违规立刻短路返回。

##### 完整运行示例（逐轮表格）

非法树 `[5,1,4,nil,nil,3,6]`，中序序列应为 `1, 5, 3, 4, 6`：

| 访问节点 | pre（进入时） | 判断 | 更新后 pre |
|---|---|---|---|
| 1 | MinInt | 1 > MinInt ✅ | 1 |
| 5 | 1 | 5 > 1 ✅ | 5 |
| 3 | 5 | 3 <= 5 ❌ 返回 false | — |

在节点 3 处抓住违规（中序必须至少递归到一个叶子）。

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(n)\)**。

#### 解法三：后序遍历（子树 min/max，灵茶山艾府）

##### 怎么想的

后序是**自底向上**：先让左右子树各自报告“我子树里的最小值和最大值”，当前节点检查 `x > 左子树最大值 && x < 右子树最小值`，然后把自己的 `(min, max)` 上报给父节点。这就是树形 DP 的多返回值模式——子树信息向上汇总。

空子树怎么处理？返回 `(MaxInt, MinInt)`：这是“空集”的 min/max，任何数跟它取 min/max 都不受影响，相当于恒等元素。

##### 代码（灵茶山艾府）

```go
func isValidBSTPost(root *TreeNode) bool {
    var dfs func(node *TreeNode) (int, int) // 返回子树的最小值、最大值
    dfs = func(node *TreeNode) (int, int) {
        if node == nil {
            return math.MaxInt, math.MinInt // 空子树的 (min, max) 恒等元素
        }
        lMin, lMax := dfs(node.Left)
        rMin, rMax := dfs(node.Right)
        x := node.Val
        if x <= lMax || x >= rMin { // 违反：x 必须大于左子树最大值、小于右子树最小值
            return math.MinInt, math.MaxInt // 用 (MinInt, MaxInt) 标记整棵子树非法
        }
        return min(lMin, x), max(rMax, x) // 上报包含当前节点后的 (min, max)
    }
    _, mx := dfs(root)
    return mx != math.MaxInt // 若根子树被标记非法，mx 就是 MaxInt
}
```

##### 逐行理解

- 空节点返回 `(MaxInt, MinInt)`：叶子上报时 `min(MaxInt, x) = x`、`max(MinInt, x) = x`，正好是它自己；
- `x <= lMax`：当前值必须大于左子树里所有值（左子树最大值）；
- `x >= rMin`：当前值必须小于右子树里所有值（右子树最小值）；
- 违规时返回 `(MinInt, MaxInt)` 作为“非法标记”，一路向上传播；
- 合法时返回 `(min(lMin, x), max(rMax, x))`：把当前节点合并进子树的 min/max；
- 最后 `mx != math.MaxInt`：如果根子树没被标记非法，就是合法 BST（Go 里节点值最多到 int32 范围，合法的 max 不可能等于 math.MaxInt）。

##### 完整运行示例（逐轮表格）

合法树 `[2,1,3]`：

| 节点 | 左子树 (min,max) | 右子树 (min,max) | 判断 | 返回 |
|---|---|---|---|---|
| 1 | (MaxInt, MinInt) | (MaxInt, MinInt) | 1<=MinInt? 否；1>=MaxInt? 否 | (1, 1) |
| 3 | (MaxInt, MinInt) | (MaxInt, MinInt) | 通过 | (3, 3) |
| 2 | (1, 1) | (3, 3) | 1<2<3 ✅ | (1, 3) |

`mx = 3 != MaxInt` → true ✅

非法树 `[5,1,4,nil,nil,3,6]`：

| 节点 | 左子树 (min,max) | 右子树 (min,max) | 判断 | 返回 |
|---|---|---|---|---|
| 1 | 空 | 空 | 通过 | (1, 1) |
| 3 | 空 | 空 | 通过 | (3, 3) |
| 6 | 空 | 空 | 通过 | (6, 6) |
| 4 | (3, 3) | (6, 6) | 3<4<6 ✅ | (3, 6) |
| 5 | (1, 1) | (3, 6) | 5 >= rMin=3 ❌ | (MinInt, MaxInt) |

`mx = MaxInt` → false ✅。注意 4 这层是合法的，违规在根节点 5 处才暴露——后序必须先把子树算完。

##### 复杂度

- **时间复杂度：\(O(n)\)**。
- **空间复杂度：\(O(n)\)**。

#### 极值处理（面试必须说清）

上下界版本用 `math.MinInt / math.MaxInt` 当哨兵：Go 的 `int` 在 64 位平台是 64 位，比题目允许的节点值范围（int32）严格更小/更大，所以**当前代码实测安全**。

但这是“依赖 int 位宽”的写法：在 32 位 Go、或 Java 的 `int` 场景，节点值可能等于 `MinInt/MaxInt` 本身，`left < x` 或 `x <= pre` 就会误判。Java 题解因此用 `long`；更稳妥、可移植的做法是**用 `*int`，nil 表示“无界”**：

```go
func isValidBST(root *TreeNode) bool {
    var dfs func(node *TreeNode, lo, hi *int) bool
    dfs = func(node *TreeNode, lo, hi *int) bool {
        if node == nil {
            return true
        }
        if lo != nil && node.Val <= *lo {
            return false
        }
        if hi != nil && node.Val >= *hi {
            return false
        }
        return dfs(node.Left, lo, &node.Val) &&
            dfs(node.Right, &node.Val, hi)
    }
    return dfs(root, nil, nil)
}
```

中序版本同理，把 `pre` 改成 `*int`：

```go
var pre *int
// 检查处：if pre != nil && node.Val <= *pre { return false }
```

#### 对比与复盘

| 对比项 | 前序（上下界） | 中序（前值） | 后序（子树 min/max） |
|---|---|---|---|
| 检查位置 | 前序：进节点时 | 中序：左子树之后 | 后序：左右子树算完 |
| 核心思路 | 路径约束向下传 | 中序严格升序 | 子树信息向上汇总 |
| 提前返回 | 某些数据可不递归到叶子 | 至少要递归到一个叶子 | 至少要递归到一个叶子 |
| 需要变量 | 2 个区间参数 | 1 个前值 | 子树 min/max |
| 思想定位 | 自上而下传状态 | 用 BST 性质，最省变量 | 自底向上，最通用（DP 基础） |

#### 本地测试（表驱动 + 三实现对拍）

复用 `treeFromSlice` / `intPtr`，三种实现跑同一批用例：

```go
func TestIsValidBST(t *testing.T) {
    tests := []struct {
        name string
        vals []*int
        want bool
    }{
        {"empty", nil, true},
        {"single", []*int{intPtr(1)}, true},
        {"valid", []*int{intPtr(2), intPtr(1), intPtr(3)}, true},
        {"invalid-deep", []*int{intPtr(5), intPtr(1), intPtr(4), nil, nil, intPtr(3), intPtr(6)}, false},
        {"duplicate", []*int{intPtr(1), intPtr(1)}, false},
        {"extreme-min", []*int{intPtr(math.MinInt32)}, true},
        {"extreme-invalid", []*int{intPtr(math.MaxInt32), intPtr(math.MaxInt32)}, false},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := isValidBSTPre(treeFromSlice(tt.vals)); got != tt.want {
                t.Errorf("前序 got %v, want %v", got, tt.want)
            }
            if got := isValidBSTIn(treeFromSlice(tt.vals)); got != tt.want {
                t.Errorf("中序 got %v, want %v", got, tt.want)
            }
            if got := isValidBSTPost(treeFromSlice(tt.vals)); got != tt.want {
                t.Errorf("后序 got %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### 易错点

1. 只比较父子节点：深层节点会漏掉祖先的界限（必须传上下界或用中序/后序）。
2. 用 `<=` / `>=` 而不是 `<` / `>`：BST 不允许重复，等于就是违规。
3. 中序忘记更新 `pre`：右子树会拿旧前值比较，漏判。
4. 后序不知道空子树返回什么：空子树是 `(MaxInt, MinInt)` 恒等元素，不是 `(0, 0)`。
5. 后序违规标记 `(MinInt, MaxInt)` 与合法值混淆：Go 里合法 max 不可能等于 math.MaxInt，但换语言/位宽要小心。
6. 依赖 `math.MinInt/MaxInt` 哨兵：64 位 Go 安全，但面试要能说出 `*int`（nil=无界）的替代方案。

#### 建议测试案例

```text
[]                          → true
[1]                         → true
[2,1,3]                     → true
[5,1,4,nil,nil,3,6]         → false   // 深层违规：3 在右子树却 < 5
[1,1]                       → false   // 重复值
[MinInt32]                  → true    // 极值单点（64 位 Go 哨兵安全）
[MaxInt32, MaxInt32]        → false   // 极值重复
```

#### 可迁移的规律

- **前序上下界**：自上而下传约束——凡是“子树必须满足祖先界限”的题都用它。
- **中序前值**：BST 中序严格升序——230 第 K 小、530 最小绝对差、783 都是直接套。
- **后序子树信息**：自底向上多返回值 DP——543 直径、110 平衡、124 最大路径和；本题是“返回两个值（min/max）”的代表。
- **哨兵 vs 指针**：需要表示“无界”时优先 `*int`（nil），不要赌类型位宽。

#### 来源说明

- [LeetCode 98. 验证二叉搜索树题解列表](https://leetcode.cn/problems/validate-binary-search-tree/solutions/)
- 灵茶山艾府《【视频】前序中序后序，三种方法，一个视频讲透！》（基础算法精讲 11）。

#### 重做记录

> 2026-08-24：完成前序/中序/后序三解法；重做时重点检查：后序返回子树 min/max 的写法、极值哨兵的可移植性（`*int` 版）、中序严格升序（`<=` 违规）、三实现对拍。

---

### 5. 专题参考资料

- [Hello 算法：二叉树](https://www.hello-algo.com/chapter_tree/binary_tree/)
- [Hello 算法：二叉树遍历](https://www.hello-algo.com/chapter_tree/binary_tree_traversal/)
- [Hello 算法：二叉搜索树](https://www.hello-algo.com/chapter_tree/binary_search_tree/)
- [代码随想录：二叉树的递归遍历](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/二叉树的递归遍历.md)
- [代码随想录：二叉树的迭代遍历](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/二叉树的迭代遍历.md)
- [代码随想录：0102.二叉树的层序遍历](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0102.二叉树的层序遍历.md)
- [代码随想录：0104.二叉树的最大深度](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0104.二叉树的最大深度.md)
- [代码随想录：0226.翻转二叉树](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0226.翻转二叉树.md)
- [代码随想录：0098.验证二叉搜索树](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0098.验证二叉搜索树.md)
- [LeetCode-Go：题解对照](https://github.com/halfrost/LeetCode-Go)

---

## 专题五：图与回溯

### 1. 专题背景

本专题区分两类问题：**遍历所有连通区域**（200 岛屿数量、994 腐烂的橘子、207 课程表）和**枚举所有可行选择**（46 全排列、78 子集、39 组合总和）。底层内容来自 hello-algo 第九章《图》和第十三章《回溯》：图的定义与表示（9.1）、图的遍历（9.3）、回溯算法（13.1）、全排列问题（13.2）、子集和问题（13.3）。

#### 1.1 hello-algo 章节映射

| 本专题知识点 | hello-algo 章节 |
|---|---|
| 图的定义、术语、邻接表/邻接矩阵 | 9.1 图 |
| BFS / DFS 遍历、visited 标记 | 9.3 图的遍历 |
| 回溯三要素（尝试/回退/剪枝） | 13.1 回溯算法 |
| 全排列：selected 剪枝 | 13.2 全排列问题 |
| 子集/组合：start 剪枝、排序剪枝 | 13.3 子集和问题 |
| 拓扑排序（207） | hello-algo 未单列：底层是 9.1 的入度概念 + BFS 遍历思想 |

#### 1.2 图的基本概念与表示（hello-algo 9.1）

- 图由**顶点**和**边**组成；无向图 vs 有向图；连通图 vs 非连通图；有权图 vs 无权图；
- **度**：顶点拥有的边数；有向图中分**入度**（指向该顶点的边数）和**出度**（从该顶点指出的边数）——207 拓扑排序的核心；
- **邻接矩阵**：查边 \(O(1)\)、空间 \(O(n^2)\)；**邻接表**：只存实际边、更省空间（Go 常用 `[][]int` 或 `map[int][]int`）；
- **网格是特殊图**：200/994 把每个格子当顶点、上下左右四条边当邻接关系。

#### 1.3 图的遍历（hello-algo 9.3）

- **BFS**：队列 + visited，由近及远逐层扩散；遍历序列不唯一；复杂度 \(O(|V|+|E|)\)；
- **DFS**：递归（或显式栈）+ visited，走到尽头再回头；复杂度 \(O(|V|+|E|)\)；
- **访问标记何时设置**：入队/进入时立刻标记，不能等到“弹出/离开时”才标记——否则同一节点可能被重复入队，网格题会死循环（200、994 的必考细节）；
- **多源 BFS（994）**：把所有腐烂橘子同时入队，队列层数 = 扩散的分钟数。

#### 1.4 拓扑排序（207 课程表）

hello-algo 没有拓扑排序专章，知识基础就是 9.1 的入度 + 9.3 的 BFS 队列：

- **入度含义**：一门课还差几门前置课没修完；
- **Kahn 算法**：入度为 0 的课程入队 → 出队“修完” → 把它的后继课程入度减 1 → 入度变 0 再入队；
- **有环判断**：能出队的课程数 < 总课程数，说明存在循环依赖（环上的课入度永远不为 0）。

#### 1.5 回溯三要素（hello-algo 13.1）

回溯 = DFS + 撤销选择。核心术语：**状态（state）**、**选择集合（choices）**、**约束条件（剪枝）**、**解（solution）**。复杂度通常是指数/阶乘级，**剪枝是唯一的关键优化**。

三题的选择集合差异：

| 题 | 选择集合 | 剪枝关键 | 答案在哪 |
|---|---|---|---|
| 46 全排列 | 所有元素（每元素一次） | selected 布尔数组 | 叶子节点 |
| 78 子集 | 当前位置之后的元素 | start 递增（i+1） | 每个节点都是答案 |
| 39 组合总和 | 可重复选 | 下一轮从 i 开始；排序后超过 target 剪枝 | 达到 target 的路径 |

#### 1.6 四个骨架（Day 5 要求：从空白写）

**骨架一：网格 DFS（200 岛屿数量）**

```go
var dirs = [4][2]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}}

func dfsGrid(grid [][]byte, i, j int) {
    if i < 0 || i >= len(grid) || j < 0 || j >= len(grid[0]) || grid[i][j] != '1' {
        return
    }
    grid[i][j] = '0' // 进入时立刻标记（沉岛），防止重复访问
    for _, d := range dirs {
        dfsGrid(grid, i+d[0], j+d[1])
    }
}
```

**骨架二：多源 BFS（994 腐烂的橘子）**

```go
q := []int{} // 存坐标（如 i*n+j），所有源点同时入队
for len(q) > 0 {
    size := len(q)
    for k := 0; k < size; k++ {
        // 出队、处理四方向、新腐烂的橘子入队
    }
    minutes++
}
```

**骨架三：拓扑排序（207 课程表）**

```go
indeg := make([]int, numCourses)
graph := make([][]int, numCourses)
// 建图 + 统计入度
q := []int{}
for i, d := range indeg {
    if d == 0 {
        q = append(q, i)
    }
}
for len(q) > 0 {
    cur := q[0]
    q = q[1:]
    for _, nxt := range graph[cur] {
        indeg[nxt]--
        if indeg[nxt] == 0 {
            q = append(q, nxt)
        }
    }
}
// 出队总数 < numCourses 则有环
```

**骨架四：回溯（46/78/39 通用）**

```go
func backtrack(state []int, choices []int, start int) {
    // 1. 判断当前 state 是否是答案，是则记录（注意复制）
    // 2. 遍历选择集合（用 start / selected / 剪枝控制）
    //    for i := start; i < len(choices); i++ {
    //        做出选择：state = append(state, choices[i])
    //        backtrack(state, choices, 下一轮start) // 46 传0+selected；78 传i+1；39 传i
    //        撤销选择：state = state[:len(state)-1]
    //    }
}
```

#### 1.7 本地测试约定（Day 5）

- 表驱动；网格用 `[][]byte`/`[][]int`，图用边列表构造邻接表；
- 回溯结果**排序后比较**（结果顺序不唯一，避免顺序依赖）；
- 当天复盘：从空白写 DFS、BFS、拓扑排序和回溯四个骨架。

### 2. 本专题题目看板

题目来自 Day 5 执行清单，难度标记沿用 A/B 分组。

| 状态 | 分组 | 题号 | 题目 | 核心训练点 | 笔记 |
|:---:|:---:|---:|---|---|---|
| ⬜ | A | 200 | [岛屿数量](https://leetcode.cn/problems/number-of-islands/) | 网格 DFS/BFS、访问标记时机 | [查看](#题目-200岛屿数量) |
| ⬜ | A | 994 | [腐烂的橘子](https://leetcode.cn/problems/rotting-oranges/) | 多源 BFS、同时入队 | [查看](#题目-994腐烂的橘子) |
| ⬜ | A | 207 | [课程表](https://leetcode.cn/problems/course-schedule/) | 拓扑排序、入度、有环判断 | [查看](#题目-207课程表) |
| ⬜ | A | 46 | [全排列](https://leetcode.cn/problems/permutations/) | 回溯、路径与选择集合 | [查看](#题目-46全排列) |
| ⬜ | A | 78 | [子集](https://leetcode.cn/problems/subsets/) | 回溯、每个节点都是答案 | [查看](#题目-78子集) |
| ⬜ | B | 39 | [组合总和](https://leetcode.cn/problems/combination-sum/) | 回溯、剪枝、可重复选择 | [查看](#题目-39组合总和) |

状态说明：

- ⬜ 未开始
- 🟡 已完成首次提交，尚未复盘
- ✅ 已完成题解与复盘
- 🔁 已独立重做

### 3. 每道题的记录模板

以后新增题目时复制下面这段：

```markdown
### 题目 X：题目名称

#### 题目摘要

- **题目链接**：
- **输入**：
- **输出**：
- **关键约束**：
- **核心模式**：
- **面试必须说清**：
- **本地测试标准**：

#### 我的第一反应

> 记录最初思路、踩过的坑（即使后来发现不对，也保留）。

#### 解法一：直觉 / 暴力解法

##### 我的思路
##### 代码
##### 复杂度
##### 主要关注点

#### 解法二：优化解法

##### 优化突破口
##### 代码
##### 逐行理解
##### 完整运行示例（逐轮表格）
##### 复杂度
##### 关键不变量

#### 对比与复盘

| 对比项 | 解法一 | 解法二 |
|---|---|---|
| 时间复杂度 |  |  |
| 空间复杂度 |  |  |
| 核心操作 |  |  |
| 优点 |  |  |
| 局限 |  |  |

#### 本地测试（表驱动）

#### 易错点

#### 建议测试案例

#### 可迁移的规律

#### 来源说明

#### 重做记录
```

---

### 题目 200：岛屿数量

#### 题目摘要

- **题目链接**：[LeetCode 200. 岛屿数量](https://leetcode.cn/problems/number-of-islands/)
- **输入**：`m×n` 网格 `grid [][]byte`（`'1'` 陆地、`'0'` 水）。
- **输出**：岛屿数量（相邻的 1 组成一座岛，四方向连通）。
- **关键约束**：`m,n ∈ [1, 300]`。
- **核心模式**：网格 DFS/BFS + 访问标记。
- **面试必须说清**：访问标记何时设置（进入/入队时立刻标记）。
- **本地测试标准**：空网格、全 1、全 0、单岛、多岛、环形岛。

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

### 题目 994：腐烂的橘子

#### 题目摘要

- **题目链接**：[LeetCode 994. 腐烂的橘子](https://leetcode.cn/problems/rotting-oranges/)
- **输入**：`grid [][]int`（`0` 空、`1` 新鲜、`2` 腐烂）。
- **输出**：全部腐烂所需分钟数；无法全部腐烂返回 `-1`。
- **关键约束**：`m,n ∈ [1, 10]`。
- **核心模式**：多源 BFS。
- **面试必须说清**：为什么所有腐烂橘子同时入队（同步扩散，层数 = 分钟）。
- **本地测试标准**：无新鲜、无腐烂、被隔离的新鲜橘子（-1）、多源混合。

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

### 题目 207：课程表

#### 题目摘要

- **题目链接**：[LeetCode 207. 课程表](https://leetcode.cn/problems/course-schedule/)
- **输入**：课程数 `numCourses` 和先修关系 `prerequisites`。
- **输出**：能否完成所有课程（`bool`）。
- **关键约束**：课程数 `[1, 2000]`。
- **核心模式**：拓扑排序（Kahn）+ 入度。
- **面试必须说清**：入度含义和有环判断。
- **本地测试标准**：无先修、线性链、环、自环、多依赖。

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

### 题目 46：全排列

#### 题目摘要

- **题目链接**：[LeetCode 46. 全排列](https://leetcode.cn/problems/permutations/)
- **输入**：不含重复数字的数组 `nums`。
- **输出**：所有全排列。
- **关键约束**：长度 `[1, 6]`。
- **核心模式**：回溯。
- **面试必须说清**：路径和选择集合如何维护（`selected` 布尔数组）。
- **本地测试标准**：长度 1/2/3；结果数量为 `n!`。

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

### 题目 78：子集

#### 题目摘要

- **题目链接**：[LeetCode 78. 子集](https://leetcode.cn/problems/subsets/)
- **输入**：不含重复元素的数组 `nums`。
- **输出**：所有子集。
- **关键约束**：长度 `[1, 10]`。
- **核心模式**：回溯。
- **面试必须说清**：每个节点为什么都是答案。
- **本地测试标准**：空集、单元素；`n=3` 共 8 个子集。

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

### 题目 39：组合总和

#### 题目摘要

- **题目链接**：[LeetCode 39. 组合总和](https://leetcode.cn/problems/combination-sum/)
- **输入**：无重复整数 `candidates` 和目标 `target`。
- **输出**：所有和为 `target` 的组合（每个元素可重复选择）。
- **关键约束**：`candidates` 长度 `[2, 40]`，`target` 为正整数。
- **核心模式**：回溯 + 剪枝。
- **面试必须说清**：元素重复选择如何实现（下一轮从 `i` 开始而不是 `i+1`）。
- **本地测试标准**：单元素、避免顺序重复、排序剪枝、无解。

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

### 5. 专题参考资料

- [Hello 算法：图](https://www.hello-algo.com/chapter_graph/graph/)
- [Hello 算法：图的遍历](https://www.hello-algo.com/chapter_graph/graph_traversal/)
- [Hello 算法：回溯算法](https://www.hello-algo.com/chapter_backtracking/backtracking_algorithm/)
- [Hello 算法：全排列问题](https://www.hello-algo.com/chapter_backtracking/permutations_problem/)
- [Hello 算法：子集和问题](https://www.hello-algo.com/chapter_backtracking/subset_sum_problem/)
- [代码随想录：0200.岛屿数量](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0200.岛屿数量.md)
- [代码随想录：0994.腐烂的橘子](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0994.腐烂的橘子.md)
- [代码随想录：0207.课程表](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0207.课程表.md)
- [代码随想录：0046.全排列](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0046.全排列.md)
- [代码随想录：0078.子集](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0078.子集.md)
- [代码随想录：0039.组合总和](https://github.com/youngyangyang04/leetcode-master/blob/master/problems/0039.组合总和.md)
- [LeetCode-Go：题解对照](https://github.com/halfrost/LeetCode-Go)
