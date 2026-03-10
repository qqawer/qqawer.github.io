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
# Gemini API 深度调研与实战指南

## 一、Gemini API 快速入门

### 1. 安装 Google GenAI SDK

在你的模块目录下运行以下命令安装相关的包：

```bash
go get google.golang.org/genai
go get google.golang.org/api
go get golang.org/x/oauth2/google
go get cloud.google.com/go/storage
```

### 2. 环境配置：设置 API Key

客户端在初始化时会自动读取环境变量 `GEMINI_API_KEY`。所有 Gemini API 的官方示例代码都假定你已经设置了该环境变量。

#### 临时设置（仅当前终端有效）

```bash
# macOS/Linux (Terminal)
export GEMINI_API_KEY="[ENCRYPTION_KEY]"

# Windows (Command Prompt)
set GEMINI_API_KEY="[ENCRYPTION_KEY]"

# Windows (PowerShell)
$env:GEMINI_API_KEY="[ENCRYPTION_KEY]"
```

#### 永久设置（推荐）

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

### 3. 发送第一个请求

以下示例展示了如何使用 `GenerateContent` 方法调用 Gemini 2.5 Flash 模型发送基础的文本请求。

{{< tabs >}}
{{< tab "Go" >}}
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
    /*
    result, err := client.Models.GenerateContent(
        ctx,
        "gemini-3-flash-preview",
        genai.Text("Explain how AI works in a few words"),
        nil,
    )
    */
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(resp.Text)
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.GenerateContentResponse;

