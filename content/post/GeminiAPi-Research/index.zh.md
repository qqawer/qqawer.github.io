---
title: "Gemini API 深度调研与实战指南"
description: "全面解析 Gemini API 的核心功能、环境配置及代码实现，包含 Files API 复用、GCS 注册等进阶场景，助你快速上手 Google 最强 AI 模型。"
date: 2026-03-06
slug: "gemini-api-research"
categories:
    - Documentation
tags:
    - Java
    - AI
    - Gemini
    - Go
toc: true
---

# Gemini API 快速入门

## 1. 安装 Google GenAI SDK

在你的模块目录下运行以下命令安装相关的包：

```bash
go get google.golang.org/genai
go get google.golang.org/api
go get golang.org/x/oauth2/google
go get cloud.google.com/go/storage
```

## 2. 环境配置：设置 API Key

客户端在初始化时会自动读取环境变量 `GEMINI_API_KEY`。所有 Gemini API 的官方示例代码都假定你已经设置了该环境变量。

### 临时设置（仅当前终端有效）

```bash
# macOS/Linux (Terminal)
export GEMINI_API_KEY="[ENCRYPTION_KEY]"

# Windows (Command Prompt)
set GEMINI_API_KEY="[ENCRYPTION_KEY]"

# Windows (PowerShell)
$env:GEMINI_API_KEY="[ENCRYPTION_KEY]"
```

### 永久设置（推荐）

```bash
# macOS
nano ~/.zshrc
# 在文件末尾添加：export GEMINI_API_KEY="[ENCRYPTION_KEY]"
source ~/.zshrc

# Linux
# 编辑 ~/.bashrc 文件，在末尾添加：export GEMINI_API_KEY="[ENCRYPTION_KEY]"
source ~/.bashrc

# Windows
# 搜索“编辑系统环境变量” -> 环境变量 -> 新建用户或系统变量：
# 变量名：GEMINI_API_KEY
# 变量值：[ENCRYPTION_KEY]
```

---

## 3. 发送第一个请求

以下示例展示了如何使用 `GenerateContent` 方法调用 Gemini 2.5 Flash 模型发送基础的文本请求。

```go
package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx)
	if err != nil {
		log.Fatal(err)
	}
	defer client.Close()

	model := client.GenerativeModel("gemini-2.5-flash")
	resp, err := model.GenerateContent(ctx, genai.Text("Hello, Gemini! Explain how AI works in a few words"))
	
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(resp.Text)
}
```

---

# 进阶：多媒体文件输入 (File input methods)

Gemini API 的所有接口（包括 Batch, Interactions 和 Live API）都支持多模态输入（PDF、图像、视频等）。你可以从本地读取文件并将其包含在提示中，或者通过 API 上传大文件。

## 一、文件输入方式对比

| 方法 | 适用场景 | 最大文件大小 | 持久化特性 |
|------|----------|---------------|-------------|
| **Inline data（内置数据）** | 快速测试、本地小文件、实时应用 | 单请求/载荷 100 MB<br>（PDF 限制 50 MB） | 无（每次请求都需发送完整数据块） |
| **File API upload（文件上传）** | 大视频、长音频、需多次重复询问的文档 | 单文件 2 GB，<br>每个项目最多 20 GB | 云端保留 48 小时（自动删除），无法下载 |
| **GCS URI 注册** | 已存储在 Google Cloud Storage (GCS) 的大文件 | 单文件 2 GB，总存储看 GCS 桶容量 | 无自身存储限制，单次注册最长 30 天访问权限 |
| **External URLs（外部 URL）** | 公有云存储（AWS/Azure/GCS）的外链、公网公开文件 | 单请求/载荷 100 MB | 无（每次请求由模型端拉取） |

---

## 二、核心实现代码（Go 版本）

以下提供了上述四种场景的**完整独立可运行代码**，包含了所有的包引入和客户端初始化。

### 1. Inline Data（内置数据）- 本地小文件直接上传

最简单的文件输入方法。适用于小文件（PDF ≤ 50MB，其他 ≤ 100MB）。

