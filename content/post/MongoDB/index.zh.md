---
title: "MongoDB教学"
description: "从入门到实践：MongoDB 核心概念、镜像操作与常用命令详解"
date: 2026-02-03
slug: "mongodb-teaching"
image: "helena-hertz-wWZzXlDpMog-unsplash.jpg"
categories:
    - Documentation
tags:
    - MongoDB
    - Java
toc: true
---


# MongoDB 从入门到实战：EcoGo 项目核心操作指南
## 一、前言
本文以 EcoGo 环保出行项目为实战背景，系统讲解 MongoDB 数据库的核心操作（增删改查），涵盖 Docker 环境下的 MongoDB 操作、集合创建、数据操作语法及 Java 业务层集成，适合 MongoDB 新手快速上手并落地到实际项目中。

## 二、前置准备：Docker 操作 MongoDB
### 2.1 查看运行中的 MongoDB 容器
```bash
sudo docker ps | grep mongodb
```
**作用**：筛选出名称/包含 "mongodb" 的运行容器，确认 MongoDB 服务是否正常启动。

### 2.2 进入 MongoDB 终端
```bash
sudo docker exec -it mongodb mongosh
```
- `exec -it`：以交互模式进入容器
- `mongodb`：容器名称（需与实际容器名一致）
- `mongosh`：MongoDB 5.0+ 推荐的终端工具（替代旧版 `mongo`）

### 2.3 基础数据库操作
```js
// 查看所有数据库
show dbs;

// 切换/创建数据库（不存在则自动创建）
use EcoGo;

// 删除当前数据库（谨慎操作）
db.dropDatabase();

// 语法：db.集合名.drop()
db.chat_records.drop(); // 删除chat_records集合

// 退出终端
exit;
```

## 三、集合创建：EcoGo 项目核心集合设计
集合（Collection）是 MongoDB 存储文档的容器，类似关系型数据库的表。针对 EcoGo 项目的业务场景，创建以下核心集合：
```js
// 切换到EcoGo数据库
use EcoGo;

// 1. 用户核心集合
db.createCollection("users");
// 2. 行程集合
db.createCollection("trips");
// 3. 交通方式字典集合
db.createCollection("transport_modes_dict");
// 4. 积分日志集合
db.createCollection("user_points_logs");
// 5. 徽章模板集合
db.createCollection("badges");
// 6. 用户徽章关联集合
db.createCollection("user_badges");
// 7. 广告集合
db.createCollection("advertisements");
// 8. 订单集合
db.createCollection("orders");
// 9. 交易记录集合
db.createCollection("transactions");
// 10. 聊天记录集合
db.createCollection("chat_records");
// 11. 路线推荐集合
db.createCollection("route_recommendations");
// 12. 排行榜集合
db.createCollection("leaderboard");
// 13. 商品集合
db.createCollection("goods");
// 14. 统计面板集合
db.createCollection("dashboard_stats");
// 15. 用户流失风险集合
db.createCollection("user_churn_risk");

// 验证创建结果
show collections;
```

## 四、核心操作：MongoDB 增删改查（CRUD）
以 `users` 集合为例，讲解 MongoDB 最常用的 CRUD 操作，语法通用可迁移到其他集合。

### 4.1 新增数据（Create）
MongoDB 插入数据无需提前定义字段结构，支持单条/批量插入，字段可灵活增减。

#### 4.1.1 插入单条用户数据（常用）
```js
db.users.insertOne({
  "id": "8f2e4a0d-7b1c-4f9a-9d2e-1a3b5c7d9f0e", // 业务主键（UUID）
  "userid": "123456",
  "phone": "13800001234",
  "password": "$2a$10$EixZaYbB.rK4fl8x2q6s8u5Gf7K4Q6e7R8T9U0V1W2X3Y4Z5", // bcrypt加密密码
  "nickname": "环保小达人",
  "isAdmin": false,
  "vip": { 
    "is_active": false, 
    "expiry_date": ISODate("2026-05-01T23:59:59Z") 
  },
  "total_carbon": 1250, // 累计碳减排量
  "created_at": ISODate("2026-01-01T00:00:00Z")
});
```
**成功输出**：
```js
{ "acknowledged": true, "insertedId": ObjectId("65e4b7891234567890abcdef") }
```

