---
title: "16 个常用设计模式・Java / Go 双语言版：业务场景 + 痛点 + 代码，一表看懂"
description: "8 大高频设计模式 + 8 个第二梯队模式，补充备忘录、迭代器、命令、桥接模式：典型业务场景、痛点、什么时候不用；Java / Go 页签一键切换对照，开头一张总结表帮你一眼分清 16 个模式。"
date: 2026-08-18T00:00:00+08:00
slug: "java-design-patterns-scenarios"
categories:
    - Programming
tags:
    - Java
    - Go
    - Design Patterns
    - Architecture
    - 面试
toc: true
---

# 🧩 16 个常用设计模式・Java / Go 双语言版：场景、痛点、代码一表看懂

> 这篇博客整理自一份《8 大高频设计模式・详细业务场景 + 痛点 + 什么时候不用》的笔记，并做了三件事：
>
> 1. **内容审核**：逐个核对了模式归类、场景描述和结论，与经典 GoF 设计模式分类一致，细节核对结果放在文末「内容审核与补充说明」；
> 2. **双语言代码**：每个模式的代码框里都有 **Java / Go 两个页签，一键切换对照**，想用哪种语言看哪种；
> 3. **保留原文**：场景、痛点、口诀一字不删；原文 Go 代码全部保留，直接放在每个模式的代码页签里，不再单独设附录。

在原有 12 个模式的基础上，本文补充了 **备忘录 Memento、迭代器 Iterator、命令 Command、桥接 Bridge**，共 16 个模式。「第一梯队 / 第二梯队」沿用原笔记的学习分组，不代表严格的使用频率排名。

先看总表，再逐一看细节，也可以配合「易混模式对照」和「工厂 + 策略组合实战」理解模式之间的关系。

## 📋 开篇总结表：16 个模式一眼看懂

| 模式 | 类型 | 核心一句话 | 典型业务场景 | 什么时候不用 | 一句话口诀 |
|---|---|---|---|---|---|
| 单例 Singleton | 创建型 | 全局唯一实例 | 数据库连接池、全局配置、日志、Redis/MQ 客户端 | 需要多份独立状态；单测难 mock | 全项目只有一份，谁拿都是它 |
| 简单工厂 Simple Factory | 创建型 | 按类型统一创建对象，选择只发生在创建时 | 支付渠道、文件导出器、消息发送 | 产品常新增且不想改工厂；中途要换实现 | 一次性选好对象，用完拉倒 |
| 建造者 Builder | 创建型 | 分步构建字段多、可选参数多的复杂对象 | 复杂订单、多条件查询、HTTP 请求体、报表对象 | 字段只有 2-3 个 | 字段太多，链式 Builder 慢慢搭 |
| 适配器 Adapter | 结构型 | 转换接口，做翻译层 | 第三方支付 SDK、新旧接口字段映射、多数据源 | 接口本来就一致 | 别人的接口和我不一样 → 加一层适配器翻译 |
| 装饰器 Decorator | 结构型 | 动态叠加附加能力，不改原代码 | 日志/耗时/链路、缓存、权限、文件流包装 | 要完全替换主体逻辑 | 原来的功能我还要，只是额外加点东西 |
| 代理 Proxy | 结构型 | 替身控制对真实对象的访问 | RPC 远程调用、权限拦截、懒加载、限流熔断 | 只是加日志计时 | 访问真实对象之前，先管控一下能不能进 |
| 策略 Strategy | 行为型 | 同一目标多种算法，运行时可切换 | 折扣、运费、排序、导出格式 | 创建后永不换实现 | 同一个任务多种方案，中途可以换 |
| 观察者 Observer | 行为型 | 一对多事件通知，主流程解耦 | 下单成功后的扣库存/短信/账单/积分、注册事件、MQ | 强依赖、必须顺序执行 | 一件事做完，触发一堆附属事情 |
| 外观 Facade | 结构型 | 简单入口，隐藏复杂子系统 | 下单聚合库存/支付/物流 | 子系统本来就简单 | 复杂一堆子系统 → 一个入口 |
| 责任链 Chain | 行为型 | 一条流水线依次处理，可中断 | 参数→权限→限流→业务、审批流 | 环节不固定、职责常变 | 校验/审批一条流水线，中途失败就截断 |
| 状态 State | 行为型 | 行为随内部状态自动变化，状态间可转换 | 订单状态流转、工单/审批 | 状态少且流转简单 | 一个对象内部状态流转、自动切换行为 |
| 模板方法 Template | 行为型 | 固定流程骨架，子类重写部分步骤 | 报表导出（加载→格式化→保存） | 流程本身不固定 | 流程骨架固定不变，只有部分步骤自定义 |
| 备忘录 Memento | 行为型 | 在不暴露内部细节的前提下保存、恢复对象状态 | 编辑器撤销、表单草稿回退、游戏存档 | 状态太大且快照频繁；需要撤销外部副作用 | 先存一份状态，后悔时读档 |
| 迭代器 Iterator | 行为型 | 统一遍历入口，隐藏集合内部结构 | 订单集合、树形目录、分页结果遍历 | 普通集合直接循环就够用 | 只管取下一个，不管里面怎么存 |
| 命令 Command | 行为型 | 把请求封装成对象，分离发起者与执行者 | 按钮与快捷键、任务队列、操作撤销 | 一次直接调用就能表达清楚 | 把要做的事装成命令，交给别人执行 |
| 桥接 Bridge | 结构型 | 拆开两个独立变化的维度，用组合连接 | 通知级别 × 发送渠道、报表种类 × 输出格式、控件类型 × 绘制平台 | 只有一个变化维度；维度之间强耦合 | 两个维度各自扩展，组合搭桥 |

---

# 一、8 大高频设计模式（第一梯队）

## 1. 单例 Singleton｜创建型

**核心：全局唯一实例**

### ✅ 典型业务场景

- **数据库连接池**
  痛点：每次请求新建数据库连接，连接数爆炸、性能差。
  做法：全局只有一个连接池对象，所有线程共用。
- **全局配置管理器 Config**
  加载一次 yaml/json 配置文件，全项目读取同一份配置，避免重复读文件。
- **日志 Logger 实例**
  整个服务共用同一个日志句柄，统一控制日志级别、输出文件。
- **Redis 客户端、MQ 客户端**
  不要每次发消息新建一个 redis 连接。

### ⚠️ 什么时候不要用

- 需要多份独立状态；
- 单元测试很难 mock 单例。

### ☕ 双语言示例（Java / Go 页签切换）

原版 Go 用 `sync.Once` 保证「只初始化一次」，Java 最接近的等价写法是**双重检查锁（DCL）**：

{{< tabs >}}
{{< tab "Java" >}}
```java
public class Config {
    // volatile：防止“先返回半初始化对象”的指令重排问题
    private static volatile Config instance;
    public String dbHost;

    private Config() {
        System.out.println("初始化配置");
        dbHost = "127.0.0.1";
    }

    // 双重检查锁（DCL）：懒加载 + 线程安全
    public static Config getInstance() {
        if (instance == null) {                 // 第一次检查：避免无谓加锁
            synchronized (Config.class) {
                if (instance == null) {         // 第二次检查：保证全局唯一
                    instance = new Config();
                }
            }
        }
        return instance;
    }

    public static void main(String[] args) {
        Config c1 = Config.getInstance();
        Config c2 = Config.getInstance();
        System.out.println(c1 == c2);   // true：拿到的始终是同一个实例
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import (
	"fmt"
	"sync"
)

type Config struct {
	DBHost string
}

var (
	instance *Config
	once     sync.Once
)

func GetConfig() *Config {
	once.Do(func() {
		fmt.Println("初始化配置")
		instance = &Config{DBHost: "127.0.0.1"}
	})
	return instance
}

func main() {
	c1 := GetConfig()
	c2 := GetConfig()
	fmt.Println(c1 == c2)
}
```
{{< /tab >}}
{{< /tabs >}}

> 补充：Java 里线程安全的单例还有「静态内部类」和「枚举」两种写法，其中**枚举**天然线程安全、防反射、防序列化破坏，最推荐：
>
> ```java
> public enum ConfigEnum {
>     INSTANCE;                  // 全局只有一个 INSTANCE
>     public String dbHost = "127.0.0.1";
> }
> ```

### 一句话口诀（补充）

> 全局只要一份，谁拿都是它 → 单例

---

## 2. 简单工厂 Simple Factory｜创建型

**核心：统一创建对象；根据类型选择实现；选择仅发生在创建时**

### ✅ 典型业务场景

- **多种支付渠道创建：支付宝、微信、银行卡、PayPal**
  痛点：散落在代码各处到处 `if ("alipay".equals(type)) { return new Alipay(); }`，创建逻辑分散难维护。
  工厂收拢所有支付对象创建。拿到实例后直接 Pay，中途一般不换支付方式。
- **文件导出器：导出 Excel、PDF、CSV、Word**
  用户一次导出任务选定格式，导出完任务结束，中途不会切换导出格式。
- **消息发送工具：短信、邮件、站内信、钉钉通知**
  根据消息类型，工厂返回对应的发送实例，执行一次发送。

### ⚠️ 什么时候不要用

- 产品列表经常新增，且不想修改工厂代码 → 改用工厂方法模式。
- 需要运行中途更换行为 → 用策略模式，不是工厂。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
// 支付接口：所有支付方式都实现它
interface Payment {
    void pay(double amount);
}