public class Main {
    public static void main(String[] args) throws Exception {
        // 自动读取 GEMINI_API_KEY 环境变量
        Client client = new Client();

        GenerateContentResponse response = client.models.generateContent(
            "gemini-2.5-flash",
            "Hello, Gemini! Explain how AI works in a few words",
            null
        );
        System.out.println(response.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

---

## 二、File Input Methods（多媒体文件输入）

Gemini API 的所有接口（包括 Batch, Interactions 和 Live API）都支持多模态输入（PDF、图像、视频等）。你可以从本地读取文件并将其包含在提示中，或者通过 API 上传大文件。

### 一、文件输入方式对比

| 方法 | 适用场景 | 最大文件大小 | 持久化特性 |
|------|----------|---------------|-------------|
| **Inline data（内置数据）** | 快速测试、本地小文件、实时应用 | 单请求/载荷 100 MB<br>（PDF 限制 50 MB） | 无（每次请求都需发送完整数据块） |
| **File API upload（文件上传）** | 大视频、长音频、需多次重复询问的文档 | 单文件 2 GB，<br>每个项目最多 20 GB | 云端保留 48 小时（自动删除），无法下载 |
| **GCS URI 注册** | 已存储在 Google Cloud Storage (GCS) 的大文件 | 单文件 2 GB，总存储看 GCS 桶容量 | 无自身存储限制，单次注册最长 30 天访问权限 |
| **External URLs（外部 URL）** | 公有云存储（AWS/Azure/GCS）的外链、公网公开文件 | 单请求/载荷 100 MB | 无（每次请求由模型端拉取） |

---

### 二、核心实现代码（Go 版本）

以下提供了上述四种场景的**完整独立可运行代码**，包含了所有的包引入和客户端初始化。

#### 1. Inline Data（内置数据）- 本地小文件直接上传

最简单的文件输入方法。适用于小文件（PDF ≤ 50MB，其他 ≤ 100MB）。

{{< tabs >}}
{{< tab "Go" >}}
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
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        // 初始化客户端（自动读取 GEMINI_API_KEY 环境变量）
        Client client = new Client();

        // 读取本地 PDF 文件
        byte[] fileBytes = Files.readAllBytes(Paths.get("my_local_file.pdf"));

        // 构造请求内容（文件二进制数据 + 文本提示）
        List<Part> parts = List.of(
            Part.fromBytes(fileBytes, "application/pdf"),
            Part.fromText("Summarize this document")
        );
        Content content = Content.fromParts(parts, "user");

        // 调用 API
        GenerateContentResponse response = client.models.generateContent(
            "gemini-2.5-flash",
            List.of(content),
            null
        );
        System.out.println(response.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 2. GCS URI 注册 (Google Cloud Storage)

适用于已托管在 GCP 云端的大文件，省去本地下载和重新上传动作。

##### 前置：GCP 命令行权限配置
必须确保 Gemini 服务代理拥有 `Storage Object Viewer` 权限：
```bash
# 1. 创建服务代理
gcloud beta services identity create --service=generativelanguage.googleapis.com --project=<你的项目ID>

# 2. 授予权限
gcloud storage buckets add-iam-policy-binding gs://<你的存储桶> \
  --member="serviceAccount:service-<项目编号>@gcp-sa-generativelanguage.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

##### Go 实现代码
{{< tabs >}}
{{< tab "Go" >}}
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
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        // 初始化客户端（自动读取 GEMINI_API_KEY 和应用默认凭证）
        Client client = new Client();

        String[] gcsURIs = {"gs://my_bucket/some_object.pdf"};
        String prompt = "Summarize this file.";

        for (String uri : gcsURIs) {
            System.out.println("处理文件: " + uri);
            // 从 GCS URI 直接加载文件
            List<Part> parts = List.of(
                Part.fromText(prompt),
                Part.fromUri(uri, "application/pdf")
            );
            Content content = Content.fromParts(parts, "user");

            GenerateContentResponse response = client.models.generateContent(
                "gemini-2.5-flash",
                List.of(content),
                null
            );
            System.out.println(response.text());
        }
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 3. External HTTP / Signed URLs

适用于公有可访问的 HTTPS URL 或预签名 URL（支持 S3/Azure SAS），文件大小 ≤ 100MB。
*(注意：Gemini 2.0 系列模型可能暂不支持外链抓取，本例默认使用 1.5 验证)*

{{< tabs >}}
{{< tab "Go" >}}
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
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        String externalUri = "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf";

        // 使用推荐稳定版处理外链
        List<Part> parts = List.of(
            Part.fromUri(externalUri, "application/pdf"),
            Part.fromText("Summarize this external file")
        );
        Content content = Content.fromParts(parts, "user");

        GenerateContentResponse response = client.models.generateContent(
            "gemini-1.5-flash",
            List.of(content),
            null
        );
        System.out.println(response.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

---

### 三、Gemini Files API 深度应用与复用逻辑

当你的请求**超过 100 MB**，或者 PDF 文件**大于 50 MB** 时，必须使用 **Files API**。
复用的核心优势是：**上传 1 次文件拿到唯一的 File ID，在 48 小时内可以多次用这个 ID 调用 API，不用重复传输巨大的文件体。**

#### Files API 基础操作片段

{{< tabs >}}
{{< tab "Go" >}}
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
{{< /tab >}}

{{< tab "Java" >}}
```java
// 上传文件并返回 File 对象
File file = client.files.upload(Paths.get("path/to/sample.mp3"), null);

// 获取文件元数据
File gotFile = client.files.get(file.name());

// 遍历列出项目中所有上传的文件
for (File fileData : client.files.list(null)) {
    System.out.println(fileData.name());
}

// 主动删除文件
client.files.delete(file.name());
```
{{< /tab >}}
{{< /tabs >}}

#### 实战：一次性上传多个 PDF，分别调用（最常用）

这个场景适合批量上传一批发票或合同，然后针对每一个独立发送解析指令。

{{< tabs >}}
{{< tab "Go" >}}
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
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.nio.file.Paths;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        // 1. 定义要上传的多个 PDF
        String[] pdfFiles = {"docs/invoice1.pdf", "docs/contract2.pdf"};
        Map<String, File> uploadedFiles = new LinkedHashMap<>();

        // 2. 上传文件并保存
        for (String filePath : pdfFiles) {
            File uploaded = client.files.upload(Paths.get(filePath), null);
            uploadedFiles.put(filePath, uploaded);
            System.out.printf("文件 %s 上传成功，File ID: %s%n", filePath, uploaded.name());
        }

        // 3. 第一次调用：利用保存的 File URI 请求
        System.out.println("
=== 第一次调用（解析文件）===");
        for (Map.Entry<String, File> entry : uploadedFiles.entrySet()) {
            File f = entry.getValue();
            List<Part> parts = List.of(
                Part.fromUri(f.uri(), f.mimeType()),
                Part.fromText("提取 PDF 中的关键信息，输出 JSON 格式")
            );
            GenerateContentResponse resp = client.models.generateContent(
                "gemini-2.5-flash",
                List.of(Content.fromParts(parts, "user")),
                null
            );
            System.out.println("解析结果: " + entry.getKey());
            System.out.println(resp.text());
        }

        // 4. 第二次调用：复用同一个 File URI，更换提示词
        System.out.println("
=== 第二次调用（复用 File URI 换提示语）===");
        for (Map.Entry<String, File> entry : uploadedFiles.entrySet()) {
            File f = entry.getValue();
            List<Part> parts = List.of(
                Part.fromUri(f.uri(), f.mimeType()),
                Part.fromText("总结核心内容，200字以内")
            );
            GenerateContentResponse resp = client.models.generateContent(
                "gemini-2.5-flash",
                List.of(Content.fromParts(parts, "user")),
                null
            );
            System.out.println(resp.text());
        }

        // 5. 最终清理
        for (File f : uploadedFiles.values()) {
            client.files.delete(f.name());
        }
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 实战：一次性上传多个 PDF，合并调用（关联分析）

这个场景下，我们将几个文件的 File ID 同时扔给模型，让其进行逻辑对比。

{{< tabs >}}
{{< tab "Go" >}}
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
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.nio.file.Paths;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        // 1. 上传多个相关文件
        String[] pdfPaths = {"docs/file1.pdf", "docs/file2.pdf"};
        List<File> uploadedFiles = new ArrayList<>();

        for (String path : pdfPaths) {
            File uploaded = client.files.upload(Paths.get(path), null);
            uploadedFiles.add(uploaded);
        }

        // 2. 构造多文件请求
        List<Part> parts = new ArrayList<>();
        for (File f : uploadedFiles) {
            parts.add(Part.fromUri(f.uri(), f.mimeType()));
        }
        parts.add(Part.fromText("对比这两份 PDF，找出异同点，输出 markdown。"));

        // 3. 单次统一请求
        GenerateContentResponse response = client.models.generateContent(
            "gemini-2.5-flash",
            List.of(Content.fromParts(parts, "user")),
            null
        );
        System.out.println("多文件对比结果:");
        System.out.println(response.text());

        // 清理
        for (File f : uploadedFiles) {
            client.files.delete(f.name());
        }
    }
}
```
{{< /tab >}}
{{< /tabs >}}

---

### 四、Prompting 工程与注意事项

#### 编写多模态提示词的原则 (Prompt fundamentals)
- **明确且具体**：不要含糊，清楚地告诉模型步骤。
- **添加示例 (Few-shot)**：给出你期望的答案。
- **指定输出格式**：比如 markdown, JSON, HTML。
- **图像优先**：如果提示词包含图片或图表数据，在 `[]genai.Part` 中尽量先传图片 `Blob`，再传文字提示 `Text`。

#### 故障排除最佳实践 (Troubleshooting)
1. **模型抓错了重点（区域）**：在文字提示中具体指出“请关注表格的右上角数据”。
2. **输出过于宽泛表面**：分两步走，要求模型“先描述图片的细节特征”，然后再“根据上述发现回答我的问题”。
3. **幻觉与死循环控制**：
   - 提取严谨数据（如发票金额）：降低 `Temperature`，或者使用结构化 JSON。
   - 一般场景由于太严格导致模型卡死：尝试将 `Temperature` 回调到默认值 `1.0`。
4. **单次提交流程**：Files API 虽然能传很多文件，但是对于普通的问答，一次请求最好控制在 5 个相关文档内，避免模型遗忘最初的上下文。

---

## 三、Context Caching（上下文缓存）

在典型的 AI 工作流中，你可能会反复向模型传递相同的庞大背景知识。Gemini API 提供了两种缓存机制来帮助降低成本：

### 1. 隐式缓存（Implicit Caching / 自动）

隐式缓存默认开启。如果你在短时间内发送了包含相似大段前缀提示的请求，系统会自动对其进行缓存，并将节省的成本返还给你。
- **成本节省**：自动生效，但不保证每次都能命中。
- **最低 Token 阈值**：
  - `gemini-2.5-flash` / `gemini-3-flash-preview`：**1024 tokens**
  - `gemini-2.5-pro` / `gemini-3.1-pro-preview`：**4096 tokens**
- **如何验证命中**：你可以在响应对象的 `usage_metadata` 字段中查看命中缓存的 token 数量。

### 2. 显式缓存（Explicit Caching / 手动）

显式缓存允许你手动为一组 token 创建带有生效时间 (TTL，默认 1 小时) 的缓存对象。在需要重复传入大量相同背景内容的场景下，这能稳定保证更低的成本。

#### 适用场景：
- 带有海量 System Instructions (系统指令) 的聊天机器人。
- 对同一个长视频、长音频或超大 PDF 文件进行反复的多轮提问分析。
- 多次分析同一个庞大的代码仓库。

#### 实战代码：Go 语言中的显式缓存

以下代码演示了如何显式地创建和调用缓存。请特别注意代码注释中标出的**缓存核心逻辑**位置。

{{< tabs >}}
{{< tab "Go" >}}
```go
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"google.golang.org/genai"
	"google.golang.org/api/option"
)

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, option.WithAPIKey(""))
	if err != nil { log.Fatal(err) }
	defer client.Close()

	modelName := "gemini-2.5-flash"
	
	// 1. 常规上传大文件 (使用 Files API)
	document, err := client.Files.UploadFromPath(ctx, "docs/large_transcript.txt", nil)
	if err != nil { log.Fatal(err) }

	parts := []*genai.Part{ genai.NewPartFromURI(document.URI, document.MIMEType) }
	contents := []*genai.Content{ genai.NewContentFromParts(parts, genai.RoleUser) }

	// =====================================================================
	// 2. 创建缓存 (⚠️ 缓存动作在此发生)
	// 在这里我们不直接调用 GenerateContent，而是创建一个 Cache 对象。
	// 我们将刚刚上传的文件以及系统提示词绑定到这个缓存对象上。
	// =====================================================================
	cache, err := client.Caches.Create(ctx, modelName, &genai.CreateCachedContentConfig{
		Contents: contents,
		SystemInstruction: genai.NewContentFromText("你是一个专业的会议录音分析专家。", genai.RoleUser),
		TTL: 3600 * time.Second, // 缓存存活时间：1小时
	})
	if err != nil { log.Fatal(err) }
	
	fmt.Println("缓存创建成功！Cache Name:", cache.Name)

	// =====================================================================
	// 3. 第一次使用缓存 (⚠️ 命中缓存)
	// 将缓存的 Name 传入 GenerateContentConfig。
	// 模型会自动读取庞大的原始文本，只消耗“缓存读取”的廉价 token。
	// =====================================================================
	fmt.Println("\n--- 第 1 次提问 ---")
	resp1, err := client.Models.GenerateContent(
		ctx,
		modelName,
		genai.Text("请总结这份会议记录的核心要点。"),
		&genai.GenerateContentConfig{
			CachedContent: cache.Name, // 核心：显式关联 Cache ID
		},
	)
	if err != nil { log.Fatal(err) }
	printResponse(resp1) 

	// =====================================================================
	// 4. 第二次使用同一个缓存 (⚠️ 再次命中缓存)
	// 在 TTL 到期前，你可以无限次复用这个庞大的上下文，而不用重新传输文件。
	// =====================================================================
	fmt.Println("\n--- 第 2 次提问 ---")
	resp2, err := client.Models.GenerateContent(
		ctx,
		modelName,
		genai.Text("请提取这份记录中提到的所有财务数据指标。"),
		&genai.GenerateContentConfig{
			CachedContent: cache.Name, // 复用同一个 Cache ID
		},
	)
	if err != nil { log.Fatal(err) }
	printResponse(resp2)
}

func printResponse(resp *genai.GenerateContentResponse) {
	if resp != nil && len(resp.Candidates) > 0 {
		for _, cand := range resp.Candidates {
			if cand.Content != nil {
				for _, part := range cand.Content.Parts { fmt.Println(part) }
			}
		}
	}
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();
        String modelName = "gemini-2.5-flash";

        // 1. 常规上传大文件 (使用 Files API)
        File document = client.files.upload(Paths.get("docs/large_transcript.txt"), null);
        List<Part> parts = List.of(Part.fromUri(document.uri(), document.mimeType()));
        List<Content> contents = List.of(Content.fromParts(parts, "user"));

        // =====================================================================
        // 2. 创建缓存 (⚠️ 缓存动作在此发生)
        // =====================================================================
        CachedContent cache = client.caches.create(
            modelName,
            CreateCachedContentConfig.builder()
                .contents(contents)
                .systemInstruction(Content.fromText("你是一个专业的会议录音分析专家。", "user"))
                .ttl(Duration.ofSeconds(3600))
                .build()
        );
        System.out.println("缓存创建成功！Cache Name: " + cache.name());

        // =====================================================================
        // 3. 第一次使用缓存 (⚠️ 命中缓存)
        // =====================================================================
        System.out.println("\n--- 第 1 次提问 ---");
        GenerateContentResponse resp1 = client.models.generateContent(
            modelName,
            "请总结这份会议记录的核心要点。",
            GenerateContentConfig.builder().cachedContent(cache.name()).build()
        );
        System.out.println(resp1.text());

        // =====================================================================
        // 4. 第二次使用同一个缓存 (⚠️ 再次命中缓存)
        // =====================================================================
        System.out.println("\n--- 第 2 次提问 ---");
        GenerateContentResponse resp2 = client.models.generateContent(
            modelName,
            "请提取这份记录中提到的所有财务数据指标。",
            GenerateContentConfig.builder().cachedContent(cache.name()).build()
        );
        System.out.println(resp2.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 缓存的生命周期管理操作（完整代码）

缓存的内容本身无法被下载出来，但你可以管理它的元数据（如 `name`, `model`, `display_name`, `usage_metadata`, `expire_time`）和生命周期：

##### 1. 列出所有缓存（List caches）

你可以通过分页或一次性列出当前项目下的所有可用缓存：

{{< tabs >}}
{{< tab "Go" >}}
```go
// 简单列出所有缓存
caches, err := client.Caches.All(ctx)
if err != nil {
    log.Fatal(err)
}
fmt.Println("Listing all caches:")
for _, item := range caches {
    fmt.Println("   ", item.Name)
}

// 分页列出缓存 (Page size = 2)
page, err := client.Caches.List(ctx, &genai.ListCachedContentsConfig{PageSize: 2})
if err != nil {
    log.Fatal(err)
}

pageIndex := 1
for {
    fmt.Printf("Listing caches (page %d):\n", pageIndex)
    for _, item := range page.Items {
        fmt.Println("   ", item.Name)
    }
    if page.NextPageToken == "" {
        break
    }
    page, err = page.Next(ctx)
    if err == genai.ErrPageDone {
        break
    } else if err != nil {
        log.Fatal(err)
    }
    pageIndex++
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
// 简单列出所有缓存
List<CachedContent> caches = client.caches.list(null);
System.out.println("Listing all caches:");
for (CachedContent cc : caches) {
    System.out.println("    " + cc.name());
}

// 分页列出缓存（页大小 = 2）
ListCachedContentsResponse page = client.caches.list(
    ListCachedContentsConfig.builder().pageSize(2).build()
);
int pageIndex = 1;
while (page != null) {
    System.out.printf("Listing caches (page %d):%n", pageIndex);
    for (CachedContent cc : page.cachedContents()) {
        System.out.println("    " + cc.name());
    }
    page = page.hasNextPage() ? page.nextPage() : null;
    pageIndex++;
}
```
{{< /tab >}}
{{< /tabs >}}

##### 2. 更新缓存的存活期（Update a cache）

你只能更新缓存的过期时间 (`ttl` 或 `expire_time`)，不支持修改缓存内的文件或提示词。

{{< tabs >}}
{{< tab "Go" >}}
```go
// 将 TTL 更新为 2 小时 (7200 秒)
cache, err = client.Caches.Update(ctx, cache.Name, &genai.UpdateCachedContentConfig{
    TTL: 7200 * time.Second,
})
if err != nil {
    log.Fatal(err)
}
fmt.Println("After update:")
fmt.Println(cache)
```
{{< /tab >}}

{{< tab "Java" >}}
```java
// 将 TTL 更新为 2 小时（7200 秒）
CachedContent updated = client.caches.update(
    cache.name(),
    UpdateCachedContentConfig.builder()
        .ttl(Duration.ofSeconds(7200))
        .build()
);
System.out.println("After update:");
System.out.println(updated);
```
{{< /tab >}}
{{< /tabs >}}

##### 3. 主动删除缓存（Delete a cache）

如果提问结束，推荐主动调用删除操作防止产生多余的按时计费存储成本：

{{< tabs >}}
{{< tab "Go" >}}
```go
_, err = client.Caches.Delete(ctx, cache.Name, &genai.DeleteCachedContentConfig{})
if err != nil {
    log.Fatal(err)
}
fmt.Println("Cache deleted:", cache.Name)
```
{{< /tab >}}

{{< tab "Java" >}}
```java
client.caches.delete(cache.name());
System.out.println("Cache deleted: " + cache.name());
```
{{< /tab >}}
{{< /tabs >}}

---

### 实战场景三：缓存超长 Prompt 模板（按单据类型）

**场景背景**：你有多种单据类型（发票、提单、合同…），每种类型对应一段**极长**的提取指令（JSON Schema 定义 + 规则约束 + Few-Shot 示例），内容固定不变。
同一类型的单据每次传入的是不同文件，但 prompt 完全相同。

> **核心思路变换**：
> - 场景一：缓存**大文件**，每次换 prompt → 适合反复问同一份文档
> - 本场景：缓存**超长 Prompt 模板**，每次换文件 → 适合批量处理同类型的不同单据

#### 设计思路

```
【缓存里存放的内容】
└── SystemInstruction: "你是专业单据解析引擎…"
└── Contents:          [超长的 JSON Schema + Few-Shot 示例 + 提取规则]  ← 这部分每次都一样，非常长

【每次 GenerateContent 传入的内容】
└── CachedContent:  对应单据类型的 Cache Name
└── 新鲜内容:        本次实际单据文件（每次不同）
```

#### 完整 Go 代码实现

{{< tabs >}}
{{< tab "Go" >}}
```go
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"google.golang.org/genai"
	"google.golang.org/api/option"
)

// 超长 prompt 模板（发票类型）
// ❗ 注意：角色声明由 SystemInstruction 统一负责，这里只放具体任务指令
// Contents 里只放：JSON Schema + 字段规则 + Few-Shot 示例（纯任务内容）
const invoicePromptTemplate = `

## 输出格式（必须为合法 JSON）
{
  "invoice_number":   "string",
  "invoice_date":     "YYYY-MM-DD",
  "seller_name":      "string",
  "buyer_name":       "string",
  "total_amount":     number,
  "currency":         "string",
  "line_items": [
    {
      "description":  "string",
      "quantity":     number,
      "unit_price":   number,
      "subtotal":     number
    }
  ]
}

## 提取规则
- 日期统一转换为 YYYY-MM-DD 格式
- 金额统一转为数值型，去除货币符号
- 如字段不存在，填 null，不得省略 key
- line_items 必须提取所有行，一条不可遗漏
...（此处省略，实际 prompt 可能长达数千 token）
`

// 单据类型注册表：提前为每种类型创建并缓存 prompt 模板
type DocTypeCache struct {
	CacheName string
}

func buildPromptCache(ctx context.Context, client *genai.Client, modelName, docType, promptTemplate string) (*DocTypeCache, error) {
	// =====================================================================
	// 关键：把超长 prompt 模板作为 Contents 缓存进去
	// 系统指令 + 长 prompt = 每次请求都省掉的大批 token
	// =====================================================================
	promptParts := []*genai.Part{genai.NewPartFromText(promptTemplate)}
	promptContent := []*genai.Content{genai.NewContentFromParts(promptParts, genai.RoleUser)}

	cache, err := client.Caches.Create(ctx, modelName, &genai.CreateCachedContentConfig{
		Contents: promptContent,
		SystemInstruction: genai.NewContentFromText(
			"你是专业的单据解析引擎，请严格按照已缓存的指令提取字段，输出合法 JSON。",
			genai.RoleUser,
		),
		TTL: 24 * 3600 * time.Second, // 每天构建一次缓存即可
	})
	if err != nil {
		return nil, fmt.Errorf("[%s] 缓存创建失败: %v", docType, err)
	}
	fmt.Printf("[%s] Prompt 模板缓存成功: %s\n", docType, cache.Name)
	return &DocTypeCache{CacheName: cache.Name}, nil
}

func processDocument(ctx context.Context, client *genai.Client, modelName string, cache *DocTypeCache, filePath string) {
	// 上传本次实际单据文件（每次都是新的）
	document, err := client.Files.UploadFromPath(ctx, filePath, nil)
	if err != nil {
		log.Printf("文件上传失败 [%s]: %v", filePath, err)
		return
	}
	defer client.Files.Delete(ctx, document.Name)

	// =====================================================================
	// 每次 GenerateContent：
	//   - CachedContent = 已缓存的超长 prompt 模板 (⚠️ 命中缓存，廉价 token)
	//   - 新鲜传入     = 本次实际文件            (⚠️ 正常计费 token)
	// =====================================================================
	resp, err := client.Models.GenerateContent(
		ctx,
		modelName,
		genai.NewPartFromURI(document.URI, document.MIMEType), // 只传文件，prompt 已在缓存里
		&genai.GenerateContentConfig{
			CachedContent: cache.CacheName, // 引用对应单据类型的缓存
		},
	)
	if err != nil {
		log.Printf("解析失败 [%s]: %v", filePath, err)
		return
	}

	fmt.Printf("\n=== 解析结果 [%s] ===\n", filePath)
	for _, cand := range resp.Candidates {
		if cand.Content != nil {
			for _, part := range cand.Content.Parts {
				fmt.Println(part)
			}
		}
	}
}

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, option.WithAPIKey(""))
	if err != nil { log.Fatal(err) }
	defer client.Close()

	modelName := "gemini-2.5-flash"

	// 1. 启动时按单据类型构建 Prompt 缓存（只建一次）
	invoiceCache, err := buildPromptCache(ctx, client, modelName, "invoice", invoicePromptTemplate)
	if err != nil { log.Fatal(err) }
	defer client.Caches.Delete(ctx, invoiceCache.CacheName, &genai.DeleteCachedContentConfig{})

	// billOfLadingCache, err := buildPromptCache(ctx, client, modelName, "bol", bolPromptTemplate)
	// contractCache, err := buildPromptCache(ctx, client, modelName, "contract", contractPromptTemplate)

	// 2. 批量处理发票文件，每次只传文件，prompt 命中缓存
	invoiceFiles := []string{
		"docs/invoice_2024_001.pdf",
		"docs/invoice_2024_002.pdf",
		"docs/invoice_2024_003.pdf",
	}

	for _, f := range invoiceFiles {
		processDocument(ctx, client, modelName, invoiceCache, f)
	}
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.List;

// 单据类型注册表
class DocTypeCache {
    String cacheName;
    DocTypeCache(String name) { this.cacheName = name; }
}

public class Main {
    static final String INVOICE_PROMPT_TEMPLATE =
        "## 输出格式（必须为合法 JSON）\n" +
        "{ \"invoice_number\": \"string\", \"invoice_date\": \"YYYY-MM-DD\", ... }\n" +
        "## 提取规则\n" +
        "- 日期统一转换为 YYYY-MM-DD 格式\n" +
        "- 金额统一转为数值型，去除货币符号\n" +
        "- 如字段不存在，填 null，不得省略 key\n" +
        "...（实际 prompt 可能长达数千 token）";

    static DocTypeCache buildPromptCache(Client client, String modelName,
            String docType, String promptTemplate) throws Exception {
        List<Part> promptParts = List.of(Part.fromText(promptTemplate));
        List<Content> promptContent = List.of(Content.fromParts(promptParts, "user"));

        CachedContent cache = client.caches.create(
            modelName,
            CreateCachedContentConfig.builder()
                .contents(promptContent)
                .systemInstruction(Content.fromText(
                    "你是专业的单据解析引擎，请严格按照已缓存的指令提取字段，输出合法 JSON。",
                    "user"))
                .ttl(Duration.ofSeconds(86400))
                .build()
        );
        System.out.printf("[%s] Prompt 模板缓存成功: %s%n", docType, cache.name());
        return new DocTypeCache(cache.name());
    }

    static void processDocument(Client client, String modelName,
            DocTypeCache cache, String filePath) throws Exception {
        File document = client.files.upload(Paths.get(filePath), null);
        try {
            GenerateContentResponse resp = client.models.generateContent(
                modelName,
                Part.fromUri(document.uri(), document.mimeType()),
                GenerateContentConfig.builder()
                    .cachedContent(cache.cacheName)
                    .build()
            );
            System.out.printf("%n=== 解析结果 [%s] ===%n%s%n", filePath, resp.text());
        } finally {
            client.files.delete(document.name());
        }
    }

    public static void main(String[] args) throws Exception {
        Client client = new Client();
        String modelName = "gemini-2.5-flash";

        DocTypeCache invoiceCache = buildPromptCache(
            client, modelName, "invoice", INVOICE_PROMPT_TEMPLATE);

        String[] invoiceFiles = {
            "docs/invoice_2024_001.pdf",
            "docs/invoice_2024_002.pdf",
            "docs/invoice_2024_003.pdf"
        };
        for (String f : invoiceFiles) {
            processDocument(client, modelName, invoiceCache, f);
        }
        client.caches.delete(invoiceCache.cacheName);
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 成本优势一览

| 策略 | 每次请求发送的 token | 适合场景 |
|------|----------------------|---------|
| 不使用缓存 | 文件 + 超长 Prompt（每次全量） | 偶发请求 |
| 缓存超长 Prompt（本场景）| 文件（普通计费） + Prompt（缓存价格，约 75% 折扣） | 批量处理同类型单据 |
| 缓存大文件（场景一）| Prompt（普通计费） + 文件（缓存价格） | 反复询问同一份文件 |

---

### 实战场景四：ResponseSchema 结构化输出（JSON Schema 不占 prompt token）

**核心问题**：JSON Schema 很大，把它塞在 prompt 里会：
1. **大量消耗 token**（Schema 本身就很长）
2. **无法保证 JSON 不乱**（模型只是"参考"你的 prompt，仍然可能输出格式错误）

**解决方案**：`GenerateContentConfig.ResponseSchema` + `ResponseMIMEType: "application/json"`

这是 Gemini 的**结构化输出（Structured Output）** 功能。Schema 作为推理引擎的约束参数传入，**完全不进入 prompt token 计算**，且模型底层使用约束解码（Constrained Decoding），从语法层面**强制输出合法 JSON**。

#### 两种方案对比

| | 把 Schema 写在 prompt 里 | 用 ResponseSchema |
|---|---|---|
| Schema token 消耗 | ✅ 占用 prompt token（很贵） | ✅ 不占 prompt token |
| JSON 合法性保证 | ❌ 模型"参考"，可能输出乱格式 | ✅ 约束解码，语法层强制保证 |
| Schema 与 prompt 是否解耦 | ❌ 混在一起难维护 | ✅ 完全独立，代码清晰 |
| 是否可与 Context Cache 结合 | ✅ | ✅ |

#### Go 代码实现

{{< tabs >}}
{{< tab "Go" >}}
```go
package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/genai"
	"google.golang.org/api/option"
)

// 每种单据类型定义各自的 ResponseSchema（Go 代码定义，不写在 prompt 里）
var invoiceSchema = &genai.Schema{
	Type: genai.TypeObject,
	Properties: map[string]*genai.Schema{
		"invoice_number": {Type: genai.TypeString},
		"invoice_date":   {Type: genai.TypeString, Description: "格式: YYYY-MM-DD"},
		"seller_name":    {Type: genai.TypeString},
		"buyer_name":     {Type: genai.TypeString},
		"total_amount":   {Type: genai.TypeNumber},
		"currency":       {Type: genai.TypeString},
		"line_items": {
			Type: genai.TypeArray,
			Items: &genai.Schema{
				Type: genai.TypeObject,
				Properties: map[string]*genai.Schema{
					"description": {Type: genai.TypeString},
					"quantity":    {Type: genai.TypeNumber},
					"unit_price":  {Type: genai.TypeNumber},
					"subtotal":    {Type: genai.TypeNumber},
				},
				Required: []string{"description", "quantity", "unit_price", "subtotal"},
			},
		},
	},
	Required: []string{"invoice_number", "invoice_date", "seller_name", "buyer_name", "total_amount", "currency", "line_items"},
}

// 不同单据类型的 prompt 可以有完全不同的语义描述（简洁版，无需 Schema 文本）
var docTypePrompts = map[string]string{
	"invoice": "请从这张发票中提取所有关键字段，包括卖家、买家、金额和商品行项目。",
	"bol":     "请从这份提单中提取所有货运关键信息，包括托运人、收货人、货物描述和运输路线。",
	"contract": "请从这份合同中提取合同编号、签署方、生效日期、到期日期及核心条款摘要。",
}

var docTypeSchemas = map[string]*genai.Schema{
	"invoice":  invoiceSchema,
	// "bol":      billOfLadingSchema,
	// "contract": contractSchema,
}

func processWithSchema(ctx context.Context, client *genai.Client, modelName, docType, filePath string) {
	schema, ok := docTypeSchemas[docType]
	if !ok {
		log.Fatalf("未知单据类型：%s", docType)
	}
	prompt, ok := docTypePrompts[docType]
	if !ok {
		log.Fatalf("未找到对应 prompt：%s", docType)
	}

	// 上传文件
	document, err := client.Files.UploadFromPath(ctx, filePath, nil)
	if err != nil { log.Fatal(err) }
	defer client.Files.Delete(ctx, document.Name)

	resp, err := client.Models.GenerateContent(
		ctx,
		modelName,
		[]*genai.Content{{
			Parts: []*genai.Part{
				genai.NewPartFromURI(document.URI, document.MIMEType),
				genai.NewPartFromText(prompt), // prompt 简洁，无需 Schema 文字
			},
		}},
		&genai.GenerateContentConfig{
			// =====================================================================
			// ⚠️ 关键：Schema 在这里传入，完全不占 prompt token
			// 模型底层使用约束解码，输出必然是合法的 JSON，不可能乱掉
			// =====================================================================
			ResponseMIMEType: "application/json",
			ResponseSchema:   schema,
		},
	)
	if err != nil { log.Fatal(err) }

	// 直接拿到合法 JSON 字符串
	fmt.Printf("[%s] 解析结果:\n%s\n", filePath, resp.Text())
}

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, option.WithAPIKey(""))
	if err != nil { log.Fatal(err) }
	defer client.Close()

	modelName := "gemini-2.5-flash"

	processWithSchema(ctx, client, modelName, "invoice", "docs/invoice_001.pdf")
	processWithSchema(ctx, client, modelName, "invoice", "docs/invoice_002.pdf")
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

public class Main {
    // 每种单据类型定义各自的 ResponseSchema
    static final Schema INVOICE_SCHEMA = Schema.builder()
        .type(Type.OBJECT)
        .properties(Map.of(
            "invoice_number", Schema.builder().type(Type.STRING).build(),
            "invoice_date",   Schema.builder().type(Type.STRING)
                                .description("格式: YYYY-MM-DD").build(),
            "seller_name",    Schema.builder().type(Type.STRING).build(),
            "buyer_name",     Schema.builder().type(Type.STRING).build(),
            "total_amount",   Schema.builder().type(Type.NUMBER).build(),
            "currency",       Schema.builder().type(Type.STRING).build(),
            "line_items", Schema.builder()
                .type(Type.ARRAY)
                .items(Schema.builder()
                    .type(Type.OBJECT)
                    .properties(Map.of(
                        "description", Schema.builder().type(Type.STRING).build(),
                        "quantity",    Schema.builder().type(Type.NUMBER).build(),
                        "unit_price",  Schema.builder().type(Type.NUMBER).build(),
                        "subtotal",    Schema.builder().type(Type.NUMBER).build()
                    ))
                    .required(List.of("description","quantity","unit_price","subtotal"))
                    .build())
                .build()
        ))
        .required(List.of("invoice_number","invoice_date","seller_name",
                          "buyer_name","total_amount","currency","line_items"))
        .build();

    static void processWithSchema(Client client, String modelName,
            String docType, String filePath) throws Exception {
        File document = client.files.upload(Paths.get(filePath), null);
        try {
            GenerateContentResponse resp = client.models.generateContent(
                modelName,
                List.of(Content.fromParts(List.of(
                    Part.fromUri(document.uri(), document.mimeType()),
                    Part.fromText("请从这张发票中提取所有关键字段，包括卖家、买家、金额和商品行项目。")
                ), "user")),
                // ⚠️ 关键：Schema 在这里传入，完全不占 prompt token
                GenerateContentConfig.builder()
                    .responseMimeType("application/json")
                    .responseSchema(INVOICE_SCHEMA)
                    .build()
            );
            System.out.printf("[%s] 解析结果:%n%s%n", filePath, resp.text());
        } finally {
            client.files.delete(document.name());
        }
    }

    public static void main(String[] args) throws Exception {
        Client client = new Client();
        String modelName = "gemini-2.5-flash";
        processWithSchema(client, modelName, "invoice", "docs/invoice_001.pdf");
        processWithSchema(client, modelName, "invoice", "docs/invoice_002.pdf");
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 与 Context Caching 结合使用

ResponseSchema 和 Context Caching 完全可以同时使用。这是最优组合：

```
【缓存里存放的内容】
└── SystemInstruction: "你是专业单据解析引擎"（简洁角色声明）
└── Contents:          [单据类型特定的 prompt（描述性语言，无需贴 Schema）]

【每次 GenerateContent】
└── CachedContent:    对应单据类型的 Cache Name
└── 新鲜内容:          实际文件
└── ResponseSchema:   Go 代码定义的 Schema（不占 prompt token，底层约束）
```

{{< tabs >}}
{{< tab "Go" >}}
```go
// 最终最优方案（缓存 prompt 描述 + Schema 约束解码）
resp, err := client.Models.GenerateContent(
	ctx,
	modelName,
	genai.NewPartFromURI(document.URI, document.MIMEType),
	&genai.GenerateContentConfig{
		CachedContent:    invoiceCache.CacheName,  // 命中缓存：描述性 prompt
		ResponseMIMEType: "application/json",
		ResponseSchema:   invoiceSchema,            // Schema 不在 prompt 里，不占 token
	},
)
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

public class Main {
    // 每种单据类型定义各自的 ResponseSchema
    static final Schema INVOICE_SCHEMA = Schema.builder()
        .type(Type.OBJECT)
        .properties(Map.of(
            "invoice_number", Schema.builder().type(Type.STRING).build(),
            "invoice_date",   Schema.builder().type(Type.STRING)
                                .description("格式: YYYY-MM-DD").build(),
            "seller_name",    Schema.builder().type(Type.STRING).build(),
            "buyer_name",     Schema.builder().type(Type.STRING).build(),
            "total_amount",   Schema.builder().type(Type.NUMBER).build(),
            "currency",       Schema.builder().type(Type.STRING).build(),
            "line_items", Schema.builder()
                .type(Type.ARRAY)
                .items(Schema.builder()
                    .type(Type.OBJECT)
                    .properties(Map.of(
                        "description", Schema.builder().type(Type.STRING).build(),
                        "quantity",    Schema.builder().type(Type.NUMBER).build(),
                        "unit_price",  Schema.builder().type(Type.NUMBER).build(),
                        "subtotal",    Schema.builder().type(Type.NUMBER).build()
                    ))
                    .required(List.of("description","quantity","unit_price","subtotal"))
                    .build())
                .build()
        ))
        .required(List.of("invoice_number","invoice_date","seller_name",
                          "buyer_name","total_amount","currency","line_items"))
        .build();

    static void processWithSchema(Client client, String modelName,
            String docType, String filePath) throws Exception {
        File document = client.files.upload(Paths.get(filePath), null);
        try {
            GenerateContentResponse resp = client.models.generateContent(
                modelName,
                List.of(Content.fromParts(List.of(
                    Part.fromUri(document.uri(), document.mimeType()),
                    Part.fromText("请从这张发票中提取所有关键字段，包括卖家、买家、金额和商品行项目。")
                ), "user")),
                // ⚠️ 关键：Schema 在这里传入，完全不占 prompt token
                GenerateContentConfig.builder()
                    .responseMimeType("application/json")
                    .responseSchema(INVOICE_SCHEMA)
                    .build()
            );
            System.out.printf("[%s] 解析结果:%n%s%n", filePath, resp.text());
        } finally {
            client.files.delete(document.name());
        }
    }

    public static void main(String[] args) throws Exception {
        Client client = new Client();
        String modelName = "gemini-2.5-flash";
        processWithSchema(client, modelName, "invoice", "docs/invoice_001.pdf");
        processWithSchema(client, modelName, "invoice", "docs/invoice_002.pdf");
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 小结：什么该放在哪里？

| 内容 | 放在哪里 | 原因 |
|------|----------|------|
| 角色声明（"你是解析引擎"） | `SystemInstruction` | 高优先级，短小 |
| 描述性任务 prompt（"请提取发票字段，注意..."） | `Contents`（可缓存） | 有意义的语义描述，可随单据类型变化 |
| JSON Schema 结构定义 | `ResponseSchema` | 不占 prompt token，约束解码保证合法 JSON |
| 实际单据文件 | 每次新鲜传入 `Contents` | 每次不同 |

---

## 四、Document Understanding（PDF 文档理解）

Gemini 使用**原生视觉**处理 PDF，像人类一样阅读文档，不仅理解文字，还能理解图像、图表、表格和排版结构，支持最多 **1000 页**。这与传统 OCR 有本质区别：Gemini 能理解上下文和结构。

**核心能力：**
- 提取数据为结构化输出（JSON、表格）
- 基于视觉 + 文本元素进行问答和摘要
- 转录文档内容（如 HTML），保留排版供下游使用

> ⚠️ 非 PDF 类型（TXT、HTML、Markdown、XML 等）虽然可以传入，但只会被当作**纯文本**提取，图表、格式信息全部丢失。

---

### 方式一：Inline Data 内联传入（小文件 ≤ 50 MB）

适合一次性、临时性处理的小文档。文件字节直接嵌入请求 payload，无需上传步骤。

#### 从 URL 获取 PDF

{{< tabs >}}
{{< tab "Go" >}}
```go
package main

import (
    "context"
    "fmt"
    "io"
    "net/http"
    "os"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, _ := genai.NewClient(ctx, &genai.ClientConfig{
        APIKey:  os.Getenv("GEMINI_API_KEY"),
        Backend: genai.BackendGeminiAPI,
    })

    // 1. 从 URL 拉取 PDF 字节
    pdfResp, _ := http.Get("https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf")
    pdfBytes, _ := io.ReadAll(pdfResp.Body)
    pdfResp.Body.Close()

    parts := []*genai.Part{
        // ⚠️ INLINE DATA：字节直接嵌入请求体，无上传步骤，不可复用
        {InlineData: &genai.Blob{
            MIMEType: "application/pdf",
            Data:     pdfBytes,
        }},
        genai.NewPartFromText("请总结这份文档"),
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash",
        []*genai.Content{genai.NewContentFromParts(parts, genai.RoleUser)},
        nil,
    )
    fmt.Println(result.Text())
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.io.InputStream;
import java.net.URL;
import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        // 1. 从 URL 拉取 PDF 字节
        URL url = new URL("https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf");
        byte[] pdfBytes;
        try (InputStream in = url.openStream()) {
            pdfBytes = in.readAllBytes();
        }

        List<Part> parts = List.of(
            // ⚠️ INLINE DATA：字节直接嵌入请求体，无上传步骤，不可复用
            Part.fromBytes(pdfBytes, "application/pdf"),
            Part.fromText("请总结这份文档")
        );

        GenerateContentResponse result = client.models.generateContent(
            "gemini-2.5-flash",
            List.of(Content.fromParts(parts, "user")),
            null
        );
        System.out.println(result.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 从本地文件读取

{{< tabs >}}
{{< tab "Go" >}}
```go
// 同样的结构，改为从磁盘读取字节
pdfBytes, _ := os.ReadFile("path/to/your/file.pdf")

parts := []*genai.Part{
    // ⚠️ INLINE DATA：本地字节直接嵌入，快但不可复用
    {InlineData: &genai.Blob{MIMEType: "application/pdf", Data: pdfBytes}},
    genai.NewPartFromText("请总结这份文档"),
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
// 同样的结构，改为从磁盘读取字节
byte[] pdfBytes = Files.readAllBytes(Paths.get("path/to/your/file.pdf"));

List<Part> parts = List.of(
    // ⚠️ INLINE DATA：本地字节直接嵌入，快但不可复用
    Part.fromBytes(pdfBytes, "application/pdf"),
    Part.fromText("请总结这份文档")
);
```
{{< /tab >}}
{{< /tabs >}}

---

### 方式二：Files API 上传（大文件 / 可复用）

以下情况必须使用 Files API：
- 文件超过 50 MB，或整体 payload 超过 100 MB
- 需要多次查询同一份文件（节省带宽、降低延迟）
- 文件存储于 Google 服务器 **48 小时**，免费

#### 从 URL 下载后上传

{{< tabs >}}
{{< tab "Go" >}}
```go
package main

import (
    "context"
    "fmt"
    "io"
    "net/http"
    "os"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, _ := genai.NewClient(ctx, &genai.ClientConfig{
        APIKey:  os.Getenv("GEMINI_API_KEY"),
        Backend: genai.BackendGeminiAPI,
    })

    // 1. 先下载到本地
    pdfURL := "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"
    localPath := "A17_FlightPlan_downloaded.pdf"
    respHttp, _ := http.Get(pdfURL)
    defer respHttp.Body.Close()
    outFile, _ := os.Create(localPath)
    io.Copy(outFile, respHttp.Body)
    outFile.Close()

    // ⚠️ FILES API 上传：文件存入 Google 服务器 48 小时
    // 返回的 URI 可在后续多次 GenerateContent 中复用
    uploadedFile, _ := client.Files.UploadFromPath(ctx, localPath,
        &genai.UploadFileConfig{MIMEType: "application/pdf"},
    )

    promptParts := []*genai.Part{
        // ⚠️ 通过 URI 引用：不需要重传，模型直接从服务端获取
        genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
        genai.NewPartFromText("请总结这份文档"),
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash",
        []*genai.Content{genai.NewContentFromParts(promptParts, genai.RoleUser)},
        nil,
    )
    fmt.Println(result.Text())
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.io.*;
import java.net.URL;
import java.nio.file.*;
import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        // 1. 先下载到本地
        String pdfUrl = "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf";
        Path localPath = Paths.get("A17_FlightPlan_downloaded.pdf");
        try (InputStream in = new URL(pdfUrl).openStream()) {
            Files.copy(in, localPath, StandardCopyOption.REPLACE_EXISTING);
        }

        // ⚠️ FILES API 上传：文件存入 Google 服务器 48 小时
        File uploadedFile = client.files.upload(
            localPath,
            UploadFileConfig.builder().mimeType("application/pdf").build()
        );

        List<Part> promptParts = List.of(
            // ⚠️ 通过 URI 引用：不需要重传，模型直接从服务端获取
            Part.fromUri(uploadedFile.uri(), uploadedFile.mimeType()),
            Part.fromText("请总结这份文档")
        );

        GenerateContentResponse result = client.models.generateContent(
            "gemini-2.5-flash",
            List.of(Content.fromParts(promptParts, "user")),
            null
        );
        System.out.println(result.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

#### 直接上传本地文件

{{< tabs >}}
{{< tab "Go" >}}
```go
// ⚠️ FILES API 上传：将本地 PDF 上传至 Google 服务器
uploadedFile, _ := client.Files.UploadFromPath(ctx, "/path/to/file.pdf",
    &genai.UploadFileConfig{MIMEType: "application/pdf"},
)

// ⚠️ URI 引用：将返回的 URI 传给模型
promptParts := []*genai.Part{
    genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
    genai.NewPartFromText("请给我这份 PDF 的摘要。"),
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
// ⚠️ FILES API 上传：将本地 PDF 上传至 Google 服务器
File uploadedFile = client.files.upload(
    Paths.get("/path/to/file.pdf"),
    UploadFileConfig.builder().mimeType("application/pdf").build()
);

// ⚠️ URI 引用：将返回的 URI 传给模型
List<Part> promptParts = List.of(
    Part.fromUri(uploadedFile.uri(), uploadedFile.mimeType()),
    Part.fromText("请给我这份 PDF 的摘要。")
);
```
{{< /tab >}}
{{< /tabs >}}

---

### 方式三：多 PDF 合并分析

Gemini 支持在**单次请求**中传入多份 PDF（总计最多 1000 页，在模型上下文窗口内），适合跨文档对比分析。

{{< tabs >}}
{{< tab "Go" >}}
```go
package main

import (
    "context"
    "fmt"
    "io"
    "net/http"
    "os"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, _ := genai.NewClient(ctx, &genai.ClientConfig{
        APIKey:  os.Getenv("GEMINI_API_KEY"),
        Backend: genai.BackendGeminiAPI,
    })

    // 下载两篇论文
    urls := map[string]string{
        "doc1_downloaded.pdf": "https://arxiv.org/pdf/2312.11805",
        "doc2_downloaded.pdf": "https://arxiv.org/pdf/2403.05530",
    }
    for localPath, url := range urls {
        resp, _ := http.Get(url)
        f, _ := os.Create(localPath)
        io.Copy(f, resp.Body)
        f.Close()
        resp.Body.Close()
    }

    // ⚠️ 分别上传两份文件（独立的 Files API 调用）
    file1, _ := client.Files.UploadFromPath(ctx, "doc1_downloaded.pdf",
        &genai.UploadFileConfig{MIMEType: "application/pdf"})
    file2, _ := client.Files.UploadFromPath(ctx, "doc2_downloaded.pdf",
        &genai.UploadFileConfig{MIMEType: "application/pdf"})

    promptParts := []*genai.Part{
        // ⚠️ 两个 URI 放在同一个 Parts 数组 → Gemini 同时读取两份文件
        genai.NewPartFromURI(file1.URI, file1.MIMEType),
        genai.NewPartFromURI(file2.URI, file2.MIMEType),
        genai.NewPartFromText("对比这两篇论文的主要基准指标差异，以表格形式输出。"),
    }

    result, _ := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash",
        []*genai.Content{genai.NewContentFromParts(promptParts, genai.RoleUser)},
        nil,
    )
    fmt.Println(result.Text())
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.io.*;
import java.net.URL;
import java.nio.file.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        // 下载两篇论文
        Map<String, String> urls = Map.of(
            "doc1_downloaded.pdf", "https://arxiv.org/pdf/2312.11805",
            "doc2_downloaded.pdf", "https://arxiv.org/pdf/2403.05530"
        );
        for (Map.Entry<String, String> e : urls.entrySet()) {
            try (InputStream in = new URL(e.getValue()).openStream()) {
                Files.copy(in, Paths.get(e.getKey()), StandardCopyOption.REPLACE_EXISTING);
            }
        }

        // ⚠️ 分别上传两份文件（独立的 Files API 调用）
        File file1 = client.files.upload(Paths.get("doc1_downloaded.pdf"),
            UploadFileConfig.builder().mimeType("application/pdf").build());
        File file2 = client.files.upload(Paths.get("doc2_downloaded.pdf"),
            UploadFileConfig.builder().mimeType("application/pdf").build());

        List<Part> promptParts = List.of(
            // ⚠️ 两个 URI 放在同一个 Parts 列表 → Gemini 同时读取两份文件
            Part.fromUri(file1.uri(), file1.mimeType()),
            Part.fromUri(file2.uri(), file2.mimeType()),
            Part.fromText("对比这两篇论文的主要基准指标差异，以表格形式输出。")
        );

        GenerateContentResponse result = client.models.generateContent(
            "gemini-2.5-flash",
            List.of(Content.fromParts(promptParts, "user")),
            null
        );
        System.out.println(result.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

---

### 技术限制与最佳实践

| 维度 | 限制 / 说明 |
|------|-------------|
| 最大文件大小 | 50 MB（内联）/ 2 GB（Files API）|
| 最多页数 | 每次请求 1000 页 |
| 每页 token 消耗 | 258 tokens |
| 页面分辨率 | 最大缩放至 3072×3072（低分辨率无折扣）|
| Files API 存储 | 48 小时，免费 |

**最佳实践：**
- 上传前将页面旋转至正确方向
- 避免模糊或低对比度的扫描件
- 单页文档时，将文字 prompt 放在页面 Part **之后**
- 凡是需要多次查询的文件，一律使用 Files API

---

## 五、结构化输出（Structured Output）

结构化输出功能允许你为 Gemini 指定一个 JSON Schema，模型通过底层**约束解码（Constrained Decoding）**，在语法层面强制保证输出严格符合该 Schema。

**适用场景：**
- **数据提取** — 从非结构化文本中提取指定字段（姓名、日期、金额）
- **文本分类** — 将内容归类为预定义的枚举值
- **智能体工作流** — 为工具或 API 生成结构化输入

> **注意**：与此前场景中的 `ResponseSchema`（传 `*genai.Schema` Go 类型对象）相比，`ResponseJsonSchema` 允许直接传原生 `map[string]any` JSON Schema，两种方式都触发相同的约束解码机制，按需选择即可。

---

### Go 示例：菜谱提取

以下代码演示使用 `ResponseJsonSchema`（原生 JSON Schema）从无格式文本中提取结构化菜谱数据。

{{< tabs >}}
{{< tab "Go" >}}
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
    // 自动读取 GEMINI_API_KEY 环境变量
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `请从以下文本中提取菜谱信息。
用户想要制作美味的巧克力芯片饼干。
需要 2 又 1/4 杯中筋面粉、1 茶匙小苏打...`

    config := &genai.GenerateContentConfig{
        // ⚠️ 第一步：强制 JSON 输出模式
        ResponseMIMEType: "application/json",

        // ⚠️ 第二步：以 map[string]any（原生 JSON Schema）定义输出结构
        // 与 ResponseSchema(*genai.Schema) 的区别：这里直接传 JSON Schema 规范格式。
        // 两者均触发约束解码，根据你的偏好选择即可。
        ResponseJsonSchema: map[string]any{
            "type": "object",
            "properties": map[string]any{
                "recipe_name": map[string]any{
                    "type":        "string",
                    "description": "菜谱名称",
                },
                "prep_time_minutes": map[string]any{
                    "type":        "integer",
                    "description": "准备时间（分钟），可选",
                },
                "ingredients": map[string]any{
                    "type": "array",
                    "items": map[string]any{
                        "type": "object",
                        "properties": map[string]any{
                            "name":     map[string]any{"type": "string"},
                            "quantity": map[string]any{"type": "string"},
                        },
                        "required": []string{"name", "quantity"},
                    },
                },
                "instructions": map[string]any{
                    "type":  "array",
                    "items": map[string]any{"type": "string"},
                },
            },
            "required": []string{"recipe_name", "ingredients", "instructions"},
        },
    }

    // ⚠️ 第三步：GenerateContent — 模型被约束为只能输出符合 Schema 的 JSON
    result, err := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash",
        genai.Text(prompt),
        config,
    )
    if err != nil {
        log.Fatal(err)
    }

    // result.Text() 保证是与 Schema 完全匹配的合法 JSON 字符串
    fmt.Println(result.Text())
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        String prompt = "请从以下文本中提取菜谱信息。\n" +
            "用户想要制作美味的巧克力芯片饼干。\n" +
            "需要 2 又 1/4 杯中筋面粉、1 茶匙小苏打...";

        // ⚠️ 第一步：强制 JSON 输出模式
        // ⚠️ 第二步：以 Map（原生 JSON Schema）定义输出结构
        GenerateContentConfig config = GenerateContentConfig.builder()
            .responseMimeType("application/json")
            .responseJsonSchema(Map.of(
                "type", "object",
                "properties", Map.of(
                    "recipe_name", Map.of("type", "string", "description", "菜谱名称"),
                    "prep_time_minutes", Map.of("type", "integer", "description", "准备时间（分钟），可选"),
                    "ingredients", Map.of(
                        "type", "array",
                        "items", Map.of(
                            "type", "object",
                            "properties", Map.of(
                                "name",     Map.of("type", "string"),
                                "quantity", Map.of("type", "string")
                            ),
                            "required", List.of("name", "quantity")
                        )
                    ),
                    "instructions", Map.of("type", "array", "items", Map.of("type", "string"))
                ),
                "required", List.of("recipe_name", "ingredients", "instructions")
            ))
            .build();

        // ⚠️ 第三步：GenerateContent — 模型被约束为只能输出符合 Schema 的 JSON
        GenerateContentResponse result = client.models.generateContent(
            "gemini-2.5-flash",
            prompt,
            config
        );
        System.out.println(result.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

**预期输出（保证符合 Schema 规范）：**
```json
{
  "recipe_name": "美味巧克力芯片饼干",
  "ingredients": [
    {"name": "中筋面粉", "quantity": "2 又 1/4 杯"},
    {"name": "小苏打", "quantity": "1 茶匙"}
  ],
  "instructions": [
    "预热烤箱至 190°C。",
    "将面粉、小苏打和盐搅拌均匀..."
  ]
}
```

---

### `ResponseSchema` vs `ResponseJsonSchema` — 如何选择？

| | `ResponseSchema` | `ResponseJsonSchema` |
|---|---|---|
| 输入类型 | `*genai.Schema`（强类型 Go 结构体）| `map[string]any`（原生 JSON Schema）|
| 约束解码 | ✅ | ✅ |
| 适合场景 | 有强类型 Go 模型时 | Schema 来自配置/数据库或动态生成时 |

---

### 支持的 JSON Schema 类型

| 类型 | 说明 |
|------|------|
| `string` | 支持 `enum`（固定枚举值）、`format`（date-time, date）|
| `number` | 浮点数；支持 `minimum`、`maximum`、`enum` |
| `integer` | 整数；支持 `minimum`、`maximum`、`enum` |
| `boolean` | `true`/`false` |
| `object` | 使用 `properties`、`required`、`additionalProperties` |
| `array` | 使用 `items`、`minItems`、`maxItems`、`prefixItems` |
| `null` | 通过 `{"type": ["string", "null"]}` 允许空值 |

在任意字段上使用 `description` 可引导模型精准提取对应内容。

---

### 最佳实践与限制

**最佳实践：**
- 每个字段都写 `description` — 这是引导提取精度的最主要手段
- 分类字段使用 `enum` 限制候选值集合
- prompt 里明确说明要做什么（"请从文本中提取以下字段..."）
- **在应用代码里始终进行业务语义校验** — 结构化输出只保证 JSON 语法合法，不保证业务逻辑正确

**限制：**
- 不支持的 JSON Schema 特性会被静默忽略
- 过大或深度嵌套的 Schema 可能被拒绝 — 尝试简化字段名、减少嵌套或减少约束条件
- 结构化输出支持大多数 Gemini 模型：`gemini-2.5-flash`、`gemini-2.5-pro`、`gemini-2.0-flash` 以及 Gemini 3 系列

---

## 六、结构化输出进阶专题

你可以配置 Gemini 模型，使其输出严格遵循指定 JSON Schema 的响应，从而获得可预期的、类型安全的结果，并简化从非结构化文本中提取数据的过程。

结构化输出的典型应用场景：

- **数据提取** — 从文本中精确抽取姓名、日期、金额等字段
- **结构化分类** — 将内容归入预定义的枚举类别
- **智能体工作流** — 为工具或 API 调用生成标准化的结构化输入

除了在 REST API 中直接使用 JSON Schema，Google GenAI SDK 还支持通过 Pydantic（Python）和 Zod（JavaScript）来定义 Schema。

### 菜谱提取示例（Go）

以下代码演示如何使用基本 JSON Schema 类型（`object`、`array`、`string`、`integer`）从文本中提取结构化数据：

{{< tabs >}}
{{< tab "Go" >}}
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
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `
  请从以下文本中提取菜谱信息。
  用户想要制作美味的巧克力芯片饼干。
  需要 2 又 1/4 杯中筋面粉、1 茶匙小苏打、1 茶匙盐、
  1 杯无盐黄油（软化）、3/4 杯白砂糖、3/4 杯红糖、
  1 茶匙香草精和 2 个大鸡蛋，以及 2 杯半甜巧克力豆。
  首先将烤箱预热至 190°C，混合干料，奶油打发后加入鸡蛋，
  逐步拌入干料，最后加入巧克力豆，烘烤 9 至 11 分钟。
  `
    config := &genai.GenerateContentConfig{
        ResponseMIMEType: "application/json",
        ResponseJsonSchema: map[string]any{
            "type": "object",
            "properties": map[string]any{
                "recipe_name": map[string]any{
                    "type":        "string",
                    "description": "菜谱名称",
                },
                "prep_time_minutes": map[string]any{
                    "type":        "integer",
                    "description": "准备时间（分钟），可选",
                },
                "ingredients": map[string]any{
                    "type": "array",
                    "items": map[string]any{
                        "type": "object",
                        "properties": map[string]any{
                            "name":     map[string]any{"type": "string", "description": "食材名称"},
                            "quantity": map[string]any{"type": "string", "description": "用量（含单位）"},
                        },
                        "required": []string{"name", "quantity"},
                    },
                },
                "instructions": map[string]any{
                    "type":  "array",
                    "items": map[string]any{"type": "string"},
                },
            },
            "required": []string{"recipe_name", "ingredients", "instructions"},
        },
    }

    result, err := client.Models.GenerateContent(
        ctx,
        "gemini-3-flash-preview",
        genai.Text(prompt),
        config,
    )
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(result.Text())
}
```
{{< /tab >}}

{{< tab "Java" >}}
```java
package main;

import com.google.genai.Client;
import com.google.genai.types.*;
import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        String prompt = "请从以下文本中提取菜谱信息。\n" +
            "用户想要制作美味的巧克力芯片饼干。\n" +
            "需要 2 又 1/4 杯中筋面粉、1 茶匙小苏打...";

        // ⚠️ 第一步：强制 JSON 输出模式
        // ⚠️ 第二步：以 Map（原生 JSON Schema）定义输出结构
        GenerateContentConfig config = GenerateContentConfig.builder()
            .responseMimeType("application/json")
            .responseJsonSchema(Map.of(
                "type", "object",
                "properties", Map.of(
                    "recipe_name", Map.of("type", "string", "description", "菜谱名称"),
                    "prep_time_minutes", Map.of("type", "integer", "description", "准备时间（分钟），可选"),
                    "ingredients", Map.of(
                        "type", "array",
                        "items", Map.of(
                            "type", "object",
                            "properties", Map.of(
                                "name",     Map.of("type", "string"),
                                "quantity", Map.of("type", "string")
                            ),
                            "required", List.of("name", "quantity")
                        )
                    ),
                    "instructions", Map.of("type", "array", "items", Map.of("type", "string"))
                ),
                "required", List.of("recipe_name", "ingredients", "instructions")
            ))
            .build();

        // ⚠️ 第三步：GenerateContent — 模型被约束为只能输出符合 Schema 的 JSON
        GenerateContentResponse result = client.models.generateContent(
            "gemini-2.5-flash",
            prompt,
            config
        );
        System.out.println(result.text());
    }
}
```
{{< /tab >}}
{{< /tabs >}}

---

### Streaming（流式输出）

你可以对结构化输出使用流式传输，无需等待整个响应生成完毕即可开始处理数据，从而改善应用的响应体验。

流式返回的每个 chunk 是合法的 **部分 JSON 字符串**，拼接所有 chunk 后即可得到完整的 JSON 对象。

```python
from google import genai
from pydantic import BaseModel, Field
from typing import Literal

class Feedback(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str

client = genai.Client()
prompt = "新 UI 直觉上非常流畅，视觉效果也很出色。干得漂亮！请添加一段较长的摘要以测试流式输出。"

response_stream = client.models.generate_content_stream(
    model="gemini-3-flash-preview",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Feedback.model_json_schema(),
    },
)

for chunk in response_stream:
    print(chunk.candidates[0].content.parts[0].text)
```

---

### 结构化输出与工具结合使用

> ⚠️ **预览功能**：仅支持 Gemini 3 系列模型（`gemini-3.1-pro-preview` 和 `gemini-3-flash-preview`）。

Gemini 3 支持同时使用结构化输出与内置工具，包括：**Google Search Grounding**、**URL Context**、**代码执行**、**文件搜索** 和 **函数调用**。

```python
from google import genai
from pydantic import BaseModel, Field
from typing import List

class MatchResult(BaseModel):
    winner: str = Field(description="获胜者名称")
    final_match_score: str = Field(description="最终比赛比分")
    scorers: List[str] = Field(description="进球者名单")

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="搜索最新一届欧洲杯的所有详细信息。",
    config={
        "tools": [
            {"google_search": {}},
            {"url_context": {}}
        ],
        "response_mime_type": "application/json",
        "response_json_schema": MatchResult.model_json_schema(),
    },
)

result = MatchResult.model_validate_json(response.text)
print(result)
```

---

### JSON Schema 支持详解

配置结构化输出时，在生成配置中将 `response_mime_type` 设为 `application/json`，并提供 `response_json_schema`。模型将生成一个符合该 Schema 的合法 JSON 字符串，输出字段顺序与 Schema 中的 key 顺序一致。

**支持的类型：**

- `string` — 文本
- `number` — 浮点数
- `integer` — 整数
- `boolean` — 布尔值（true/false）
- `object` — 键值对结构体
- `array` — 列表
- `null` — 允许某字段为空，使用 `{"type": ["string", "null"]}` 格式

**辅助描述属性：**

- `title` — 字段的简短描述
- `description` — 字段的详细说明（引导模型精准提取的最重要手段）

#### 各类型特有属性

**object：**
- `properties` — 各字段名对应的子 Schema
- `required` — 必须包含的字段列表
- `additionalProperties` — 是否允许额外字段（布尔值或子 Schema）

**string：**
- `enum` — 限定可选值集合（分类任务推荐）
- `format` — 格式约束，如 `date-time`、`date`、`time`

**number / integer：**
- `enum` — 限定可选数值集合
- `minimum` / `maximum` — 最小/最大值（含边界）

**array：**
- `items` — 数组元素的 Schema
- `prefixItems` — 前 N 项各自的 Schema（tuple 结构）
- `minItems` / `maxItems` — 最少/最多元素数量

---

### 模型支持情况

| 模型 | 支持结构化输出 |
|------|:---:|
| Gemini 3.1 Pro Preview | ✔️ |
| Gemini 3 Flash Preview | ✔️ |
| Gemini 2.5 Pro | ✔️ |
| Gemini 2.5 Flash | ✔️ |
| Gemini 2.5 Flash-Lite | ✔️ |
| Gemini 2.0 Flash | ✔️* |
| Gemini 2.0 Flash-Lite | ✔️* |

> *Gemini 2.0 需要在 JSON 输入中显式指定 `propertyOrdering` 列表来定义输出字段顺序。

---

### 结构化输出 vs. 函数调用

两者都使用 JSON Schema，但用途不同：

| 功能 | 主要用途 |
|------|---------|
| **结构化输出** | 格式化最终响应。适用于希望模型以特定格式输出答案的场景（如从文档中提取数据存入数据库） |
| **函数调用** | 在对话过程中触发操作。适用于模型需要你执行某个任务（如"获取当前天气"）后才能给出最终答案的场景 |

---

### 最佳实践

- **清晰的 description** — 为 Schema 中每个字段提供清晰的描述，这是引导模型精准提取的最关键手段
- **强类型约束** — 尽量使用具体类型（`integer`、`string`、`enum`），有限候选值的字段务必使用 `enum`
- **配合 Prompt 说明任务** — 在提示词中明确说明要做什么，例如"请从文本中提取以下字段……"或"请按照提供的 Schema 对反馈进行分类……"
- **业务语义校验不可省** — 结构化输出只保证 JSON 语法合法，不保证值在业务逻辑上正确，应用层必须自行校验
- **健壮的错误处理** — 即使输出符合 Schema，也可能不满足业务逻辑要求，需做好异常处理

### 限制

- Schema 子集：并非所有 JSON Schema 特性都受支持，不支持的属性会被静默忽略
- 过大或深度嵌套的 Schema 可能被拒绝，尝试简化结构
- 结构化输出与流式输出同时使用时，每个 chunk 是部分 JSON，需全部拼接后才得到完整合法的 JSON