#### 4.1.2 批量插入多条用户数据
```js
db.users.insertMany([
  {
    "id": "1a2b3c4d-5e6f-7890-abcd-1234567890ab",
    "userid": "654321",
    "phone": "13900001234",
    "nickname": "绿色出行者",
    "isAdmin": false,
    "total_carbon": 980,
    "created_at": ISODate("2026-01-02T00:00:00Z")
  },
  {
    "id": "9d8c7b6a-5e4f-3210-ba98-76543210fedc",
    "userid": "789012",
    "phone": "13700001234",
    "nickname": "低碳先锋",
    "isAdmin": true, // 管理员用户
    "total_carbon": 2500,
    "created_at": ISODate("2026-01-03T00:00:00Z")
  }
]);
```
**成功输出**：
```js
{ 
  "acknowledged": true, 
  "insertedIds": { 
    "0": ObjectId("65e4b7901234567890abcdef"), 
    "1": ObjectId("65e4b7911234567890abcdef") 
  } 
}
```

### 4.2 查询数据（Read）
查询是最常用的操作，`find()` 支持条件筛选、字段投影、分页等功能。

#### 4.2.1 基础查询语法
```js
// 1. 查询所有用户（返回全部字段）
db.users.find();

// 2. 查询所有用户，仅显示昵称和碳减排量（隐藏 _id 字段）
db.users.find({}, { "nickname": 1, "total_carbon": 1, "_id": 0 });

// 3. 按条件查询（VIP 激活的用户）
db.users.find({ "vip.is_active": true });

// 4. 复杂条件查询（管理员且碳减排量>2000）
db.users.find(
  { "isAdmin": true, "total_carbon": { $gt: 2000 } }, // $gt = 大于
  { "nickname": 1, "id": 1, "_id": 0 } // 仅返回指定字段
);

// 5. 分页查询（跳过前1条，取2条）
db.users.find().skip(1).limit(2);
```

#### 4.2.2 实战场景：查询用户行程后的数据校验
```js
// 场景：用户完成行程后，查询该用户当前积分和碳减排量
db.users.find(
  { "phone": "13800001234" }, 
  { "current_points": 1, "total_carbon": 1, "_id": 0 }
);
```

### 4.3 更新数据（Update）
更新使用 `updateOne()`（单条）/ `updateMany()`（批量），核心是通过**更新操作符**定义修改逻辑。

#### 4.3.1 常用更新操作符
| 操作符         | 作用                  | 示例                                  |
|----------------|-----------------------|---------------------------------------|
| `$set`         | 修改/新增字段         | `$set: { "nickname": "新昵称" }`      |
| `$inc`         | 数值增减（+/-）       | `$inc: { "total_carbon": 100 }`       |
| `$mul`         | 数值乘法              | `$mul: { "current_points": 1.5 }`     |
| `$unset`       | 删除字段              | `$unset: { "email": "" }`             |
| `$currentDate` | 设置为当前时间        | `$currentDate: { "updated_at": true }`|

#### 4.3.2 单条数据更新（实战场景）
```js
// 场景：用户完成行程后，更新碳减排量、积分和最后更新时间
db.users.updateOne(
  { "id": "1a2b3c4d-5e6f-7890-abcd-1234567890ab" }, // 定位用户（业务主键）
  {
    $inc: {
      "total_carbon": 85, // 本次行程减排85g
      "total_points": 25, // 累计积分+25
      "current_points": 25 // 可用积分+25
    },
    $set: { "last_login_at": ISODate() },
    $currentDate: { "updated_at": true }
  }
);
```
**成功输出**：
```js
{ "acknowledged": true, "matchedCount": 1, "modifiedCount": 1 }
```
- `matchedCount`：匹配到的条数
- `modifiedCount`：实际修改的条数

#### 4.3.3 批量数据更新
```js
// 场景：给所有管理员用户的积分翻倍
db.users.updateMany(
  { "isAdmin": true }, 
  { $mul: { "current_points": 2 } }
);
```

### 4.4 删除数据（Delete）
删除使用 `deleteOne()`（单条）/ `deleteMany()`（批量），**必须加查询条件**（否则会删除整个集合！）。

#### 4.4.1 单条数据删除（推荐）
```js
// 按业务主键删除（避免误删）
db.users.deleteOne({ "id": "8f2e4a0d-7b1c-4f9a-9d2e-1a3b5c7d9f0e" });

// 或按唯一字段（手机号）删除
db.users.deleteOne({ "phone": "13800001234" });
```
**成功输出**：`{ "acknowledged": true, "deletedCount": 1 }`

