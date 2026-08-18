---
title: "8 大高频设计模式・Java 版：业务场景 + 痛点 + 代码，一表看懂"
description: "8 大高频设计模式 + 4 个第二梯队模式：典型业务场景、痛点、什么时候不用，全部配上可运行的 Java 示例；开头一张总结表帮你一眼分清 12 个模式。"
date: 2026-08-18T00:00:00+08:00
slug: "java-design-patterns-scenarios"
categories:
    - Programming
tags:
    - Java
    - Design Patterns
    - Architecture
    - 面试
toc: true
---

# 🧩 8 大高频设计模式・Java 版：场景、痛点、代码一表看懂

> 这篇博客整理自一份《8 大高频设计模式・详细业务场景 + 痛点 + 什么时候不用》的笔记，并做了三件事：
>
> 1. **内容审核**：逐个核对了模式归类、场景描述和结论，与经典 GoF 设计模式分类一致，细节核对结果放在文末「内容审核与补充说明」；
> 2. **补充 Java 代码**：原文是 Go 示例，这里为每个模式补上**可直接运行的 Java 版本**，重点展示和 Go 示例一一对应的写法；
> 3. **保留原文**：场景、痛点、口诀一字不删，原版 Go 完整代码放在文末附录，方便对照，想看哪份看哪份。

先看总表，再逐一看细节，最后看「易混模式对照」和「工厂 + 策略组合实战」。

## 📋 开篇总结表：12 个模式一眼看懂

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

### ☕ Java 示例

原版 Go 用 `sync.Once` 保证「只初始化一次」，Java 最接近的等价写法是**双重检查锁（DCL）**：

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

### ☕ Java 示例

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

### ☕ Java 示例

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

### ☕ Java 示例

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

### ☕ Java 示例

原版 Go 用「函数包函数」实现装饰，Java 里对应的是「装饰器类持有原对象、实现同一接口」：

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

### ☕ Java 示例

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

### ☕ Java 示例

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

### ☕ Java 示例

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

## 🚀 工厂 + 策略 组合完整示例（Java）

业务中最常一起搭配使用：**工厂负责创建策略对象，上下文负责使用、切换策略对象**。

思路说明：

- 策略：支付宝、微信支付，属于可互换的支付算法；
- 简单工厂：负责根据类型字符串，生成对应的策略实例；
- 上下文 Context（Order）：持有策略，运行时可以随时更换支付策略；
- 职责拆分：工厂 = 创建策略对象；上下文 = 使用、切换策略对象。

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

# 三、第二梯队 4 个高频模式

## 9. 外观模式 Facade（结构型）

**作用：对外提供一个简单入口，隐藏内部一堆复杂子系统**

**场景：下单入口，内部依次调用库存、支付、物流；上层只调用一个 `createOrder()`，不用关心内部多个子服务。**

### ⚠️ 什么时候不要用（补充）

- 子系统调用关系本来就简单、只有一两个类，加门面属于过度设计；
- 门面不要越做越大变成「上帝类」——它只负责编排入口，不负责塞业务逻辑。

### ☕ Java 示例

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

### 一句话口诀（补充）

> 复杂一堆子系统 → 一个入口调用

---

## 10. 责任链 Chain of Responsibility（行为型）

**作用：一条处理链条，请求依次经过每个处理器，可中断**

**场景：接口校验链路 → 参数校验 → 权限校验 → 限流校验 → 执行业务；审批流（员工 → 主管 → 经理）**

### ⚠️ 什么时候不要用（补充）

- 环节顺序不固定、职责经常增删，链条会很难维护；
- 只有两三个简单 `if` 校验，直接写就行，不需要责任链。

### ☕ Java 示例

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

### ☕ Java 示例

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

### 一句话口诀（补充）

> 一个对象内部状态流转、自动切换行为（订单状态）

---

## 12. 模板方法 Template-Method（行为型）

**作用：父类定义固定流程骨架，子类重写部分步骤实现不同逻辑；流程顺序不可变**

**场景：报表导出，固定流程：加载数据 → 格式化 → 保存文件；导出 Excel 和 PDF 只是格式化步骤不一样。**

### ⚠️ 什么时候不要用（补充）

- 流程本身不固定、经常要调整步骤顺序，模板方法反而束缚；
- 只有一个实现、短期内没有第二个变体，不需要先抽象模板。

### ☕ Java 示例

原版 Go 用「接口 + 外部函数」模拟模板，Java 里更贴切的写法是**抽象类 + final 模板方法**：公共步骤写死在基类，可变步骤留成抽象方法。

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

### 一句话口诀（补充）

> 流程骨架固定不变，只有部分步骤子类自定义

---

# 四、4 个第二梯队模式速记区分（原文保留）

- **外观 Facade**：复杂一堆子系统 → 一个入口调用；
- **责任链**：校验 / 审批一条流水线，中途失败就截断；
- **状态 State**：一个对象内部状态流转、自动切换行为（订单状态）；
- **模板方法**：流程骨架固定不变，只有部分步骤子类自定义。

---

# 五、内容审核与补充说明

对照 GoF 经典分类逐条核对过，原稿结论基本正确，这里把几处容易混淆的点明确一下：

1. **分类核对**：单例、简单工厂、建造者 = 创建型；适配器、装饰器、代理、外观 = 结构型；策略、观察者、责任链、状态、模板方法 = 行为型。
2. **简单工厂**严格说不在 GoF 23 个经典模式里，它是「工厂方法 / 抽象工厂」的简化教学版本，教程里常把它单列出来讲，本文按原稿保留。
3. **观察者 vs MQ**：进程内观察者默认是同步通知；MQ / Kafka 是「发布-订阅」思想在分布式下的实现，可以异步、削峰，但核心思路一致。
4. **装饰器 vs 代理**：装饰器一定会执行目标对象；代理可能直接拦截不调用真实对象（原稿结论正确）。
5. **适配器 vs 外观**：适配器是「接口翻译」，解决两个接口不兼容；外观是「简化入口」，隐藏内部编排。场景里「接入多个支付 SDK」是适配器，「下单聚合库存/支付/物流」是外观。
6. **模板方法**：Go 版用「接口 + 外部函数」模拟，Java 版用「抽象类 + final 模板方法」表达，语义更严格。
7. **代码语言**：正文 Java 示例与原文 Go 示例一一对应；原版 Go 完整代码在下方附录，**未删减**。

---

# 附录：原版 Go 完整代码（保留原文）

> 以下代码全部来自原稿，未做删改，方便对照学习。

## 1. 单例 Singleton

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

## 2. 简单工厂 Simple Factory

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

## 3. 建造者 Builder

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

## 4. 适配器 Adapter

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

## 5. 装饰器 Decorator

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

## 6. 代理 Proxy

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

## 7. 策略 Strategy

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

## 8. 观察者 Observer（发布-订阅）

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

## 9. 外观模式 Facade

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

## 10. 责任链 Chain of Responsibility

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

## 11. 状态模式 State

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

## 12. 模板方法 Template-Method

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

## 附加：工厂 + 策略组合完整示例（Go 原版）

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

运行输出：

```text
支付宝支付：100.00 元
微信支付：200.00 元
```