```go
package main

import (
	"context"
	"fmt"
	"io/ioutil"
	"log"

	"google.golang.org/genai"
	"google.golang.org/api/option"
)

func main() {
	ctx := context.Background()

	// 初始化 Gemini 客户端（自动读取环境变量 GEMINI_API_KEY）
	client, err := genai.NewClient(ctx, option.WithAPIKey(""))
	if err != nil {
		log.Fatalf("创建客户端失败: %v", err)
	}
	defer client.Close()

	// 读取本地 PDF 文件
	filePath := "my_local_file.pdf"
	fileBytes, err := ioutil.ReadFile(filePath)
	if err != nil {
		log.Fatalf("读取文件失败: %v", err)
	}

	model := client.GenerativeModel("gemini-2.5-flash")

	// 构造请求内容（文件二进制数据 + 文本提示）
	contents := []genai.Part{
		genai.Blob("application/pdf", fileBytes), 
		genai.Text("Summarize this document"),    
	}

	// 调用 API
	resp, err := model.GenerateContent(ctx, contents...)
	if err != nil {
		log.Fatalf("调用 API 失败: %v", err)
	}

	printResponse(resp)
}

// 通用结果打印函数
func printResponse(resp *genai.GenerateContentResponse) {
	if len(resp.Candidates) == 0 {
		log.Println("无返回结果")
		return
	}
	for _, cand := range resp.Candidates {
		if cand.Content != nil {
			for _, part := range cand.Content.Parts {
				fmt.Println(part)
			}
		}
	}
	fmt.Println("---")
}
```

### 2. GCS URI 注册 (Google Cloud Storage)

适用于已托管在 GCP 云端的大文件，省去本地下载和重新上传动作。

#### 前置：GCP 命令行权限配置
必须确保 Gemini 服务代理拥有 `Storage Object Viewer` 权限：
```bash
# 1. 创建服务代理
gcloud beta services identity create --service=generativelanguage.googleapis.com --project=<你的项目ID>

# 2. 授予权限
gcloud storage buckets add-iam-policy-binding gs://<你的存储桶> \
  --member="serviceAccount:service-<项目编号>@gcp-sa-generativelanguage.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

#### Go 实现代码
```go
package main

import (
	"context"
	"fmt"
	"log"

	"cloud.google.com/go/storage"
	"golang.org/x/oauth2/google"
	"google.golang.org/api/option"
	"google.golang.org/genai"
)

// 获取 GCS 访问凭证
func getGCSCredentials(ctx context.Context) (*google.Credentials, error) {
	// 场景1：外部环境（本地/非 GCP 服务器）- 使用服务账号 JSON 密钥
	creds, err := google.CredentialsFromJSON(ctx, nil,
		"https://www.googleapis.com/auth/devstorage.read_only",
		"https://www.googleapis.com/auth/cloud-platform",
	)
	if err != nil {
		// 场景2：GCP 内部环境（Cloud Run/Compute Engine）- 使用默认凭证
		creds, err = google.FindDefaultCredentials(ctx,
			"https://www.googleapis.com/auth/devstorage.read_only",
			"https://www.googleapis.com/auth/cloud-platform",
		)
		if err != nil {
			return nil, fmt.Errorf("获取凭证失败: %v", err)
		}
	}
	return creds, nil
}

func main() {
	ctx := context.Background()

	// 1. 获取凭证
	creds, err := getGCSCredentials(ctx)
	if err != nil {
		log.Fatalf("获取凭证失败: %v", err)
	}

	// 2. 初始化客户端（需同时提供 API Key 和 GCS 凭证）
	geminiClient, err := genai.NewClient(ctx, option.WithAPIKey(""), option.WithCredentials(creds))
	if err != nil {
		log.Fatalf("创建客户端失败: %v", err)
	}
	defer geminiClient.Close()

	gcsURIs := []string{"gs://my_bucket/some_object.pdf"}
	model := geminiClient.GenerativeModel("gemini-2.5-flash")
	prompt := "Summarize this file."

	for _, uri := range gcsURIs {
		fmt.Printf("处理文件: %s\n", uri)
		// 从 GCS URI 直接加载文件
		contents := []genai.Part{
			genai.Text(prompt),
			genai.BlobFromURI(uri, "application/pdf"), 
		}

		resp, err := model.GenerateContent(ctx, contents...)
		if err != nil {
			log.Printf("处理文件 %s 失败: %v", uri, err)
			continue
		}
		printResponse(resp)
	}
}