class Alipay implements Payment {
    public void pay(double amount) {
        System.out.printf("支付宝支付 %.2f%n", amount);
    }
}

class WechatPay implements Payment {
    public void pay(double amount) {
        System.out.printf("微信支付 %.2f%n", amount);
    }
}

// 工厂：把所有“创建支付对象”的逻辑收拢到一处
class PaymentFactory {
    public static Payment create(String type) {
        switch (type) {
            case "alipay": return new Alipay();
            case "wechat": return new WechatPay();
            default:       return null;
        }
    }
}

public class Main {
    public static void main(String[] args) {
        // 创建时选定实现，拿到实例后直接 Pay
        Payment pay = PaymentFactory.create("alipay");
        pay.pay(100);
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

type Payment interface {
	Pay(amount float64)
}

type Alipay struct{}
func (a Alipay) Pay(amount float64) {
	fmt.Printf("支付宝支付 %.2f\n", amount)
}

type WechatPay struct{}
func (w WechatPay) Pay(amount float64) {
	fmt.Printf("微信支付 %.2f\n", amount)
}

func NewPayment(typ string) Payment {
	switch typ {
	case "alipay":
		return Alipay{}
	case "wechat":
		return WechatPay{}
	default:
		return nil
	}
}

func main() {
	pay := NewPayment("alipay")
	pay.Pay(100)
}
```
{{< /tab >}}
{{< /tabs >}}

### 一句话口诀（原文）

> 一次性选好对象，用完拉倒 → 工厂

---

## 3. 建造者 Builder｜创建型

**核心：分步构建复杂对象；字段多、可选参数多**

### ✅ 典型业务场景

- **复杂订单对象 Order**
  字段：订单号、用户 id、商品、优惠券、运费、折扣、备注、地址、发票信息。
  很多字段可选，如果直接构造函数，会出现超长参数列表，极易传参顺序出错。
  链式调用：`new Order.Builder().setUser(...).setGoods(...).setDiscount(...).build()`。
- **复杂查询条件 QueryCondition**
  数据库多条件查询：时间范围、页码、排序、状态、关键词、标签。很多条件非必填。
- **HTTP 复杂请求体、API DTO**
  调用第三方 API，body 参数庞大，部分字段可选。
- **报表生成对象**
  报表标题、行列、样式、筛选条件、导出格式。

### ⚠️ 什么时候不要用

- 对象属性很少（2-3 个字段），直接赋值就行，builder 属于过度设计。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
public class Order {
    // 字段多、可选参数多：构造函数根本写不过来
    private final String orderNo;
    private final int userId;
    private final int goodsId;
    private final double discount;

    // 私有构造：只能通过 Builder 创建
    private Order(Builder b) {
        this.orderNo = b.orderNo;
        this.userId = b.userId;
        this.goodsId = b.goodsId;
        this.discount = b.discount;
    }

    // 链式构建器：每个 set 方法返回 this，最后 build()
    public static class Builder {
        private String orderNo;
        private int userId;
        private int goodsId;
        private double discount;

        public Builder setOrderNo(String orderNo) { this.orderNo = orderNo; return this; }
        public Builder setUserId(int userId)      { this.userId = userId;   return this; }
        public Builder setGoodsId(int goodsId)    { this.goodsId = goodsId; return this; }
        public Builder setDiscount(double d)      { this.discount = d;      return this; }

        public Order build() {
            return new Order(this);
        }
    }

    @Override
    public String toString() {
        return "Order{orderNo='" + orderNo + "', userId=" + userId
                + ", goodsId=" + goodsId + ", discount=" + discount + '}';
    }

    public static void main(String[] args) {
        Order order = new Order.Builder()
                .setOrderNo("O1001")
                .setUserId(123)
                .setGoodsId(456)
                .setDiscount(0.9)
                .build();
        System.out.println(order);
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

type Order struct {
	OrderNo  string
	UserID   int
	GoodsID  int
	Discount float64
}

type OrderBuilder struct {
	order Order
}

func NewOrderBuilder() *OrderBuilder {
	return &OrderBuilder{}
}

func (b *OrderBuilder) SetOrderNo(no string) *OrderBuilder {
	b.order.OrderNo = no
	return b
}
func (b *OrderBuilder) SetUserID(id int) *OrderBuilder {
	b.order.UserID = id
	return b
}
func (b *OrderBuilder) SetGoodsID(id int) *OrderBuilder {
	b.order.GoodsID = id
	return b
}
func (b *OrderBuilder) SetDiscount(d float64) *OrderBuilder {
	b.order.Discount = d
	return b
}

func (b *OrderBuilder) Build() Order {
	return b.order
}

func main() {
	order := NewOrderBuilder().
		SetOrderNo("O1001").
		SetUserID(123).
		SetGoodsID(456).
		SetDiscount(0.9).
		Build()
	fmt.Println(order)
}
```
{{< /tab >}}
{{< /tabs >}}

> 补充：实际项目中常用 Lombok 的 `@Builder` 注解自动生成这套代码，写法不变、省掉样板代码。

### 一句话口诀（补充）

> 字段太多、可选太多 → 链式 Builder 慢慢搭

---

## 4. 适配器 Adapter｜结构型

**核心：转换接口，让两个不兼容的东西一起工作；做翻译层**

### ✅ 典型业务场景

- **接入多个第三方支付 SDK**
  支付宝 SDK 方法名：`alipay.tradePay()`；
  微信 SDK：`wx.unifiedOrder()`。
  两个第三方接口完全不一样。写一层适配器，对外统一暴露 `pay(amount)`，内部调用各自 sdk。上层业务代码不用改。
- **新旧系统对接，老接口改造**
  老系统返回字段 `user_name`；新系统需要 `username`。适配器做字段映射转换。
- **多数据源适配**
  同时读 MySQL、Elasticsearch、MongoDB，对外统一查询接口。
- **第三方消息推送服务商切换**
  极光、个推，封装统一接口。

### ⚠️ 什么时候不要用

- 接口本身就一致，不需要转换；不要为了适配而适配增加无用代码。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
// 目标接口：上层业务只认这一个
interface Target {
    String request();
}

// 第三方老 SDK：方法名、返回格式都跟我们的目标不一致
class OldSdk {
    public String oldRequest() {
        return "第三方返回数据";
    }
}

// 适配器：做一层“翻译”，把旧接口转换成目标接口
class Adapter implements Target {
    private OldSdk old;

    public Adapter(OldSdk old) {
        this.old = old;
    }

    @Override
    public String request() {
        return old.oldRequest();
    }
}

public class Main {
    public static void main(String[] args) {
        Target client = new Adapter(new OldSdk());
        System.out.println(client.request());
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

type Target interface {
	Request() string
}

type OldSDK struct{}
func (o *OldSDK) OldRequest() string {
	return "第三方返回数据"
}

type Adapter struct {
	old *OldSDK
}

func (a *Adapter) Request() string {
	return a.old.OldRequest()
}

func main() {
	client := &Adapter{old: &OldSDK{}}
	fmt.Println(client.Request())
}
```
{{< /tab >}}
{{< /tabs >}}

### 一句话口诀（原文）

> 别人的接口和我不一样 → 加一层适配器翻译

---

## 5. 装饰器 Decorator｜结构型

**核心：动态给原有功能叠加附加能力；不改原有函数代码**

**关注点：增强功能，不是替换主体逻辑**

### ✅ 典型业务场景

- **给接口增加横切能力**
  原有核心函数：`createOrder()`；
  装饰加上：打印入参日志、函数耗时统计、异常捕获、链路 TraceId。
  原业务代码完全不动。
- **缓存装饰器**
  原始函数从数据库查询用户；装饰一层：先查 Redis 缓存，没命中再查 DB。
- **权限校验**
  原始 handler 执行业务；装饰器先校验 token、角色权限。
- **文件流多层包装**
  文件读取 → 加解压 → 加解密。

### ⚠️ 什么时候不要用

- 需要完全替换掉原有业务逻辑；替换用策略模式，增强用装饰器。

### ☕ 双语言示例（Java / Go 页签切换）

原版 Go 用「函数包函数」实现装饰，Java 里对应的是「装饰器类持有原对象、实现同一接口」：

{{< tabs >}}
{{< tab "Java" >}}
```java
interface Handler {
    void execute();
}

// 原始业务：只干一件事
class BizTask implements Handler {
    public void execute() {
        System.out.println("执行业务逻辑");
    }
}

// 装饰器：给原功能叠加日志，BizTask 一行代码都不用改
class LogDecorator implements Handler {
    private final Handler target;

    public LogDecorator(Handler target) {
        this.target = target;
    }

    public void execute() {
        System.out.println("开始执行");
        target.execute();
        System.out.println("执行结束");
    }
}

public class Main {
    public static void main(String[] args) {
        // 想要日志：包一层；不想要：直接用 new BizTask()
        Handler task = new LogDecorator(new BizTask());
        task.execute();
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

type Handler func()

func WithLog(h Handler) Handler {
	return func() {
		fmt.Println("开始执行")
		h()
		fmt.Println("执行结束")
	}
}

func BizTask() {
	fmt.Println("执行业务逻辑")
}

func main() {
	task := WithLog(BizTask)
	task()
}
```
{{< /tab >}}
{{< /tabs >}}

> 补充：JDK 里的 `BufferedInputStream` 包 `FileInputStream`、`InflaterInputStream` 包普通输入流，就是文件流多层包装的现成例子；Spring 的 `@Transactional`、切面日志本质上也是同一思想。

### 一句话口诀（原文）

> 原来的功能我还要，只是额外加点东西 → 装饰器

---

## 6. 代理 Proxy｜结构型

**核心：找一个替身控制访问真实对象；做访问控制、延迟加载**

**和装饰器区别：装饰器增强功能；代理控制对象访问。**

### ✅ 典型业务场景

- **RPC 远程调用代理**
  你调用本地接口方法，实际代理帮你发 http/grpc 请求到远程服务。
- **权限拦截**
  访问管理员接口前，代理校验用户是不是管理员，不通过直接拒绝，不去调用真实服务。
- **延迟加载（懒加载）**
  一个很重的大对象（大数据报表），先不初始化；等到第一次调用 `do()` 的时候，代理才去创建真实对象。
- **限流熔断**
  代理层控制接口 QPS，超流量直接返回降级结果，不访问真实服务。
- **接口访问日志审计**

### ⚠️ 什么时候不要用

- 单纯给函数加日志计时 → 优先装饰器。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
interface Subject {
    void doWork();
}

class RealService implements Subject {
    public void doWork() {
        System.out.println("真实业务操作");
    }
}

// 代理：权限校验 + 懒加载 + 日志，都在代理层做
class Proxy implements Subject {
    private RealService real;   // 懒加载：第一次用才创建

    public void doWork() {
        System.out.println("权限校验");
        if (real == null) {
            real = new RealService();
        }
        real.doWork();
        System.out.println("记录操作日志");
    }
}

public class Main {
    public static void main(String[] args) {
        Subject proxy = new Proxy();
        proxy.doWork();
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

type Subject interface {
	Do()
}

type RealService struct{}
func (r *RealService) Do() {
	fmt.Println("真实业务操作")
}

type Proxy struct {
	real *RealService
}

func (p *Proxy) Do() {
	fmt.Println("权限校验")
	if p.real == nil {
		p.real = &RealService{}
	}
	p.real.Do()
	fmt.Println("记录操作日志")
}

func main() {
	proxy := &Proxy{}
	proxy.Do()
}
```
{{< /tab >}}
{{< /tabs >}}

> 补充：代理**可以不调用真实对象**——权限校验不通过时直接 return，真实服务根本不会执行，这就是它和装饰器最本质的区别。Java 里的 JDK 动态代理、CGLIB、Spring AOP 都是代理思想的实现。

### 一句话口诀（原文）

> 访问真实对象之前，我想先管控一下能不能进 → 代理

---

## 7. 策略 Strategy｜行为型

**核心：同一业务目标，多种可互换的算法；运行时随时切换算法**

**重点！有上下文 Context 持有策略，可以 set 更换**

### ✅ 典型业务场景

- **订单折扣计算（最经典）**
  策略 A：满 100-20；策略 B：9 折；策略 C：会员价；策略 D：无优惠。
  同一个订单，中途可以切换优惠方案重新算价。
- **运费计算策略**
  普通快递、顺丰特快、同城跑腿，运费公式完全不一样。运行时可切换。
- **文件排序算法**
  按价格升序、按销量、按创建时间排序，随时切换排序策略。
- **导出文件的内容格式化逻辑**
  导出用户报表，可以切换：精简版、完整版、财务版。

### ⚠️ 什么时候不要用

- 创建完对象，后面永远不会更换实现 → 简单工厂就够了，不需要策略。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
// 策略接口：同一目标，多种算法
interface Discount {
    double calc(double price);
}

// 策略 A：满 100 减 20
class FullReduction implements Discount {
    public double calc(double price) {
        return price >= 100 ? price - 20 : price;
    }
}

// 策略 B：9 折
class PercentOff implements Discount {
    public double calc(double price) {
        return price * 0.9;
    }
}

// 上下文 Context：持有策略，运行时可切换
class Order {
    private Discount discount;

    public void setDiscount(Discount discount) {
        this.discount = discount;
    }

    public double getPrice(double origin) {
        return discount.calc(origin);
    }
}

public class Main {
    public static void main(String[] args) {
        Order order = new Order();

        order.setDiscount(new FullReduction());
        System.out.println(order.getPrice(150));   // 130.0

        // 中途切换优惠方案，重新算价
        order.setDiscount(new PercentOff());
        System.out.println(order.getPrice(150));   // 135.0
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

type Discount interface {
	Calc(price float64) float64
}

type FullReduction struct{}
func (f FullReduction) Calc(price float64) float64 {
	if price >= 100 {
		return price - 20
	}
	return price
}

type PercentOff struct{}
func (p PercentOff) Calc(price float64) float64 {
	return price * 0.9
}

type Order struct {
	discount Discount
}
func (o *Order) SetDiscount(d Discount) {
	o.discount = d
}
func (o *Order) GetPrice(origin float64) float64 {
	return o.discount.Calc(origin)
}

func main() {
	order := &Order{}
	order.SetDiscount(FullReduction{})
	fmt.Println(order.GetPrice(150))

	order.SetDiscount(PercentOff{})
	fmt.Println(order.GetPrice(150))
}
```
{{< /tab >}}
{{< /tabs >}}

### 一句话口诀（原文）

> 同一个任务，有多种方案可选，中途可以换方案 → 策略

---

## 8. 观察者 Observer（发布-订阅）｜行为型

**核心：一对多事件通知；主流程和后续动作解耦**

### ✅ 典型业务场景

- **下单成功事件**
  主流程：只负责创建订单，然后发出「订单创建成功」事件。
  订阅者 1：扣减商品库存；
  订阅者 2：发送短信通知用户；
  订阅者 3：生成财务账单；
  订阅者 4：更新用户积分。
  ✅ 好处：新增后续动作，完全不用修改下单主流程代码。
- **用户注册成功事件**
  欢迎短信、初始化钱包、发送欢迎邮件。
- **MQ 消息、kafka 事件监听本质就是观察者模式**
- **配置文件变更事件**
  配置修改后，通知所有服务模块重载配置。

### ⚠️ 什么时候不要用

- 流程是强依赖、必须顺序执行；不要用观察者，直接串行调用。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
import java.util.ArrayList;
import java.util.List;

// 观察者：关心事件的对象
interface Observer {
    void update(String msg);
}

// 被观察者（主题）：维护订阅者列表，事件发生后挨个通知
class Subject {
    private final List<Observer> observers = new ArrayList<>();

    public void attach(Observer observer) {
        observers.add(observer);
    }

    public void notify(String msg) {
        for (Observer observer : observers) {
            observer.update(msg);
        }
    }
}

class SmsNotify implements Observer {
    public void update(String msg) {
        System.out.println("短信收到事件：" + msg);
    }
}

class StockService implements Observer {
    public void update(String msg) {
        System.out.println("库存收到事件：" + msg);
    }
}

public class Main {
    public static void main(String[] args) {
        Subject subject = new Subject();
        subject.attach(new SmsNotify());
        subject.attach(new StockService());

        // 下单主流程只发一个事件，后续动作全部解耦
        subject.notify("订单创建成功");
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

type Observer interface {
	Update(msg string)
}

type Subject struct {
	observers []Observer
}

func (s *Subject) Attach(o Observer) {
	s.observers = append(s.observers, o)
}

func (s *Subject) Notify(msg string) {
	for _, o := range s.observers {
		o.Update(msg)
	}
}

type SmsNotify struct{}
func (s SmsNotify) Update(msg string) {
	fmt.Println("短信收到事件：", msg)
}

type StockService struct{}
func (s StockService) Update(msg string) {
	fmt.Println("库存收到事件：", msg)
}

func main() {
	subject := &Subject{}
	subject.Attach(SmsNotify{})
	subject.Attach(StockService{})

	subject.Notify("订单创建成功")
}
```
{{< /tab >}}
{{< /tabs >}}

> 补充：Java 内置的 `Observable/Observer` 已废弃；Spring 的 `ApplicationEventPublisher` + `@EventListener` 就是观察者模式的现成实现。进程内观察者默认同步执行，MQ/Kafka 是它思想在分布式场景下的实现（异步、削峰）。

### 一句话口诀（原文）

> 一件事做完之后，一堆无关的附属事情要被触发 → 观察者

---

# 二、易混模式快速对照 + 组合实战

## 📌 工厂 vs 策略 场景快速区分对照表（原文）

| 业务需求 | 选模式 |
|---|---|
| 用户下单，一次性选支付宝，付完结束，中途不会换微信 | 简单工厂 |
| 订单生成后，可以来回切换支付宝 / 微信重新支付 | 策略模式 +（工厂生成策略对象） |

一句话：**选完就不换 → 工厂；选完还要来回换 → 策略**。

## 📌 装饰器 vs 代理（原文）

- **装饰器**：增强原有功能，目标对象一定会被执行；
- **代理**：控制访问，有可能直接拦截，根本不调用真实对象。

## 📌 状态 vs 策略（补充）

- **状态模式**：状态之间可以互相转换，由「状态自己」决定下一个状态（订单：待支付 → 已支付 → 已发货）；
- **策略模式**：策略之间互相独立，由「上下文 Context」决定什么时候换（折扣：9 折 ↔ 满减，互不关联）。

## 📌 桥接 vs 适配器 vs 策略（补充）

| 模式 | 主要解决什么问题 | 通知系统里的例子 |
|---|---|---|
| 桥接 Bridge | 两个维度都要独立扩展，避免为每种组合建一个类 | 普通 / 紧急通知与邮件 / 短信渠道分开定义，再自由组合 |
| 适配器 Adapter | 已有接口不兼容，需要转换调用方式或数据 | 把短信 SDK 的 `sendSms(phone, body)` 转成系统统一的 `Sender.send(userId, content)` |
| 策略 Strategy | 同一个目标有多种可替换算法 | 对同一类通知选择固定间隔或指数退避的重试算法 |

桥接和策略都可能表现为「持有一个接口并委托调用」，区别要看设计意图：**桥接强调两套类型各自演化，策略强调替换某一项行为的算法**。仅仅注入一个接口，或支持运行时切换实现，都不足以单独判定是桥接；桥接也不要求必须在运行中切换实现。

两者还能和适配器配合：先用适配器把各家发送 SDK 接到 `Sender` 接口，再让通知类型通过这个接口组合渠道。

## 📌 备忘录 vs 命令 vs 策略（补充）

| 模式 | 关注的问题 | 编辑器里的例子 |
|---|---|---|
| 备忘录 Memento | 怎样保存并恢复「之前是什么样」 | 保存编辑前的正文、光标位置，撤销时恢复 |
| 命令 Command | 怎样封装「这次要做什么」并交给调用者管理 | 把插入文字封装成命令，按钮和快捷键共用执行入口 |
| 策略 Strategy | 同一个目标采用哪种可替换算法 | 同一段文字选择不同的排版算法 |

**命令和备忘录可以配合使用**：命令在执行前向编辑器索取快照，撤销时交还快照。命令负责操作的执行与管理，备忘录负责保存恢复所需的状态；命令本身并不要求一定支持撤销。

## 📌 迭代器 vs 责任链（补充）

- **迭代器**：从集合中依次取出数据，业务处理由调用方决定；
- **责任链**：把同一个请求交给一组处理器，决定继续传递还是结束。

遍历十个订单用迭代器；对一个订单依次做参数、权限和额度检查用责任链。两者都可能出现循环，但分离的职责不同。

## 🚀 工厂 + 策略 组合完整示例（Java / Go 页签切换）

业务中最常一起搭配使用：**工厂负责创建策略对象，上下文负责使用、切换策略对象**。

思路说明：

- 策略：支付宝、微信支付，属于可互换的支付算法；
- 简单工厂：负责根据类型字符串，生成对应的策略实例；
- 上下文 Context（Order）：持有策略，运行时可以随时更换支付策略；
- 职责拆分：工厂 = 创建策略对象；上下文 = 使用、切换策略对象。

{{< tabs >}}
{{< tab "Java" >}}
```java
// ---------------------- 策略层：定义多种支付行为 ----------------------
interface Payment {
    void pay(double amount);
}

class Alipay implements Payment {
    public void pay(double amount) {
        System.out.printf("支付宝支付：%.2f 元%n", amount);
    }
}

class WechatPay implements Payment {
    public void pay(double amount) {
        System.out.printf("微信支付：%.2f 元%n", amount);
    }
}

// ---------------------- 工厂层：生产策略对象，把 if-else 创建逻辑收拢 ----------------------
class PaymentFactory {
    public static Payment create(String payType) {
        switch (payType) {
            case "alipay": return new Alipay();
            case "wechat": return new WechatPay();
            default:       return null;
        }
    }
}

// ---------------------- 上下文 Context：使用 & 切换策略 ----------------------
class Order {
    private Payment payment;

    // 运行时更换支付策略
    public void setPayment(Payment payment) {
        this.payment = payment;
    }

    public void checkout(double amount) {
        if (payment == null) {
            System.out.println("未选择支付方式");
            return;
        }
        payment.pay(amount);
    }
}

public class Main {
    public static void main(String[] args) {
        Order order = new Order();

        // 工厂生成支付宝策略，上下文使用
        order.setPayment(PaymentFactory.create("alipay"));
        order.checkout(100);

        // 中途切换微信支付：工厂生成新策略，上下文替换
        order.setPayment(PaymentFactory.create("wechat"));
        order.checkout(200);
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

// ---------------------- 策略层 ----------------------
// Payment 支付策略接口
type Payment interface {
	Pay(amount float64)
}

// Alipay 支付宝策略
type Alipay struct{}

func (a Alipay) Pay(amount float64) {
	fmt.Printf("支付宝支付：%.2f 元\n", amount)
}

// WechatPay 微信支付策略
type WechatPay struct{}

func (w WechatPay) Pay(amount float64) {
	fmt.Printf("微信支付：%.2f 元\n", amount)
}

// ---------------------- 工厂层：生产策略对象 ----------------------
func NewPaymentStrategy(payType string) Payment {
	switch payType {
	case "alipay":
		return Alipay{}
	case "wechat":
		return WechatPay{}
	default:
		return nil
	}
}

// ---------------------- 上下文 Context：使用&切换策略 ----------------------
type Order struct {
	payment Payment
}

// SetPayment 运行时更换支付策略
func (o *Order) SetPayment(p Payment) {
	o.payment = p
}

func (o *Order) Checkout(amount float64) {
	if o.payment == nil {
		fmt.Println("未选择支付方式")
		return
	}
	o.payment.Pay(amount)
}

// ---------------------- 主程序 ----------------------
func main() {
	order := &Order{}

	// 工厂生成支付宝策略，上下文使用
	p1 := NewPaymentStrategy("alipay")
	order.SetPayment(p1)
	order.Checkout(100)

	// 中途切换微信支付，工厂生成新策略
	p2 := NewPaymentStrategy("wechat")
	order.SetPayment(p2)
	order.Checkout(200)
}
```
{{< /tab >}}
{{< /tabs >}}

运行输出：

```text
支付宝支付：100.00 元
微信支付：200.00 元
```

三者角色对比：

| 组件 | 干什么 |
|---|---|
| 策略接口 & 实现 | 定义多种支付行为 |
| 工厂 | 统一创建策略实例，把 if-else 创建逻辑收拢 |
| Order 上下文 | 持有策略引用，随时调用、随时替换 |

业务好处：

- 上层业务不用到处 `new Alipay()`；
- 如果后面新增银行卡支付，只需要：新增一个类实现 `Payment`，工厂 `switch` 加一条 `case`，业务代码（上下文 Order）无需改动。

> 再进一步：把工厂的 `switch` 换成「注册表 + 工厂方法」，新增渠道时连工厂都不改，就完全满足开闭原则了（本文先不过度展开）。

---

# 三、第二梯队 8 个常用模式

## 9. 外观模式 Facade（结构型）

**作用：对外提供一个简单入口，隐藏内部一堆复杂子系统**

**场景：下单入口，内部依次调用库存、支付、物流；上层只调用一个 `createOrder()`，不用关心内部多个子服务。**

### ⚠️ 什么时候不要用（补充）

- 子系统调用关系本来就简单、只有一两个类，加门面属于过度设计；
- 门面不要越做越大变成「上帝类」——它只负责编排入口，不负责塞业务逻辑。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
// 子系统 1：库存
class StockService {
    public void deduct(int goodsId) {
        System.out.println("扣减商品 " + goodsId + " 库存");
    }
}

// 子系统 2：支付
class PayService {
    public void pay(double amount) {
        System.out.printf("支付金额 %.2f%n", amount);
    }
}

// 子系统 3：物流
class LogisticsService {
    public void createShipment(String orderNo) {
        System.out.println("创建物流单：" + orderNo);
    }
}

// 外观门面：对外一个简单方法，封装所有复杂流程
class OrderFacade {
    private final StockService stock = new StockService();
    private final PayService pay = new PayService();
    private final LogisticsService logistics = new LogisticsService();

    public void createOrder(int goodsId, double amount, String orderNo) {
        stock.deduct(goodsId);
        pay.pay(amount);
        logistics.createShipment(orderNo);
    }
}

public class Main {
    public static void main(String[] args) {
        OrderFacade facade = new OrderFacade();
        // 上层只需要调用一个方法，无需关心内部子系统
        facade.createOrder(1001, 99.0, "ORD-001");
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

// 子系统1：库存
type StockService struct{}
func (s *StockService) Deduct(goodsId int) {
	fmt.Printf("扣减商品 %d 库存\n", goodsId)
}

// 子系统2：支付
type PayService struct{}
func (p *PayService) Pay(amount float64) {
	fmt.Printf("支付金额 %.2f\n", amount)
}

// 子系统3：物流
type LogisticsService struct{}
func (l *LogisticsService) CreateShipment(orderNo string) {
	fmt.Printf("创建物流单：%s\n", orderNo)
}

// 外观门面
type OrderFacade struct {
	stock  *StockService
	pay    *PayService
	logist *LogisticsService
}

func NewOrderFacade() *OrderFacade {
	return &OrderFacade{
		stock:  &StockService{},
		pay:    &PayService{},
		logist: &LogisticsService{},
	}
}

// 对外一个简单方法，封装所有复杂流程
func (f *OrderFacade) CreateOrder(goodsId int, amount float64, orderNo string) {
	f.stock.Deduct(goodsId)
	f.pay.Pay(amount)
	f.logist.CreateShipment(orderNo)
}

func main() {
	facade := NewOrderFacade()
	// 上层只需要调用一个方法，无需关心内部子系统
	facade.CreateOrder(1001, 99.0, "ORD-001")
}
```
{{< /tab >}}
{{< /tabs >}}

### 一句话口诀（补充）

> 复杂一堆子系统 → 一个入口调用

---

## 10. 责任链 Chain of Responsibility（行为型）

**作用：一条处理链条，请求依次经过每个处理器，可中断**

**场景：接口校验链路 → 参数校验 → 权限校验 → 限流校验 → 执行业务；审批流（员工 → 主管 → 经理）**

### ⚠️ 什么时候不要用（补充）

- 环节顺序不固定、职责经常增删，链条会很难维护；
- 只有两三个简单 `if` 校验，直接写就行，不需要责任链。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
// 处理器抽象：定义链式结构
abstract class Handler {
    private Handler next;

    // 返回 next 方便链式串接：new ParamCheck().setNext(new AuthCheck())...
    public Handler setNext(Handler next) {
        this.next = next;
        return next;
    }

    public abstract boolean handle(int request);

    // 传给下一个处理器；没有下一个就返回 true（放行）
    protected boolean pass(int request) {
        if (next != null) {
            return next.handle(request);
        }
        return true;
    }
}

// 参数校验
class ParamCheck extends Handler {
    public boolean handle(int request) {
        if (request <= 0) {
            System.out.println("参数非法，终止");
            return false;
        }
        System.out.println("参数校验通过");
        return pass(request);
    }
}

// 权限校验
class AuthCheck extends Handler {
    public boolean handle(int request) {
        if (request < 100) {
            System.out.println("权限不足，终止");
            return false;
        }
        System.out.println("权限校验通过");
        return pass(request);
    }
}

// 业务执行
class BizHandler extends Handler {
    public boolean handle(int request) {
        System.out.println("执行业务逻辑，请求值：" + request);
        return true;
    }
}

public class Main {
    public static void main(String[] args) {
        // 串起链条：参数校验 → 权限校验 → 业务执行
        new ParamCheck()
                .setNext(new AuthCheck())
                .setNext(new BizHandler())
                .handle(200);
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

// 处理器接口
type Handler interface {
	Handle(request int) bool
	SetNext(h Handler)
}

// 基础处理器
type BaseHandler struct {
	next Handler
}
func (b *BaseHandler) SetNext(h Handler) {
	b.next = h
}
func (b *BaseHandler) pass(req int) bool {
	if b.next != nil {
		return b.next.Handle(req)
	}
	return true
}

// 参数校验
type ParamCheck struct{ BaseHandler }
func (p *ParamCheck) Handle(request int) bool {
	if request <= 0 {
		fmt.Println("参数非法，终止")
		return false
	}
	fmt.Println("参数校验通过")
	return p.pass(request)
}

// 权限校验
type AuthCheck struct{ BaseHandler }
func (a *AuthCheck) Handle(request int) bool {
	if request < 100 {
		fmt.Println("权限不足，终止")
		return false
	}
	fmt.Println("权限校验通过")
	return a.pass(request)
}

// 业务执行
type BizHandler struct{ BaseHandler }
func (b *BizHandler) Handle(request int) bool {
	fmt.Println("执行业务逻辑，请求值：", request)
	return true
}

func main() {
	param := &ParamCheck{}
	auth := &AuthCheck{}
	biz := &BizHandler{}
	// 串起链条
	param.SetNext(auth)
	auth.SetNext(biz)

	param.Handle(200)
}
```
{{< /tab >}}
{{< /tabs >}}

### 一句话口诀（补充）

> 校验 / 审批一条流水线，中途失败就截断

---

## 11. 状态模式 State（行为型）

**作用：对象行为随内部状态自动变化；大量 if-else 状态判断的替代品**

**场景：订单状态流转：待支付 → 已支付 → 已发货 → 已完成；工单、审批。**

**和策略区别：状态之间可以互相转换，策略之间互相独立。**

### ⚠️ 什么时候不要用（补充）

- 状态很少（2-3 个）且流转逻辑简单，用 if-else 反而更直白；
- 状态固定不变、没有「自动流转」的需求，不需要引入状态对象。

### ☕ 双语言示例（Java / Go 页签切换）

{{< tabs >}}
{{< tab "Java" >}}
```java
// 状态接口
interface OrderState {
    void next(Order order);
}

// 上下文订单：持有当前状态
class Order {
    private OrderState state;

    public Order(OrderState state) {
        this.state = state;
    }

    public void setState(OrderState state) {
        this.state = state;
    }

    public void action() {
        state.next(this);
    }
}

// 待支付
class WaitPay implements OrderState {
    public void next(Order order) {
        System.out.println("订单：待支付 → 切换到已支付");
        order.setState(new Paid());
    }
}

// 已支付
class Paid implements OrderState {
    public void next(Order order) {
        System.out.println("订单：已支付 → 切换到已发货");
        order.setState(new Shipped());
    }
}

// 已发货
class Shipped implements OrderState {
    public void next(Order order) {
        System.out.println("订单：已发货 → 切换到已完成");
        order.setState(new Completed());
    }
}

// 已完成
class Completed implements OrderState {
    public void next(Order order) {
        System.out.println("订单已完成，不可变更");
    }
}

public class Main {
    public static void main(String[] args) {
        Order order = new Order(new WaitPay());
        order.action();   // 待支付 → 已支付
        order.action();   // 已支付 → 已发货
        order.action();   // 已发货 → 已完成
        order.action();   // 已完成，不可变更
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

// 状态接口
type OrderState interface {
	Next(order *Order)
}

// 上下文订单
type Order struct {
	state OrderState
}
func (o *Order) SetState(s OrderState) {
	o.state = s
}
func (o *Order) Action() {
	o.state.Next(o)
}

// 待支付
type WaitPay struct{}
func (w *WaitPay) Next(order *Order) {
	fmt.Println("订单：待支付 → 切换到已支付")
	order.SetState(&Paid{})
}

// 已支付
type Paid struct{}
func (p *Paid) Next(order *Order) {
	fmt.Println("订单：已支付 → 切换到已发货")
	order.SetState(&Shipped{})
}

// 已发货
type Shipped struct{}
func (s *Shipped) Next(order *Order) {
	fmt.Println("订单：已发货 → 切换到已完成")
	order.SetState(&Completed{})
}

// 已完成
type Completed struct{}
func (c *Completed) Next(order *Order) {
	fmt.Println("订单已完成，不可变更")
}

func main() {
	order := &Order{state:&WaitPay{}}
	order.Action()
	order.Action()
	order.Action()
	order.Action()
}
```
{{< /tab >}}
{{< /tabs >}}

### 一句话口诀（补充）

> 一个对象内部状态流转、自动切换行为（订单状态）

---

## 12. 模板方法 Template-Method（行为型）

**作用：父类定义固定流程骨架，子类重写部分步骤实现不同逻辑；流程顺序不可变**

**场景：报表导出，固定流程：加载数据 → 格式化 → 保存文件；导出 Excel 和 PDF 只是格式化步骤不一样。**

### ⚠️ 什么时候不要用（补充）

- 流程本身不固定、经常要调整步骤顺序，模板方法反而束缚；
- 只有一个实现、短期内没有第二个变体，不需要先抽象模板。

### ☕ 双语言示例（Java / Go 页签切换）

原版 Go 用「接口 + 外部函数」模拟模板，Java 里更贴切的写法是**抽象类 + final 模板方法**：公共步骤写死在基类，可变步骤留成抽象方法。

{{< tabs >}}
{{< tab "Java" >}}
```java
// 抽象模板：定义整套算法骨架
abstract class ExportTemplate {

    // final：流程顺序不可被子类改变
    public final void runExport() {
        loadData();   // 公共步骤：基类实现
        format();     // 可变步骤：子类实现
        save();       // 可变步骤：子类实现
    }

    // 公共步骤写死在基类，子类不用重复写
    protected void loadData() {
        System.out.println("统一加载数据库报表数据");
    }

    protected abstract void format();
    protected abstract void save();
}

// Excel 导出：只需要实现“不同”的部分
class ExcelExport extends ExportTemplate {
    protected void format() {
        System.out.println("格式化为Excel表格");
    }

    protected void save() {
        System.out.println("保存为 .xlsx 文件");
    }
}

// PDF 导出
class PdfExport extends ExportTemplate {
    protected void format() {
        System.out.println("格式化为PDF版式");
    }

    protected void save() {
        System.out.println("保存为 .pdf 文件");
    }
}

public class Main {
    public static void main(String[] args) {
        new ExcelExport().runExport();
        System.out.println("----");
        new PdfExport().runExport();
    }
}
```
{{< /tab >}}

{{< tab "Go（原版）" >}}
```go
package main

import "fmt"

// 抽象模板，定义整套算法骨架
type ExportTemplate interface {
	LoadData()
	Format()
	Save()
}

// 模板骨架，固定流程顺序
func RunExport(t ExportTemplate) {
	t.LoadData()
	t.Format()
	t.Save()
}

// Excel导出
type ExcelExport struct{}
func (e *ExcelExport) LoadData() {
	fmt.Println("统一加载数据库报表数据")
}
func (e *ExcelExport) Format() {
	fmt.Println("格式化为Excel表格")
}
func (e *ExcelExport) Save() {
	fmt.Println("保存为 .xlsx 文件")
}

// PDF导出
type PdfExport struct{}
func (p *PdfExport) LoadData() {
	fmt.Println("统一加载数据库报表数据")
}
func (p *PdfExport) Format() {
	fmt.Println("格式化为PDF版式")
}
func (p *PdfExport) Save() {
	fmt.Println("保存为 .pdf 文件")
}

func main() {
	RunExport(&ExcelExport{})
	fmt.Println("----")
	RunExport(&PdfExport{})
}
```
{{< /tab >}}
{{< /tabs >}}

### 一句话口诀（补充）

> 流程骨架固定不变，只有部分步骤子类自定义

---

## 13. 备忘录模式 Memento（行为型）

**核心：由对象自己生成状态快照，在不暴露内部细节的前提下，允许以后恢复到这个状态。**

### ✅ 典型业务场景

- **编辑器撤销：正文、光标、选区一起回退**
  痛点：撤销按钮如果直接读取、修改编辑器的内部字段，每增加一个字段，历史管理代码也要跟着改。
  做法：编辑器自己决定快照包含哪些状态，历史管理器只保存快照，撤销时交回编辑器恢复。
- **复杂表单恢复到上一次保存的草稿**
  痛点：用户改了多个关联字段，逐个写反向操作容易漏掉状态。
  做法：在需要回退的边界保存一份完整状态，取消编辑时恢复。
- **单机游戏存档、绘图工具的画布历史**
  痛点：位置、属性、图层等状态需要成组恢复，不能只回退一个数值。
  做法：由拥有这些状态的对象生成备忘录；跨进程存档还需要额外处理持久化和版本兼容。

### ⚠️ 什么时候不要用

- 状态很大、变化又频繁，全量快照会占用大量内存；可以限制历史条数，或评估增量记录。
- 只需要撤销一个很小、可逆的操作，直接记录反向操作可能更简单。
- 已经发生支付、发短信、写外部系统等副作用：恢复内存快照不能撤销这些结果，需要对应的业务补偿。

### ☕ 双语言示例（Java / Go 页签切换）

用一个正文编辑器演示「第二版 → 第一版 → 空白」。三个角色分别是：**Editor（原发器，拥有状态）、Snapshot（备忘录）、History（管理者，保存历史）**。每次修改前保存快照，撤销时弹出最近的一份；历史为空时返回 `false`。

{{< tabs >}}
{{< tab "Java" >}}
```java
import java.util.ArrayDeque;
import java.util.Deque;

class Editor {
    private String text = "";

    public void setText(String text) { this.text = text; }
    public String getText() { return text; }

    // 外部可以持有快照，但不能读取或改写其中的状态
    public static final class Snapshot {
        private final Editor owner;
        private final String text;

        private Snapshot(Editor owner, String text) {
            this.owner = owner;
            this.text = text;
        }
    }

    public Snapshot save() {
        return new Snapshot(this, text);
    }

    public void restore(Snapshot snapshot) {
        if (snapshot.owner != this) {
            throw new IllegalArgumentException("快照不属于当前编辑器");
        }
        text = snapshot.text;
    }
}

class History {
    private final Editor editor;
    private final Deque<Editor.Snapshot> snapshots = new ArrayDeque<>();

    public History(Editor editor) { this.editor = editor; }

    public void replace(String text) {
        snapshots.push(editor.save()); // 先保存，再修改
        editor.setText(text);
    }

    public boolean undo() {
        if (snapshots.isEmpty()) return false;
        editor.restore(snapshots.pop());
        return true;
    }
}

public class Main {
    public static void main(String[] args) {
        Editor editor = new Editor();
        History history = new History(editor);
        history.replace("第一版");
        history.replace("第二版");
        System.out.println(editor.getText());
        history.undo();
        System.out.println(editor.getText());
        history.undo();
        System.out.println("恢复为空白：" + editor.getText().isEmpty());
        System.out.println("还能撤销：" + history.undo());
    }
}
```
{{< /tab >}}

{{< tab "Go" >}}
```go
package main

import "fmt"

type Editor struct {
	text string
}

func (e *Editor) SetText(text string) { e.text = text }
func (e *Editor) Text() string        { return e.text }

// 小写字段对包外不可见；管理者只保存快照，不读取其内容
type snapshot struct {
	owner *Editor
	text  string
}

func (e *Editor) save() snapshot {
	return snapshot{owner: e, text: e.text}
}

func (e *Editor) restore(s snapshot) {
	if s.owner != e {
		panic("快照不属于当前编辑器")
	}
	e.text = s.text
}

type History struct {
	editor    *Editor
	snapshots []snapshot
}

func NewHistory(editor *Editor) *History {
	return &History{editor: editor}
}

func (h *History) Replace(text string) {
	h.snapshots = append(h.snapshots, h.editor.save()) // 先保存，再修改
	h.editor.SetText(text)
}

func (h *History) Undo() bool {
	if len(h.snapshots) == 0 {
		return false
	}
	last := len(h.snapshots) - 1
	h.editor.restore(h.snapshots[last])
	h.snapshots[last] = snapshot{} // 释放弹出记录持有的引用
	h.snapshots = h.snapshots[:last]
	return true
}

func main() {
	editor := &Editor{}
	history := NewHistory(editor)
	history.Replace("第一版")
	history.Replace("第二版")
	fmt.Println(editor.Text())
	history.Undo()
	fmt.Println(editor.Text())
	history.Undo()
	fmt.Println("恢复为空白：" + fmt.Sprint(editor.Text() == ""))
	fmt.Println("还能撤销：" + fmt.Sprint(history.Undo()))
}
```
{{< /tab >}}
{{< /tabs >}}

两种语言输出一致：

```text
第二版
第一版
恢复为空白：true
还能撤销：false
```

**关键不是保存一个对象引用，而是保存不会被后续修改污染的状态。** 这里正文是不可变的字符串，快照保存旧值即可；如果换成 Java 可变列表或 Go 的 slice / map，只复制引用或容器头部不够，需要根据状态结构做深拷贝，或使用不可变数据结构。

Java 示例用嵌套类的 `private` 字段隐藏快照内容；Go 的小写名称只隔离包外访问，同包代码仍可访问，因此示例中的 `History` 主动遵守「只保管、不拆解」的约定。需要语言层面的隔离时，应把编辑器和快照实现放进独立包，对外提供不暴露状态的快照接口。示例只演示单线程内存撤销，所有需要记录的编辑都经过 `History`；重做、历史容量限制需要另外实现。

Java 标准库的 `StateEdit` 也采用了类似的状态恢复思路：由被编辑对象保存编辑前后的状态，撤销与重做时恢复对应状态。参见 [StateEdit 官方文档](https://docs.oracle.com/en/java/javase/21/docs/api/java.desktop/javax/swing/undo/StateEdit.html)。

### 一句话口诀（补充）

> 先存一份状态，后悔时读档 → 备忘录

---

## 14. 迭代器模式 Iterator（行为型）

**核心：提供统一的顺序访问入口，让调用方遍历集合时，不必知道内部用数组、链表还是树来存。**

### ✅ 典型业务场景

- **批量处理订单、商品或消息集合**
  痛点：业务直接依赖数组下标或链表节点，底层存储结构一换，遍历代码也要改。
  做法：集合提供迭代器，调用方只负责取下一个元素并处理。
- **组织架构树、文件目录遍历**
  痛点：调用方既要做业务，又要维护递归、栈或队列。
  做法：深度优先、广度优先遍历分别由迭代器维护访问状态，业务只消费返回的节点。
- **分页 API、数据库游标的逐条消费**
  痛点：每个调用方都要重复写翻页、切换缓冲区等逻辑。
  做法：在迭代接口背后按需获取下一批；此时还要设计错误返回、取消和资源关闭，不能把查询失败当成遍历结束。

### ⚠️ 什么时候不要用

- 普通数组、集合、slice 的现成遍历已经够用，直接用 Java 增强 `for` 或 Go `range`，不必额外手写迭代器。
- 主要需求是随机访问、按键查询，迭代器不能替代索引或 map。
- 需要并发修改集合却没有定义一致性规则：迭代器本身不保证线程安全，也不会自动提供数据快照。

### ☕ 双语言示例（Java / Go 页签切换）

订单批次 `OrderBatch` 隐藏内部数组 / slice，每次创建迭代器时生成一个独立游标。Java 实现 `Iterable<String>`，可直接使用增强 `for`；Go 用 `Next() (string, bool)` 表达「取到元素 / 已经结束」。

{{< tabs >}}
{{< tab "Java" >}}
```java
import java.util.Iterator;
import java.util.NoSuchElementException;

class OrderBatch implements Iterable<String> {
    private final String[] ids;

    public OrderBatch(String... ids) {
        this.ids = ids.clone(); // 不共享调用方可修改的输入数组
    }

    @Override
    public Iterator<String> iterator() {
        return new Iterator<String>() {
            private int index = 0; // 每个迭代器有自己的游标

            @Override
            public boolean hasNext() {
                return index < ids.length;
            }

            @Override
            public String next() {
                if (!hasNext()) throw new NoSuchElementException();
                return ids[index++];
            }
        };
    }
}

public class Main {
    public static void main(String[] args) {
        OrderBatch orders = new OrderBatch("O1001", "O1002");
        Iterator<String> first = orders.iterator();
        Iterator<String> second = orders.iterator();
        System.out.println("迭代器 A：" + first.next());
        System.out.println("迭代器 B：" + second.next());

        // 增强 for 会取得一个新迭代器，从头遍历
        for (String id : orders) {
            System.out.println("处理订单：" + id);
        }
    }
}
```
{{< /tab >}}

{{< tab "Go" >}}
```go
package main

import "fmt"

type OrderIterator interface {
	Next() (string, bool)
}

type OrderBatch struct {
	ids []string
}

func NewOrderBatch(ids ...string) *OrderBatch {
	return &OrderBatch{ids: append([]string(nil), ids...)}
}

func (b *OrderBatch) Iterator() OrderIterator {
	return &sliceIterator{ids: b.ids} // 每次创建一个独立游标
}

type sliceIterator struct {
	ids   []string
	index int
}

func (it *sliceIterator) Next() (string, bool) {
	if it.index >= len(it.ids) {
		return "", false
	}
	id := it.ids[it.index]
	it.index++
	return id, true
}

func main() {
	orders := NewOrderBatch("O1001", "O1002")
	first, second := orders.Iterator(), orders.Iterator()
	a, _ := first.Next() // 示例已知集合非空
	b, _ := second.Next()
	fmt.Println("迭代器 A：" + a)
	fmt.Println("迭代器 B：" + b)

	it := orders.Iterator()
	for {
		id, ok := it.Next()
		if !ok {
			break
		}
		fmt.Println("处理订单：" + id)
	}
}
```
{{< /tab >}}
{{< /tabs >}}

两种语言输出一致：

```text
迭代器 A：O1001
迭代器 B：O1001
处理订单：O1001
处理订单：O1002
```

两个迭代器都从第一条订单开始，说明**遍历位置属于迭代器，不属于集合**。示例在构造订单批次时复制输入，并且不提供修改订单号的方法；这里只演示内存集合，不涉及翻页和 I/O 错误。

Java 的 `hasNext()` 不推进游标，`next()` 在耗尽后必须抛出 `NoSuchElementException`，这是 [Iterator 官方接口](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Iterator.html) 的约定。Go 示例用 `bool` 区分空字符串元素与遍历结束；现代 Go 也可用标准库 [`iter.Seq` / `iter.Seq2`](https://pkg.go.dev/iter) 配合 `range`，这里保留显式游标便于对照 Java。

### 一句话口诀（补充）

> 只管取下一个，不管里面怎么存 → 迭代器

---

## 15. 命令模式 Command（行为型）

**核心：把一次请求连同接收者、参数封装成命令对象，让发起请求的一方不必知道具体业务怎么执行。**

### ✅ 典型业务场景

- **编辑器按钮、菜单、快捷键共用同一项操作**
  痛点：三个入口分别写一遍业务逻辑，修改时容易漏掉其中一个。
  做法：把操作封装成命令，各入口只负责触发；是否保存历史由统一的调用者管理。
- **后台任务排队、延迟执行、批量操作**
  痛点：请求一发起就直接执行，难以把「创建任务」和「何时执行」分开。
  做法：先生成携带参数的命令，再交给队列或调度器执行。命令模式提供封装边界，持久化、重试和幂等仍需另外设计。
- **绘图操作撤销、设备控制历史**
  痛点：调用方如果只知道某个方法执行过，不知道执行前的状态，就无法正确撤销。
  做法：可撤销命令保存必要的历史信息，并提供 `undo()`；调用者维护已执行命令栈。

### ⚠️ 什么时候不要用

- 只有一个简单入口，不需要排队、记录或撤销，直接方法调用或函数回调更清楚。
- 只是为同一任务替换算法，优先考虑策略模式。
- 不要给每个操作都强行加 `undo()`：发短信、真实扣款等操作不能靠恢复一个字段撤销，应设计明确的业务补偿流程。

### ☕ 双语言示例（Java / Go 页签切换）

用「开灯 → 再开一次 → 撤销 → 再撤销」说明四个角色：**Command（命令接口）、SetPowerCommand（具体命令）、Remote（调用者）、Light（接收者）**。`Remote` 只调用命令接口，真正修改设备状态的是 `Light`。

这个例子选择实现可撤销命令。**撤销开灯要恢复执行前的状态，不能无条件关灯**：如果原本已经开着，再次开灯后的撤销仍应保持开灯。

{{< tabs >}}
{{< tab "Java" >}}
```java
import java.util.ArrayDeque;
import java.util.Deque;

interface Command {
    void execute();
    void undo();
}

// 接收者：拥有并修改实际状态
class Light {
    private boolean on;

    public boolean isOn() { return on; }
    public void setOn(boolean on) { this.on = on; }
}

class SetPowerCommand implements Command {
    private final Light light;
    private final boolean target;
    private boolean previous;

    public SetPowerCommand(Light light, boolean target) {
        this.light = light;
        this.target = target;
    }

    public void execute() {
        previous = light.isOn(); // 执行时记录旧值，不在构造时记录
        light.setOn(target);
    }

    public void undo() {
        light.setOn(previous);
    }
}

class Remote {
    private final Deque<Command> history = new ArrayDeque<>();

    public void run(Command command) {
        command.execute();
        history.push(command); // 执行成功后再记入历史
    }

    public boolean undo() {
        if (history.isEmpty()) return false;
        history.pop().undo();
        return true;
    }
}

public class Main {
    public static void main(String[] args) {
        Light light = new Light();
        Remote remote = new Remote();
        // 每次操作创建新命令，避免覆盖历史命令的 previous
        remote.run(new SetPowerCommand(light, true));
        remote.run(new SetPowerCommand(light, true));
        System.out.println("连续开灯后：" + light.isOn());
        remote.undo();
        System.out.println("撤销第二次：" + light.isOn());
        remote.undo();
        System.out.println("撤销第一次：" + light.isOn());
        System.out.println("还能撤销：" + remote.undo());
    }
}
```
{{< /tab >}}

{{< tab "Go" >}}
```go
package main

import "fmt"

type Command interface {
	Execute()
	Undo()
}

type Light struct {
	on bool
}

func (l *Light) IsOn() bool    { return l.on }
func (l *Light) SetOn(on bool) { l.on = on }

type SetPowerCommand struct {
	light    *Light
	target   bool
	previous bool
}

func NewSetPowerCommand(light *Light, target bool) *SetPowerCommand {
	return &SetPowerCommand{light: light, target: target}
}

func (c *SetPowerCommand) Execute() {
	c.previous = c.light.IsOn() // 执行时记录旧值
	c.light.SetOn(c.target)
}

func (c *SetPowerCommand) Undo() {
	c.light.SetOn(c.previous)
}

type Remote struct {
	history []Command
}

func (r *Remote) Run(command Command) {
	command.Execute()
	r.history = append(r.history, command)
}

func (r *Remote) Undo() bool {
	if len(r.history) == 0 {
		return false
	}
	last := len(r.history) - 1
	r.history[last].Undo()
	r.history[last] = nil
	r.history = r.history[:last]
	return true
}

func main() {
	light := &Light{}
	remote := &Remote{}
	// 每次操作创建新命令，避免覆盖历史命令的 previous
	remote.Run(NewSetPowerCommand(light, true))
	remote.Run(NewSetPowerCommand(light, true))
	fmt.Println("连续开灯后：" + fmt.Sprint(light.IsOn()))
	remote.Undo()
	fmt.Println("撤销第二次：" + fmt.Sprint(light.IsOn()))
	remote.Undo()
	fmt.Println("撤销第一次：" + fmt.Sprint(light.IsOn()))
	fmt.Println("还能撤销：" + fmt.Sprint(remote.Undo()))
}
```
{{< /tab >}}
{{< /tabs >}}

两种语言输出一致：

```text
连续开灯后：true
撤销第二次：true
撤销第一次：false
还能撤销：false
```

第一次命令记录旧值 `false`，第二次命令记录旧值 `true`，按后进先出撤销才会逐步回到初始状态。示例假设单线程执行、每次操作使用新的命令实例，设备状态只通过这个调用者修改；这里只修改内存字段，执行与撤销不会发生 I/O 失败。接真实设备时，还要设计错误返回、失败后的历史保留，以及外部状态已变化时能否撤销。

如果接收者的状态很复杂，可以把命令里的 `previous` 换成它生成的备忘录，执行前保存、撤销时恢复。需要注意的是，**可撤销和可重试是两件事**：把请求包装成命令，不会自动让扣款等操作变成幂等操作。

多个界面入口共享操作的实际 API 可以参考 [Swing Action 官方文档](https://docs.oracle.com/en/java/javase/21/docs/api/java.desktop/javax/swing/Action.html)：同一个操作对象可以供多个控件使用，并集中管理名称、图标与启用状态。

### 一句话口诀（补充）

> 把要做的事装成命令，交给别人执行 → 命令

---

## 16. 桥接模式 Bridge（结构型）

**核心：把抽象部分与实现部分分离，用组合把它们连接起来，让两边都能独立扩展。**

这里的「抽象部分」指面向业务的高层功能，「实现部分」指它依赖的底层能力，不是简单地把一个类拆成接口和实现类。例如通知系统中，**通知级别决定怎样组织消息，发送渠道决定怎样把消息送出去**。

### ✅ 典型业务场景

- **通知级别 × 发送渠道**
  痛点：普通通知、紧急通知都要支持邮件和短信。如果每个组合建一个类，就会出现 `NormalEmailNotification`、`NormalSmsNotification`、`UrgentEmailNotification`、`UrgentSmsNotification`；新增站内信又要为每种通知各加一个类。
  做法：通知类型依赖统一的发送接口，邮件、短信分别实现这个接口。新增通知类型时复用已有渠道，新增渠道时复用已有通知类型。
- **报表种类 × 输出格式**
  痛点：销售报表、库存报表都要输出 CSV 和 PDF，把取数、报表规则与格式生成写进每个组合类，会重复两边的逻辑。
  做法：报表侧负责业务数据与结构，输出侧负责渲染；用稳定的数据契约连接，前提是不同格式都能表达这份结构。
- **控件类型 × 平台绘制实现**
  痛点：按钮、复选框各自需要多个平台版本，控件交互逻辑和平台绘制逻辑容易重复。
  做法：控件维护高层交互行为，通过绘制接口调用平台实现，让两边分别演化。

### ⚠️ 什么时候不要用

- 只有一个会变化的维度，普通接口、多态或策略已经够用，不必再人为拆出第二套类型。
- 两个维度实际上强耦合，大部分组合都不成立；硬凑统一接口会产生大量特判，应先重新划分职责和能力边界。
- 只是在接入一个不兼容的旧接口，适配器通常更直接。

### ☕ 双语言示例（Java / Go 页签切换）

下面组合「普通 / 紧急通知」和「邮件 / 短信渠道」。四个角色是：**Notification（抽象部分）、NormalNotification / UrgentNotification（扩展抽象）、Sender（实现接口）、EmailSender / SmsSender（具体实现）**。

| 通知类型 | 邮件渠道 | 短信渠道 |
|---|---|---|
| 普通通知 | 普通通知 + EmailSender | 普通通知 + SmsSender |
| 紧急通知 | 紧急通知 + EmailSender | 紧急通知 + SmsSender |

每个格子都是对象组合，不需要单独定义一个类。示例仅打印发送过程，`userId` 表示接收用户；紧急通知用前缀展示不同的消息编排，不包含真实投递、重试或告警升级逻辑。

{{< tabs >}}
{{< tab "Java" >}}
```java
// 实现维度：怎样发送
interface Sender {
    void send(String userId, String content);
}

class EmailSender implements Sender {
    public void send(String userId, String content) {
        System.out.println("[邮件] " + userId + "：" + content);
    }
}

class SmsSender implements Sender {
    public void send(String userId, String content) {
        System.out.println("[短信] " + userId + "：" + content);
    }
}

// 抽象维度：哪种通知；通过持有 Sender 连接发送实现
abstract class Notification {
    protected final Sender sender;

    protected Notification(Sender sender) {
        this.sender = sender;
    }

    public abstract void notifyUser(String userId, String content);
}

class NormalNotification extends Notification {
    public NormalNotification(Sender sender) { super(sender); }

    public void notifyUser(String userId, String content) {
        sender.send(userId, "【普通】" + content);
    }
}

class UrgentNotification extends Notification {
    public UrgentNotification(Sender sender) { super(sender); }

    public void notifyUser(String userId, String content) {
        sender.send(userId, "【紧急】" + content);
    }
}

public class Main {
    public static void main(String[] args) {
        Sender email = new EmailSender();
        Sender sms = new SmsSender();
        Notification[] notifications = {
            new NormalNotification(email),
            new NormalNotification(sms),
            new UrgentNotification(email),
            new UrgentNotification(sms)
        };
        for (Notification notification : notifications) {
            notification.notifyUser("u1001", "服务将在 22:00 维护");
        }
    }
}
```
{{< /tab >}}

{{< tab "Go" >}}
```go
package main

import "fmt"

// 实现维度：怎样发送
type Sender interface {
	Send(userID, content string)
}

type EmailSender struct{}

func (EmailSender) Send(userID, content string) {
	fmt.Printf("[邮件] %s：%s\n", userID, content)
}

type SmsSender struct{}

func (SmsSender) Send(userID, content string) {
	fmt.Printf("[短信] %s：%s\n", userID, content)
}

// 抽象维度：哪种通知；具体通知通过组合持有 Sender
type Notification interface {
	Notify(userID, content string)
}

type NormalNotification struct {
	sender Sender
}

func NewNormalNotification(sender Sender) *NormalNotification {
	return &NormalNotification{sender: sender}
}

func (n *NormalNotification) Notify(userID, content string) {
	n.sender.Send(userID, "【普通】"+content)
}

type UrgentNotification struct {
	sender Sender
}

func NewUrgentNotification(sender Sender) *UrgentNotification {
	return &UrgentNotification{sender: sender}
}

func (n *UrgentNotification) Notify(userID, content string) {
	n.sender.Send(userID, "【紧急】"+content)
}

func main() {
	email, sms := EmailSender{}, SmsSender{}
	notifications := []Notification{
		NewNormalNotification(email),
		NewNormalNotification(sms),
		NewUrgentNotification(email),
		NewUrgentNotification(sms),
	}
	for _, notification := range notifications {
		notification.Notify("u1001", "服务将在 22:00 维护")
	}
}
```
{{< /tab >}}
{{< /tabs >}}

两种语言输出一致：

```text
[邮件] u1001：【普通】服务将在 22:00 维护
[短信] u1001：【普通】服务将在 22:00 维护
[邮件] u1001：【紧急】服务将在 22:00 维护
[短信] u1001：【紧急】服务将在 22:00 维护
```

**连接两边的桥，就是通知对象持有的 `Sender`。** Java 用抽象类保存这条引用，Go 用结构体字段组合发送接口，不需要模拟类继承。高层的 `notifyUser()` / `Notify()` 负责组织通知，再调用底层的 `send()` / `Send()` 完成渠道发送。

接下来增加一个 `InAppSender`（站内信），只需实现 `Sender` 并在组装处注入，普通、紧急通知的代码都不用改。反过来，新增一种通知类型，也能直接复用邮件、短信实现。前提是发送接口足够稳定，并且新能力符合已有契约。

如果有 M 种通知和 N 种渠道，为每个组合建类需要 M × N 个具体组合类；桥接把它们拆成 M 个通知类型和 N 个渠道实现，另加少量接口或基类。**减少的是重复的类型与实现代码，业务上可能出现的 M × N 种组合仍然存在，相应的兼容性验证也不能省略。**

阅读真实 API 时，可以参考高层接口与底层驱动的分层：Java 的 `DriverManager` 会从已注册的 JDBC 驱动中选择合适的驱动建立连接；Go 的 `database/sql/driver` 定义供数据库驱动实现、由 `database/sql` 使用的接口。这有助于理解通过稳定接口连接不同层次，但要判定某段设计是否属于桥接，还需找出两边各自扩展的维度。参见 [DriverManager 官方文档](https://docs.oracle.com/en/java/javase/21/docs/api/java.sql/java/sql/DriverManager.html) 和 [Go 数据库驱动接口](https://pkg.go.dev/database/sql/driver)。

### 一句话口诀（补充）

> 两个维度各自扩展，组合搭桥 → 桥接

---

# 四、8 个第二梯队模式速记区分（原文保留并补充）

- **外观 Facade**：复杂一堆子系统 → 一个入口调用；
- **责任链**：校验 / 审批一条流水线，中途失败就截断；
- **状态 State**：一个对象内部状态流转、自动切换行为（订单状态）；
- **模板方法**：流程骨架固定不变，只有部分步骤子类自定义；
- **备忘录 Memento**：先保存对象状态，需要回退时交给原对象恢复；
- **迭代器 Iterator**：统一取下一个元素，遍历过程不暴露集合内部结构；
- **命令 Command**：把请求封装成对象，方便统一触发、排队或记录操作；
- **桥接 Bridge**：把两个独立变化的维度拆开，通过组合连接起来。

---

# 五、内容审核与补充说明

对照 GoF 经典分类逐条核对过，原稿结论基本正确，这里把几处容易混淆的点明确一下：

1. **分类核对**：单例、简单工厂、建造者 = 创建型；适配器、装饰器、代理、外观、桥接 = 结构型；策略、观察者、责任链、状态、模板方法、备忘录、迭代器、命令 = 行为型。
2. **简单工厂**严格说不在 GoF 23 个经典模式里，它是「工厂方法 / 抽象工厂」的简化教学版本，教程里常把它单列出来讲，本文按原稿保留。
3. **观察者 vs MQ**：进程内观察者默认是同步通知；MQ / Kafka 是「发布-订阅」思想在分布式下的实现，可以异步、削峰，但核心思路一致。
4. **装饰器 vs 代理**：装饰器一定会执行目标对象；代理可能直接拦截不调用真实对象（原稿结论正确）。
5. **适配器 vs 外观**：适配器是「接口翻译」，解决两个接口不兼容；外观是「简化入口」，隐藏内部编排。场景里「接入多个支付 SDK」是适配器，「下单聚合库存/支付/物流」是外观。
6. **模板方法**：Go 版用「接口 + 外部函数」模拟，Java 版用「抽象类 + final 模板方法」表达，语义更严格。
7. **代码语言**：每个模式的代码框都带 **Java / Go 页签**，两者一一对应。前 12 个模式的 Go 代码保留原稿版本；新增 4 个模式提供独立的 Java / Go 示例，可分别运行，Java 示例保存为 `Main.java`，Go 示例保存为 `main.go`。
8. **备忘录**：保存和恢复状态不等于切换状态模式中的行为，也不等于数据库事务回滚；可变状态必须处理快照隔离。
9. **迭代器**：统一遍历接口不代表自动获得懒加载、并发安全或快照一致性，这些取决于具体实现及其契约。
10. **命令**：核心是请求对象化与调用解耦，撤销、持久化、重试都是按需扩展；需要撤销时，可以与备忘录配合。
11. **桥接**：属于结构型模式，重点是抽象与实现两个维度独立扩展；采用组合、依赖接口或能切换实现，本身都不是充分判断条件。