#### 4.4.1.2 删除字段
```js
// 单文档删除字段
db.集合名.updateOne(
  { 查询条件 }, // 定位要修改的文档
  { $unset: { "要删除的字段名": "" } } // 字段值可填任意（通常用空字符串）
);

// 多文档删除字段
db.集合名.updateMany(
  { 查询条件 }, // 筛选要修改的所有文档
  { $unset: { "要删除的字段名": "" } }
);

// 删除该用户的share_location字段
db.users.updateOne(
  { "phone": "13800001234" }, // 定位唯一用户
  { $unset: { "preferences.share_location": "" } } // 删除嵌套字段
);


// 场景：删除用户邮箱字段
db.users.updateMany(
  {}, // 空条件表示匹配所有文档/行（谨慎使用！）
  { $unset: { "email": "" } }
);
```
**成功输出**：`{ "acknowledged": true, "matchedCount": 1, "modifiedCount": 1 }`
- matchedCount=1：匹配到 1 个用户文档；
- modifiedCount=1：成功删除该字段。



#### 4.4.2 批量数据删除
```js
// 场景：删除非管理员且碳减排量<1000的用户（清理低活跃用户）
db.users.deleteMany({
  "isAdmin": false,
  "total_carbon": { $lt: 1000 } // $lt = 小于
});
```

#### 4.4.3 危险提醒
```js
db.users.deleteMany({}); // 无条件删除！会清空整个users集合，严禁操作！
```

## 五、实战集成：Java 业务层操作 MongoDB
以 EcoGo 项目的用户查询功能为例，展示 Spring Boot 中如何集成 MongoDB（基于 Spring Data MongoDB）。

### 5.1 核心代码实现
```java
package com.example.EcoGo.service;

import com.example.EcoGo.dto.UserResponseDto;
import com.example.EcoGo.exception.BusinessException;
import com.example.EcoGo.exception.errorcode.ErrorCode;
import com.example.EcoGo.interfacemethods.UserInterface;
import com.example.EcoGo.model.User;
import com.example.EcoGo.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * EcoGo用户服务实现类
 * 封装MongoDB用户查询逻辑，适配业务层调用
 */
@Service
@Transactional
public class UserImplementation implements UserInterface {

    @Autowired
    private UserRepository userRepository; // Spring Data MongoDB 仓库

    /**
     * 根据用户名查询用户信息（返回DTO，隐藏敏感字段）
     * @param username 用户名
     * @return 用户响应DTO
     */
    public UserResponseDto getUserByUsername(String username) {
        // 1. 调用Repository查询MongoDB中的用户
        User user = userRepository.findByUsername(username);

        // 2. 空值校验：用户不存在则抛出业务异常
        if (user == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        // 3. Model转DTO（解耦数据库模型和前端响应）
        UserResponseDto userDTO = new UserResponseDto();
        userDTO.setUsername(user.getUsername());
        userDTO.setEmail(user.getEmail());
        userDTO.setNickname(user.getNickname());
        userDTO.setTotalCarbon(user.getTotalCarbon()); // 碳减排量

        return userDTO;
    }
}
```

### 5.2 代码说明
1. **Repository 层**：`UserRepository` 继承 `MongoRepository`，无需手写 SQL/查询语句，通过方法名自动生成 MongoDB 查询（如 `findByUsername`）。
2. **DTO 转换**：返回 `UserResponseDto` 而非数据库实体 `User`，避免暴露密码、管理员标识等敏感字段。
3. **异常处理**：自定义 `BusinessException` 统一处理“用户不存在”等业务异常，提升接口友好性。

## 六、总结
1. MongoDB 是文档型数据库，无需提前定义表结构，适合字段灵活的业务场景（如 EcoGo 的用户个性化数据）。
2. 核心操作：`insertOne/insertMany`（增）、`find`（查）、`updateOne/updateMany`（改）、`deleteOne/deleteMany`（删），操作时需注意条件筛选避免误操作。
3. 项目集成：Spring Boot 中通过 `Spring Data MongoDB` 简化操作，结合 DTO 模式解耦数据库层和业务层，提升代码可维护性。
4. 安全规范：删除/更新操作必须加条件，密码等敏感数据需加密存储（如 bcrypt），避免明文暴露。