func printResponse(resp *genai.GenerateContentResponse) {
	if len(resp.Candidates) == 0 {
		return
	}
	for _, cand := range resp.Candidates {
		if cand.Content != nil {
			for _, part := range cand.Content.Parts {
				fmt.Println(part)
			}
		}
	}
}
```

### 3. External HTTP / Signed URLs

适用于公有可访问的 HTTPS URL 或预签名 URL（支持 S3/Azure SAS），文件大小 ≤ 100MB。
*(注意：Gemini 2.0 系列模型可能暂不支持外链抓取，本例默认使用 1.5 验证)*

```go
package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/genai"
	"google.golang.org/api/option"
)

func main() {
	ctx := context.Background()

	client, err := genai.NewClient(ctx, option.WithAPIKey(""))
	if err != nil {
		log.Fatalf("创建客户端失败: %v", err)
	}
	defer client.Close()

	externalURI := "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf"
	
	// 使用推荐稳定版处理外链
	model := client.GenerativeModel("gemini-1.5-flash")

	contents := []genai.Part{
		genai.BlobFromURI(externalURI, "application/pdf"), 
		genai.Text("Summarize this external file"),
	}

	resp, err := model.GenerateContent(ctx, contents...)
	if err != nil {
		log.Fatalf("调用 API 失败: %v", err)
	}

	printResponse(resp)
}

func printResponse(resp *genai.GenerateContentResponse) {
	if len(resp.Candidates) == 0 {
		log.Println("无返回结果")
		return
	}
	for _, cand := range resp.Candidates {
		if cand.Content != nil {
			for _, part := range cand.Content.Parts {
				fmt.Println(part)
			}
		}
	}
}
```

---

## 三、Gemini Files API 深度应用与复用逻辑

当你的请求**超过 100 MB**，或者 PDF 文件**大于 50 MB** 时，必须使用 **Files API**。
复用的核心优势是：**上传 1 次文件拿到唯一的 File ID，在 48 小时内可以多次用这个 ID 调用 API，不用重复传输巨大的文件体。**

### Files API 基础操作片段

```go
// 上传文件并返回 File 对象
file, err := client.Files.UploadFromPath(ctx, "path/to/sample.mp3", nil)

// 获取文件元数据
gotFile, err := client.Files.Get(ctx, file.Name)

// 遍历列出项目中所有上传的文件
for fileData, err := range client.Files.All(ctx) {
  fmt.Println(fileData.Name)
}

// 主动删除文件
client.Files.Delete(ctx, file.Name)
```

### 实战：一次性上传多个 PDF，分别调用（最常用）

这个场景适合批量上传一批发票或合同，然后针对每一个独立发送解析指令。

```go
package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/genai"
	"google.golang.org/api/option"
)

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, option.WithAPIKey(""))
	if err != nil {
		log.Fatalf("创建客户端失败: %v", err)
	}
	defer client.Close()

	// 1. 定义要上传的多个 PDF
	pdfFiles := []string{"docs/invoice1.pdf", "docs/contract2.pdf"}
	fileIDs := make(map[string]string) // 存储 文件名 -> File ID

	// 2. 上传文件并保存 ID
	for _, filePath := range pdfFiles {
		file, err := client.Files.UploadFromPath(ctx, filePath, nil)
		if err != nil {
			log.Printf("上传失败 %s: %v", filePath, err)
			continue
		}
		fileIDs[filePath] = file.Name
		fmt.Printf("文件 %s 成功，File ID: %s\n", filePath, file.Name)
		// 演示中暂不延迟删除，以便复用
	}

	// 3. 第一次调用：利用保存的 File ID 请求
	fmt.Println("\n=== 第一次调用（解析文件）===")
	for filePath, fileID := range fileIDs {
		content := &genai.Content{
			Parts: []*genai.Part{
				genai.NewPartFromFile(genai.File{Name: fileID}), // 用 ID 引用
				genai.NewPartFromText("提取 PDF 中的关键信息，输出 JSON 格式"),
			},
		}

		resp, err := client.Models.GenerateContent(ctx, "gemini-2.5-flash", []*genai.Content{content}, nil)
		if err != nil {
			log.Printf("解析失败: %v", err)
			continue
		}
		fmt.Printf("解析结果: %s\n", filePath)
		printResponse(resp)
	}

	// 4. 第二次调用：复用同一个 File ID，更换提示词
	fmt.Println("\n=== 第二次调用（复用 File ID换提示语）===")
	for filePath, fileID := range fileIDs {
		content := &genai.Content{
			Parts: []*genai.Part{
				genai.NewPartFromFile(genai.File{Name: fileID}), // 再次用 ID 引用，无需重传
				genai.NewPartFromText("总结核心内容，200字以内"),
			},
		}
		resp, err := client.Models.GenerateContent(ctx, "gemini-2.5-flash", []*genai.Content{content}, nil)
		if err != nil {
			continue
		}
		printResponse(resp)
	}

	// 5. 最终清理
	for _, fileID := range fileIDs {
		client.Files.Delete(ctx, fileID)
	}
}

