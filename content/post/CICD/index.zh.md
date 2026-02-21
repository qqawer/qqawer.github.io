---
title: "CICD 学习笔记"
description: "从入门到实践：CICD"
date: 2026-02-02
slug: "cicd-learning-notes"
categories:
    - Documentation
tags:
    - CICD
    - DevSecOps
toc: true
---

# EcoGo 项目 DevSecOps 实践文档

## 1. 总体 DevSecOps 架构
项目采用了经典的 DevSecOps 分层防御策略，将安全左移（Shift Left）到开发的各个阶段：

- **开发阶段 (Code)**：Linting, SAST (静态分析)
- **构建阶段 (Build)**：依赖安全检查, 单元测试
- **测试阶段 (Test)**：质量门禁 (SonarQube)
- **部署阶段 (Deploy)**：基础设施即代码 (IaC) 安全
- **运行阶段 (Run)**：DAST (动态分析), 实时监控

---

## 2. 具体的 CI/CD 与安全实践

### A. 静态应用安全测试 (SAST) - 在代码提交/构建时运行
目标是尽早通过静态分析发现代码中的漏洞。

#### SpotBugs
- 作用：静态扫描 Java 字节码，查找潜在的 Bug 和安全漏洞（如空指针、资源未关闭、SQL 注入风险等）。
- 配置：在 pom.xml 中集成了 spotbugs-maven-plugin，配置了 Max 级别的检查力度。
- 运行：通过 `mvn spotbugs:check` 触发。

#### OWASP Dependency Check
- 作用：扫描项目依赖（第三方 Jar 包），对比 CVE (Common Vulnerabilities and Exposures) 数据库，发现已知漏洞的组件。
- 配置：在 pom.xml 中集成了 dependency-check-maven，设置当 CVSS 评分 >= 5 时构建失败。
- 运行：通过 `mvn dependency-check:check` 触发。

#### Checkstyle (Linting)
- 作用：强制执行代码规范（Google Java Style），虽然主要是质量工具，但规范的代码有助于减少安全隐患。
- 配置：使用 google_checks.xml 配置。

#### SonarQube
- 作用：综合的代码质量管理平台，不仅检查代码味道（Code Smells）和 Bugs，还专门检测 Security Hotspots（安全热点）和 Vulnerabilities（漏洞）。
- 配置：sonar-project.properties 定义了扫描范围，排除测试代码等。

---

### B. 动态应用安全测试 (DAST) - 在应用部署后运行
目标是模拟黑客攻击，对运行中的应用进行动态扫描。

#### OWASP ZAP (Zed Attack Proxy)
- 核心工具：项目使用了 OWASP ZAP 进行 DAST 扫描。
- 配置文件：位于 .zap/ 目录下。
  - zap-config.yaml：定义了扫描上下文。
    - Context: EcoGo-API
    - Target URL: http://localhost:8090
    - Authentication: 配置了自动认证（JSON Based），使用测试账号 test@example.com / test123 登录，这样扫描器可以进入需要鉴权的接口进行深层扫描。
    - Scan Types: 配置了爬虫 (Spider) 爬取链接，以及主动扫描 (Active Scan) 进行攻击模拟。
  - rules.tsv：定义了具体的报警规则和阈值。
    - SQL注入: WARN 级别
    - XSS (跨站脚本): WARN 级别
    - 路径遍历/远程文件包含: WARN 级别
    - CSRF: WARN 级别
    - 信息泄露: INFO 级别
- 运行时机：通常在应用部署到测试环境或临时环境后执行。

---

### C. 基础设施与运维安全
- **Infrastructure as Code (IaC)**：使用 Terraform 管理 AWS 资源，Ansible 管理服务配置，实现了环境的可重复性和一致性，减少人为配置错误导致的安全漏洞。
- **监控 (Monitoring)**：使用 Prometheus 和 Grafana (在 monitoring/ 目录) 监控应用运行状态（错误率、延迟等），这是安全运营（SecOps）的重要组成部分，用于及时发现异常攻击流量或服务不可用情况。

---

## 3. 如何在本地体验安全流程
项目提供了一个便捷脚本 `scripts/local-deploy.sh`，您可以直接在本地运行这些安全检查：

1. 运行 `./scripts/local-deploy.sh`
2. 选项 2: "Run security scans (LINT + SAST)" —— 这会一次性运行 Checkstyle, SpotBugs, 和 Dependency Check。
3. 选项 5: "Full deployment" —— 这会启动应用和监控栈（Grafana/Prometheus），应用启动后，您可以手动运行 ZAP 连接到 localhost:8090 进行 DAST 扫描。

---

## 总结
本项目的 DevSecOps 实践主要体现在：POM 中集成的 Maven 插件 (SAST) 以及可配置的 OWASP ZAP 扫描 (DAST)，并通过 CI/CD 脚本将这些步骤串联起来。