func printResponse(resp *genai.GenerateContentResponse) {
	for _, cand := range resp.Candidates {
		if cand.Content != nil {
			for _, part := range cand.Content.Parts {
				fmt.Println(part)
			}
		}
	}
}
```

### 实战：一次性上传多个 PDF，合并调用（关联分析）

这个场景下，我们将几个文件的 File ID 同时扔给模型，让其进行逻辑对比。

```go
package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/genai"
	"google.golang.org/api/option"
)

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, option.WithAPIKey(""))
	if err != nil {
		log.Fatalf("创建客户端失败: %v", err)
	}
	defer client.Close()

	// 1. 上传多个相关文件
	pdfPaths := []string{"docs/file1.pdf", "docs/file2.pdf"}
	var uploadedFiles []genai.File

	for _, path := range pdfPaths {
		file, err := client.Files.UploadFromPath(ctx, path, nil)
		if err != nil {
			log.Fatalf("上传文件失败: %v", err)
		}
		uploadedFiles = append(uploadedFiles, *file)
		defer client.Files.Delete(ctx, file.Name) // 程序结束后删除
	}

	// 2. 构造多文件请求
	var parts []*genai.Part
	for _, file := range uploadedFiles {
		parts = append(parts, genai.NewPartFromFile(file))
	}
	parts = append(parts, genai.NewPartFromText("对比这两份 PDF，找出异同点，输出 markdown。"))

	// 3. 单次统一请求
	resp, err := client.Models.GenerateContent(ctx, "gemini-2.5-flash", []*genai.Content{{Parts: parts}}, nil)
	if err != nil {
		log.Fatalf("调用对比 API 失败: %v", err)
	}

	fmt.Println("多文件对比结果:")
	printResponse(resp)
}

func printResponse(resp *genai.GenerateContentResponse) {
	for _, cand := range resp.Candidates {
		if cand.Content != nil {
			for _, part := range cand.Content.Parts {
				fmt.Println(part)
			}
		}
	}
}
```

---

## 四、Prompting 工程与注意事项

### 编写多模态提示词的原则 (Prompt fundamentals)
- **明确且具体**：不要含糊，清楚地告诉模型步骤。
- **添加示例 (Few-shot)**：给出你期望的答案。
- **指定输出格式**：比如 markdown, JSON, HTML。
- **图像优先**：如果提示词包含图片或图表数据，在 `[]genai.Part` 中尽量先传图片 `Blob`，再传文字提示 `Text`。

### 故障排除最佳实践 (Troubleshooting)
1. **模型抓错了重点（区域）**：在文字提示中具体指出“请关注表格的右上角数据”。
2. **输出过于宽泛表面**：分两步走，要求模型“先描述图片的细节特征”，然后再“根据上述发现回答我的问题”。
3. **幻觉与死循环控制**：
   - 提取严谨数据（如发票金额）：降低 `Temperature`，或者使用结构化 JSON。
   - 一般场景由于太严格导致模型卡死：尝试将 `Temperature` 回调到默认值 `1.0`。
4. **单次提交流程**：Files API 虽然能传很多文件，但是对于普通的问答，一次请求最好控制在 5 个相关文档内，避免模型遗忘最初的上下文。
