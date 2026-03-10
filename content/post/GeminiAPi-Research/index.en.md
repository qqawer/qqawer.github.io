---
title: "Deep Dive into Gemini API: Advanced Practical Guide"
description: "A comprehensive guide to the core features, environment setup, and code implementation of the Gemini API. Covers the Files API reuse strategies, GCS integration, and more to help you master Google's most powerful AI model."
date: 2026-03-06
slug: "gemini-api-research"
categories:
    - Documentation
tags:
    - AI
    - Gemini
    - Go
    - Development
toc: true
---

# Gemini API Quickstart

## 1. Install Google GenAI SDK

Run the following commands in your project's module directory:

```bash
go get google.golang.org/genai
go get google.golang.org/api
go get golang.org/x/oauth2/google
go get cloud.google.com/go/storage
```

## 2. Environment Setup: Setting the API Key

The client automatically reads the `GEMINI_API_KEY` system environment variable upon initialization. All official Gemini API example code assumes you have this variable set up.

### Temporary Setup (Current Terminal Only)

```bash
# macOS/Linux (Terminal)
export GEMINI_API_KEY="[ENCRYPTION_KEY]"

# Windows (Command Prompt)
set GEMINI_API_KEY="[ENCRYPTION_KEY]"

# Windows (PowerShell)
$env:GEMINI_API_KEY="[ENCRYPTION_KEY]"
```

### Permanent Setup (Recommended)

```bash
# macOS
nano ~/.zshrc
# Append: export GEMINI_API_KEY="[ENCRYPTION_KEY]"
source ~/.zshrc

# Linux
# Edit ~/.bashrc file, append: export GEMINI_API_KEY="[ENCRYPTION_KEY]"
source ~/.bashrc

# Windows
# Search "Environment Variables" -> System Environment Variables -> New System Variable:
# Variable Name: GEMINI_API_KEY
# Variable Value: [ENCRYPTION_KEY]
```

---

## 3. Make Your First Request

The following example demonstrates how to call the Gemini 2.5 Flash model to send a basic text request using the `GenerateContent` method.

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

---

# Advanced: File Input Methods

All Gemini API endpoints (including Batch, Interactions, and Live API) natively support multi-modal inputs (PDFs, images, videos, etc.). You can read from a local file and include it in your prompt, or upload large files via the API.

## I. Comparison of Input Methods

| Method | Best Use Case | Max File Size | Persistence / Caching |
|--------|---------------|---------------|-----------------------|
| **Inline data** | Quick tests, small local files, real-time | 100 MB per payload<br>(PDFs ≤ 50 MB) | None (Requires complete re-transfer each request) |
| **File API upload** | Large videos, long audio, documents requiring multiple queries | 2 GB per file,<br>20 GB per project | Retained in cloud for 48 hours (auto-deleted), no downloads |
| **GCS URI Reg.** | Massive object datasets already stored in Google Cloud Storage (GCS) | 2 GB per file, Project limit based on GCS Bucket | Unlimited storage, single registration yields up to 30 days access |
| **External URLs** | AWS/Azure Pre-signed URLs (SAS) or public HTTPS | 100 MB per payload | None (Models pull the link in real-time) |

---

## II. Core Go Implementations

Below are the **completely independent, runnable Go code examples** for all four strategies, containing all necessary module imports and client initializations.

### 1. Inline Data - Directly Uploading Small Local Files

This is the simplest input method. Suitable for small files (PDF ≤ 50MB, others ≤ 100MB).

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

	// Initialize the Gemini Client
	client, err := genai.NewClient(ctx, option.WithAPIKey(""))
	if err != nil {
		log.Fatalf("Client creation failed: %v", err)
	}
	defer client.Close()

	// Read local PDF
	filePath := "my_local_file.pdf"
	fileBytes, err := ioutil.ReadFile(filePath)
	if err != nil {
		log.Fatalf("Failed to read file: %v", err)
	}

	model := client.GenerativeModel("gemini-2.5-flash")

	// Build multimodal content (Binary blob + prompt)
	contents := []genai.Part{
		genai.Blob("application/pdf", fileBytes), 
		genai.Text("Summarize this document"),    
	}

	// Dispatch API Call
	resp, err := model.GenerateContent(ctx, contents...)
	if err != nil {
		log.Fatalf("API call failed: %v", err)
	}

	printResponse(resp)
}

// Universal Response Printer
func printResponse(resp *genai.GenerateContentResponse) {
	if len(resp.Candidates) == 0 {
		log.Println("No response results")
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

### 2. GCS URI Reg. (Google Cloud Storage)

Useful for colossal files already hosted in GCP, sidestepping local parsing and slow re-uploads.

#### Prerequisites: GCP IAM CLI Configuration
Your Gemini service agent must explicitly own `Storage Object Viewer` authority:
```bash
# 1. Spawn a dedicated service identity
gcloud beta services identity create --service=generativelanguage.googleapis.com --project=<YOUR_PROJECT_ID>

# 2. Grant permissions
gcloud storage buckets add-iam-policy-binding gs://<YOUR_BUCKET> \
  --member="serviceAccount:service-<PROJECT_NUMBER>@gcp-sa-generativelanguage.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

#### Go Code Implementation
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

// Attempt to acquire GCS access credentials
func getGCSCredentials(ctx context.Context) (*google.Credentials, error) {
	// Scenario 1: External Environment (Requires Service Account JSON key)
	creds, err := google.CredentialsFromJSON(ctx, nil,
		"https://www.googleapis.com/auth/devstorage.read_only",
		"https://www.googleapis.com/auth/cloud-platform",
	)
	if err != nil {
		// Scenario 2: GCP Internal Execution (Cloud Run) - Automatic credentials
		creds, err = google.FindDefaultCredentials(ctx,
			"https://www.googleapis.com/auth/devstorage.read_only",
			"https://www.googleapis.com/auth/cloud-platform",
		)
		if err != nil {
			return nil, fmt.Errorf("Credential fetch failed: %v", err)
		}
	}
	return creds, nil
}

func main() {
	ctx := context.Background()

	// 1. Fetch Credentials
	creds, err := getGCSCredentials(ctx)
	if err != nil {
		log.Fatalf("Credential fetch failed: %v", err)
	}

	// 2. Initialize Client (Requires API Key AND GCS Credentials simultaneously)
	geminiClient, err := genai.NewClient(ctx, option.WithAPIKey(""), option.WithCredentials(creds))
	if err != nil {
		log.Fatalf("Client creation failed: %v", err)
	}
	defer geminiClient.Close()

	gcsURIs := []string{"gs://my_bucket/some_object.pdf"}
	model := geminiClient.GenerativeModel("gemini-2.5-flash")
	prompt := "Summarize this file."

	for _, uri := range gcsURIs {
		fmt.Printf("Processing URI: %s\n", uri)
		// Load object directly from GCS URI
		contents := []genai.Part{
			genai.Text(prompt),
			genai.BlobFromURI(uri, "application/pdf"), 
		}

		resp, err := model.GenerateContent(ctx, contents...)
		if err != nil {
			log.Printf("Failed decoding %s: %v", uri, err)
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

Optimal for fast ingestion via public HTTPS or Pre-signed URLs (S3/Azure SAS). Must be ≤ 100MB.
*(Note: Gemini 2.0 might restrict external curl crawls, so we revert to 1.5-flash here)*

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
		log.Fatalf("Client creation failed: %v", err)
	}
	defer client.Close()

	externalURI := "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf"
	
	// Recommend fallback versions for aggressive crawling
	model := client.GenerativeModel("gemini-1.5-flash")

	contents := []genai.Part{
		genai.BlobFromURI(externalURI, "application/pdf"), 
		genai.Text("Summarize this external file"),
	}

	resp, err := model.GenerateContent(ctx, contents...)
	if err != nil {
		log.Fatalf("API Call failure: %v", err)
	}

	printResponse(resp)
}

func printResponse(resp *genai.GenerateContentResponse) {
	if len(resp.Candidates) == 0 {
		log.Println("No response results")
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

## III. Files API Deep Reuse Strategy

When files breach **100 MB** total, or PDFs surpass **50 MB**, the **Files API** is unavoidable. The primary benefit lies in **Caching Logic**: Upload a massive file once to capture a unique `File ID`, then repeatedly inject that ID into new prompts over the next 48 hours without enduring large network overheads.

### Files API Basic Operations Snippets

```go
// Upload and capture the designated File memory object
file, err := client.Files.UploadFromPath(ctx, "path/to/sample.mp3", nil)

// Retrieve file metadata limits
gotFile, err := client.Files.Get(ctx, file.Name)

// Range and iterate through all cached files inside your GCP Project
for fileData, err := range client.Files.All(ctx) {
  fmt.Println(fileData.Name)
}

// Manually trigger garbage collection
client.Files.Delete(ctx, file.Name)
```

### Scenario 1: Upload Multiple PDFs, Execute Prompts Independently (Common)

Perfect for queuing up invoices or contracts into the cloud, then systematically querying each one individually.

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
		log.Fatalf("Client init failed: %v", err)
	}
	defer client.Close()

	// 1. Array of target PDFs
	pdfFiles := []string{"docs/invoice1.pdf", "docs/contract2.pdf"}
	fileIDs := make(map[string]string) // String Map: Path -> File ID

	// 2. Transmit and register IDs
	for _, filePath := range pdfFiles {
		file, err := client.Files.UploadFromPath(ctx, filePath, nil)
		if err != nil {
			log.Printf("Upload crash %s: %v", filePath, err)
			continue
		}
		fileIDs[filePath] = file.Name
		fmt.Printf("File %s cached with ID: %s\n", filePath, file.Name)
		// We purposefully do not trigger defer deletes yet to reuse IDs
	}

	// 3. First Query Layer: Utilizing the saved File IDs
	fmt.Println("\n=== First Query (File Parsing) ===")
	for filePath, fileID := range fileIDs {
		content := &genai.Content{
			Parts: []*genai.Part{
				genai.NewPartFromFile(genai.File{Name: fileID}), // Reference cached ID
				genai.NewPartFromText("Extract critical KPIs mapping to strict JSON variables."),
			},
		}

		resp, err := client.Models.GenerateContent(ctx, "gemini-2.5-flash", []*genai.Content{content}, nil)
		if err != nil {
			log.Printf("Parsing failed: %v", err)
			continue
		}
		fmt.Printf("Parsed results array for %s:\n", filePath)
		printResponse(resp)
	}

	// 4. Second Query Layer: Resubmitting the same File ID, altering the Text Input
	fmt.Println("\n=== Second Query (Recycling File IDs for Summaries) ===")
	for filePath, fileID := range fileIDs {
		content := &genai.Content{
			Parts: []*genai.Part{
				genai.NewPartFromFile(genai.File{Name: fileID}), // Avoids reuploading huge files
				genai.NewPartFromText("Summarize core concepts under 200 words."),
			},
		}
		resp, err := client.Models.GenerateContent(ctx, "gemini-2.5-flash", []*genai.Content{content}, nil)
		if err != nil {
			continue
		}
		printResponse(resp)
	}

	// 5. Explicit GC Execution
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

### Scenario 2: Batch Upload and Merge Prompts (Cross-Logic Analysis)

Instead of looping IDs, we aggregate all `File ID`s into a singular multi-dimensional prompt structure to invoke cross-logical comparisons.

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
		log.Fatalf("Client startup crash: %v", err)
	}
	defer client.Close()

	// 1. Batch document ingestion
	pdfPaths := []string{"docs/file1.pdf", "docs/file2.pdf"}
	var uploadedFiles []genai.File

	for _, path := range pdfPaths {
		file, err := client.Files.UploadFromPath(ctx, path, nil)
		if err != nil {
			log.Fatalf("File injection failed: %v", err)
		}
		uploadedFiles = append(uploadedFiles, *file)
		defer client.Files.Delete(ctx, file.Name) // Auto-scrub upon application close
	}

	// 2. Compile Cross-Logic Payload
	var parts []*genai.Part
	for _, file := range uploadedFiles {
		parts = append(parts, genai.NewPartFromFile(file))
	}
	parts = append(parts, genai.NewPartFromText("Review these two PDFs. Identify and isolate overlapping common metrics, output standard GitHub markdown constraints."))

	// 3. Dispatch the Consolidated Array Request
	resp, err := client.Models.GenerateContent(ctx, "gemini-2.5-flash", []*genai.Content{{Parts: parts}}, nil)
	if err != nil {
		log.Fatalf("Comparison dispatcher failure: %v", err)
	}

	fmt.Println("Multi-File Comparison Results:")
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

## IV. Prompt Engineering Best Practices 

### Fundamentals of Multi-modal Prompting
- **Specificity**: Never be ambiguous. Instruct the model precisely on operational pipelines.
- **Implement Few-Shot Constraints**: Inject hardcoded expected responses to force compliance.
- **Enforce Return Syntax**: Manually instruct string types (`markdown`, `JSON`, `HTML`).
- **Images Take Priority**: When pushing blob data, position image `genai.Blob` wrappers sequentially *before* the prompt strings `genai.Text`. Visual processing neurons execute top-down effectively.

### Remediation & Troubleshooting
1. **Model hallucinating incorrect sectors**: Edit internal prompt texts explicitly denoting positions ("Identify numerals strictly embedded within the top right financial column chart.")
2. **Output lacks structural depth**: Adopt a dual-query layered architecture. Advise the model to formally observe the visual evidence inside paragraph 1 ("Describe purely what shapes you are observing first"), and only construct an answer derived from the observations in paragraph 2. 
3. **Infinite Hallucination loops**: 
   - Strict metric extraction (like JSON parsing financial tables) benefits heavily from minimal deviation. Lower `Temperature` ranges heavily.
   - For creative aggregation or preventing systemic lockups (crashing on single questions), rebound the `Temperature` back toward Google's default threshold of `1.0`. 
4. **Context Saturation Limits**: The `Files API` thrives structurally uploading 50 files. But for direct prompt injections, cap specific questions mapping to roughly 5 simultaneous PDFs. Flooding prompts erases early-injected context rulesides.



# Advanced: Context Caching

In a typical AI workflow, you might pass the same input tokens over and over to a model. The Gemini API offers two caching mechanisms to reduce costs:

## 1. Implicit Caching (Automatic)

Implicit caching is enabled by default. If you send similar large prompts within a short amount of time, the system automatically caches them, and the cost savings are passed on to you.
- **Cost Saving**: Automatic, but no guaranteed hit.
- **Min Token Limits**:
  - `gemini-2.5-flash` / `gemini-3-flash-preview`: **1024 tokens**
  - `gemini-2.5-pro` / `gemini-3.1-pro-preview`: **4096 tokens**
- **How to verify**: You can see the number of tokens which were cache hits in the response object's `usage_metadata` field.

## 2. Explicit Caching (Manual)

Explicit caching allows you to manually cache a set of tokens for a specific Time-To-Live (TTL, defaults to 1 hour). This guarantees lower costs when passing the same corpus of tokens repeatedly.

### When to use Explicit Caching:
- Chatbots with extensive system instructions.
- Repetitive analysis of the exact same lengthy video, audio, or PDF files.
- Frequent code repository analysis across multiple distinct user prompts.

### Code Example: Explicit Caching in Go

Here is how you create and use an explicit cache. Pay close attention to the code comments highlighting where the caching actually happens.

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
	
	// 1. Upload your large file normally via Files API
	document, err := client.Files.UploadFromPath(ctx, "docs/large_transcript.txt", nil)
	if err != nil { log.Fatal(err) }

	parts := []*genai.Part{ genai.NewPartFromURI(document.URI, document.MIMEType) }
	contents := []*genai.Content{ genai.NewContentFromParts(parts, genai.RoleUser) }

	// =====================================================================
	// 2. CREATE THE CACHE (⚠️ CACHING LOGIC HERE)
	// Instead of calling GenerateContent directly, we create a Cache object.
	// We bind the uploaded document and the system instruction to this cache.
	// =====================================================================
	cache, err := client.Caches.Create(ctx, modelName, &genai.CreateCachedContentConfig{
		Contents: contents,
		SystemInstruction: genai.NewContentFromText("You are an expert analyzing transcripts.", genai.RoleUser),
		TTL: 3600 * time.Second, // Cache lives for 1 hour
	})
	if err != nil { log.Fatal(err) }
	
	fmt.Println("Cache successfully created! Cache Name:", cache.Name)

	// =====================================================================
	// 3. USE THE CACHE (⚠️ CACHING LOGIC HERE)
	// We pass the cached content's name into GenerateContentConfig.
	// The model will automatically inject the huge file we cached above,
	// only consuming cheaper "Context Cached" tokens.
	// =====================================================================
	fmt.Println("\n--- Query 1 ---")
	resp1, err := client.Models.GenerateContent(
		ctx,
		modelName,
		genai.Text("Please summarize this transcript"),
		&genai.GenerateContentConfig{
			CachedContent: cache.Name, // Explicitly linking the Cache ID!
		},
	)
	if err != nil { log.Fatal(err) }
	printResponse(resp1) 

	// =====================================================================
	// 4. REUSE THE SAME CACHE (⚠️ MULTIPLE HITS)
	// You can reuse this exact same cache without re-uploading the file
	// as many times as you want before the TTL expires.
	// =====================================================================
	fmt.Println("\n--- Query 2 ---")
	resp2, err := client.Models.GenerateContent(
		ctx,
		modelName,
		genai.Text("Extract all financial decisions made in this transcript."),
		&genai.GenerateContentConfig{
			CachedContent: cache.Name, // Reusing the exact same cache
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

### Cache Lifecycle Management (Full Code)

You cannot download the cached content itself, but you can manage its metadata (like `name`, `model`, `display_name`, `usage_metadata`, `expire_time`) and lifecycle:

#### 1. List Caches

You can list all available caches in your project, either all at once or via pagination:

```go
// List all caches simply
caches, err := client.Caches.All(ctx)
if err != nil {
    log.Fatal(err)
}
fmt.Println("Listing all caches:")
for _, item := range caches {
    fmt.Println("   ", item.Name)
}

// List caches using pagination (Page size = 2)
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

#### 2. Update a Cache (TTL)

You can only update the expiration time (`ttl` or `expire_time`) of a cache. Modifying the actual cached files or prompt instructions is not permitted.

```go
// Update the TTL (2 hours / 7200 seconds)
cache, err = client.Caches.Update(ctx, cache.Name, &genai.UpdateCachedContentConfig{
    TTL: 7200 * time.Second,
})
if err != nil {
    log.Fatal(err)
}
fmt.Println("After update:")
fmt.Println(cache)
```

#### 3. Delete a Cache

If you are completely finished with your queries, it is highly recommended to manually delete the cache immediately to prevent unnecessary storage billing:

```go
_, err = client.Caches.Delete(ctx, cache.Name, &genai.DeleteCachedContentConfig{})
if err != nil {
    log.Fatal(err)
}
fmt.Println("Cache deleted:", cache.Name)
```

---

## Practical Scenario 3: Caching Long Prompt Templates (Per Document Type)

**Background**: You have multiple document types (invoices, bills of lading, contracts, etc.). Each type has a correspondingly **very long** extraction instruction (JSON Schema + validation rules + few-shot examples) that is **fixed and never changes**. For the same document type, every request sends the same long prompt, but the actual document file differs each time.

> **Key Concept Reversal**:
> - **Scenario 1**: Cache the **large file**, swap the prompt each time → Best for querying one document multiple times
> - **This Scenario**: Cache the **long prompt template**, swap the file each time → Best for batch-processing different files of the same type

### Design Overview

```
【What's inside the cache】
└── SystemInstruction: "You are a professional document parsing engine..."
└── Contents:          [Very long JSON Schema + Few-Shot examples + extraction rules]  ← Fixed per doc type, very long

【What's sent fresh with each GenerateContent call】
└── CachedContent:  The cache name for the matching document type
└── Fresh content:  The actual document file for this specific request
```

### Full Go Implementation

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

// Very long prompt template (Invoice type)
// ❗ NOTE: The role/persona is already declared in SystemInstruction above.
// Only put task-specific instructions here: JSON Schema, field rules, few-shot examples.
const invoicePromptTemplate = `

## Output Format (must be valid JSON)
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

## Extraction Rules
- Convert all dates to YYYY-MM-DD format
- Convert all monetary values to numeric, stripping currency symbols
- If a field doesn't exist, set it to null — never omit the key
- Extract ALL line items without exception
...（abbreviated — the actual prompt can be thousands of tokens long）
`

// Registry of document-type caches
type DocTypeCache struct {
	CacheName string
}

// Build and cache the prompt template for a given document type (called once at startup)
func buildPromptCache(ctx context.Context, client *genai.Client, modelName, docType, promptTemplate string) (*DocTypeCache, error) {
	// =====================================================================
	// KEY: We cache the long prompt template itself as Contents.
	// SystemInstruction + long prompt = tokens saved on every subsequent request.
	// =====================================================================
	promptParts := []*genai.Part{genai.NewPartFromText(promptTemplate)}
	promptContent := []*genai.Content{genai.NewContentFromParts(promptParts, genai.RoleUser)}

	cache, err := client.Caches.Create(ctx, modelName, &genai.CreateCachedContentConfig{
		Contents: promptContent,
		SystemInstruction: genai.NewContentFromText(
			"You are a professional document parsing engine. Follow the cached instructions strictly and output valid JSON.",
			genai.RoleUser,
		),
		TTL: 24 * 3600 * time.Second, // Rebuild once per day
	})
	if err != nil {
		return nil, fmt.Errorf("[%s] cache creation failed: %v", docType, err)
	}
	fmt.Printf("[%s] Prompt template cached successfully: %s\n", docType, cache.Name)
	return &DocTypeCache{CacheName: cache.Name}, nil
}

// Process a single document using the pre-cached prompt template
func processDocument(ctx context.Context, client *genai.Client, modelName string, cache *DocTypeCache, filePath string) {
	// Upload the actual document file for this request (changes every time)
	document, err := client.Files.UploadFromPath(ctx, filePath, nil)
	if err != nil {
		log.Printf("Upload failed [%s]: %v", filePath, err)
		return
	}
	defer client.Files.Delete(ctx, document.Name)

	// =====================================================================
	// Each GenerateContent call:
	//   - CachedContent = the cached long prompt template (⚠️ CACHE HIT — cheap tokens)
	//   - Fresh content  = the actual document file for this request (⚠️ normal billing)
	// =====================================================================
	resp, err := client.Models.GenerateContent(
		ctx,
		modelName,
		genai.NewPartFromURI(document.URI, document.MIMEType), // Only the file — prompt is already cached
		&genai.GenerateContentConfig{
			CachedContent: cache.CacheName, // Reference the correct doc-type cache
		},
	)
	if err != nil {
		log.Printf("Parsing failed [%s]: %v", filePath, err)
		return
	}

	fmt.Printf("\n=== Parsed Result [%s] ===\n", filePath)
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

	// 1. Build one cache per document type at startup (only once)
	invoiceCache, err := buildPromptCache(ctx, client, modelName, "invoice", invoicePromptTemplate)
	if err != nil { log.Fatal(err) }
	defer client.Caches.Delete(ctx, invoiceCache.CacheName, &genai.DeleteCachedContentConfig{})

	// billOfLadingCache, _ := buildPromptCache(ctx, client, modelName, "bol", bolPromptTemplate)
	// contractCache, _     := buildPromptCache(ctx, client, modelName, "contract", contractPromptTemplate)

	// 2. Batch-process a list of invoice files — each file hits the same cache
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

### Cost Comparison

| Strategy | Tokens sent per request | Best For |
|----------|-------------------------|----------|
| No caching | File + full prompt (every time) | Infrequent / one-off requests |
| **Cache long prompt** (this scenario) | File (normal rate) + Prompt (cached, ~75% discount) | Batching many files of the same type |
| Cache large file (Scenario 1) | Prompt (normal rate) + File (cached, ~75% discount) | Querying the same file multiple times |

---

## Practical Scenario 4: ResponseSchema Structured Output (JSON Schema Uses Zero Prompt Tokens)

**The Problem**: A large JSON Schema embedded inside the prompt causes two issues:
1. **Massive token consumption** — the schema itself can be thousands of tokens
2. **No JSON correctness guarantee** — the model only "references" your schema text; it can still produce malformed JSON

**The Solution**: `GenerateContentConfig.ResponseSchema` + `ResponseMIMEType: "application/json"`

This is Gemini's **Structured Output** feature. The schema is passed as a constraint to the inference engine — it **does not count toward prompt tokens at all** — and the model uses **Constrained Decoding** at the grammar level to **enforce valid JSON output** every single time.

### Comparison: Two Approaches

| | Schema in the Prompt | ResponseSchema |
|---|---|---|
| Schema token cost | ❌ Counts as prompt tokens (expensive) | ✅ Zero prompt tokens |
| JSON validity guarantee | ❌ Model "references" it, can still produce malformed output | ✅ Constrained decoding enforces validity at grammar level |
| Schema / prompt decoupling | ❌ Mixed together, hard to maintain | ✅ Completely separate, clean code |
| Works with Context Caching | ✅ | ✅ |

### Go Implementation

```go
package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/genai"
	"google.golang.org/api/option"
)

// Define the ResponseSchema per document type in Go code — not in the prompt text
var invoiceSchema = &genai.Schema{
	Type: genai.TypeObject,
	Properties: map[string]*genai.Schema{
		"invoice_number": {Type: genai.TypeString},
		"invoice_date":   {Type: genai.TypeString, Description: "Format: YYYY-MM-DD"},
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

// Each document type can have a completely different (concise) prompt
// No need to paste the JSON Schema into the prompt text anymore
var docTypePrompts = map[string]string{
	"invoice":  "Extract all key fields from this invoice, including seller, buyer, amounts, and all line items.",
	"bol":      "Extract all shipping information from this bill of lading, including shipper, consignee, cargo description, and routing.",
	"contract": "Extract the contract number, parties, effective date, expiry date, and a summary of core terms.",
}

var docTypeSchemas = map[string]*genai.Schema{
	"invoice": invoiceSchema,
	// "bol":      billOfLadingSchema,
	// "contract": contractSchema,
}

func processWithSchema(ctx context.Context, client *genai.Client, modelName, docType, filePath string) {
	schema := docTypeSchemas[docType]
	prompt := docTypePrompts[docType]

	document, err := client.Files.UploadFromPath(ctx, filePath, nil)
	if err != nil { log.Fatal(err) }
	defer client.Files.Delete(ctx, document.Name)

	resp, err := client.Models.GenerateContent(
		ctx,
		modelName,
		[]*genai.Content{{
			Parts: []*genai.Part{
				genai.NewPartFromURI(document.URI, document.MIMEType),
				genai.NewPartFromText(prompt), // Concise prompt — no schema text
			},
		}},
		&genai.GenerateContentConfig{
			// =====================================================================
			// ⚠️ KEY: Schema passed here — consumes ZERO prompt tokens
			// Constrained decoding makes it IMPOSSIBLE to output malformed JSON
			// =====================================================================
			ResponseMIMEType: "application/json",
			ResponseSchema:   schema,
		},
	)
	if err != nil { log.Fatal(err) }

	// Directly use the guaranteed-valid JSON string
	fmt.Printf("[%s] Result:\n%s\n", filePath, resp.Text())
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

### Optimal Combination: ResponseSchema + Context Caching

These two features are completely compatible and work perfectly together:

```
【What's in the cache】
└── SystemInstruction: "You are a professional document parsing engine"
└── Contents:          [Descriptive prompt for this document type — no schema text needed]

【Each GenerateContent call】
└── CachedContent:    Cache name for the matching document type
└── Fresh content:    The actual document file
└── ResponseSchema:   Go-defined schema (zero prompt tokens, constrained decoding)
```

```go
// Optimal final architecture
resp, err := client.Models.GenerateContent(
	ctx,
	modelName,
	genai.NewPartFromURI(document.URI, document.MIMEType),
	&genai.GenerateContentConfig{
		CachedContent:    invoiceCache.CacheName, // Cache hit: descriptive prompt
		ResponseMIMEType: "application/json",
		ResponseSchema:   invoiceSchema,           // Schema: zero tokens, constrained output
	},
)
```

### Summary: What Goes Where?

| Content | Where | Why |
|---------|-------|-----|
| Role declaration ("You are a parsing engine") | `SystemInstruction` | High priority, short |
| Descriptive task prompt ("Extract invoice fields, pay attention to...") | `Contents` (cacheable) | Semantic description, varies by doc type |
| JSON Schema structure definition | `ResponseSchema` | Zero prompt tokens, constrained decoding guarantees valid JSON |
| Actual document file | Fresh `Contents` each call | Different every time |

---

# Document Understanding: PDF Processing in Depth

Gemini processes PDFs using **native vision** — it reads the document as a human would, understanding not just text but also images, diagrams, charts, tables, and layout across up to **1000 pages**. This is fundamentally different from traditional OCR: Gemini understands context and structure.

**Key capabilities:**
- Extract data into structured output (JSON, tables)
- Summarize and answer questions based on visual + textual elements
- Transcribe documents preserving layout/formatting for downstream apps

> ⚠️ Non-PDF types (TXT, HTML, Markdown, XML) are supported but are extracted as **plain text only** — charts, diagrams, and formatting are lost.

---

## Method 1: Inline Data (Small PDFs, ≤ 50 MB)

Best for one-off requests on small documents. The raw file bytes are embedded directly in the request payload.

### From URL

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

    // 1. Fetch the PDF bytes from a URL
    pdfResp, _ := http.Get("https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf")
    pdfBytes, _ := io.ReadAll(pdfResp.Body)
    pdfResp.Body.Close()

    parts := []*genai.Part{
        // ⚠️ INLINE DATA: raw bytes go directly into the request (no upload step)
        {InlineData: &genai.Blob{
            MIMEType: "application/pdf",
            Data:     pdfBytes,
        }},
        genai.NewPartFromText("Summarize this document"),
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

### From Local File

```go
// Same structure — just read bytes from disk instead of HTTP
pdfBytes, _ := os.ReadFile("path/to/your/file.pdf")

parts := []*genai.Part{
    // ⚠️ INLINE DATA: local bytes embedded directly — fast but not reusable
    {InlineData: &genai.Blob{MIMEType: "application/pdf", Data: pdfBytes}},
    genai.NewPartFromText("Summarize this document"),
}
```

---

## Method 2: Files API Upload (Large PDFs, Reusable)

Use the Files API when:
- File size > 50 MB, or combined payload > 100 MB
- You need to query the same document multiple times (saves bandwidth, reduces latency)
- Files are stored for **48 hours** at no cost

### From URL (Download → Upload → Query)

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

    // 1. Download the PDF locally
    pdfURL := "https://www.nasa.gov/wp-content/uploads/static/history/alsj/a17/A17_FlightPlan.pdf"
    localPath := "A17_FlightPlan_downloaded.pdf"
    respHttp, _ := http.Get(pdfURL)
    defer respHttp.Body.Close()
    outFile, _ := os.Create(localPath)
    io.Copy(outFile, respHttp.Body)
    outFile.Close()

    // ⚠️ FILES API UPLOAD: file stored in Google's servers for 48h
    // Returns a URI you can reuse in multiple GenerateContent calls
    uploadedFile, _ := client.Files.UploadFromPath(ctx, localPath,
        &genai.UploadFileConfig{MIMEType: "application/pdf"},
    )

    promptParts := []*genai.Part{
        // ⚠️ REFERENCE BY URI: no re-uploading, model fetches from cache
        genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
        genai.NewPartFromText("Summarize this document"),
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

### From Local File (Direct Upload)

```go
// ⚠️ FILES API UPLOAD: upload local PDF to Google's servers
uploadedFile, _ := client.Files.UploadFromPath(ctx, "/path/to/file.pdf",
    &genai.UploadFileConfig{MIMEType: "application/pdf"},
)

// ⚠️ REFERENCE BY URI: pass the returned URI to the model
promptParts := []*genai.Part{
    genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
    genai.NewPartFromText("Give me a summary of this PDF file."),
}
```

---

## Method 3: Multiple PDFs in One Request

Gemini can analyze up to **1000 pages** across multiple documents in a single request, as long as the combined size stays within the model's context window. Ideal for cross-document comparison.

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

    // Download the two papers
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

    // ⚠️ UPLOAD BOTH FILES separately via Files API
    file1, _ := client.Files.UploadFromPath(ctx, "doc1_downloaded.pdf",
        &genai.UploadFileConfig{MIMEType: "application/pdf"})
    file2, _ := client.Files.UploadFromPath(ctx, "doc2_downloaded.pdf",
        &genai.UploadFileConfig{MIMEType: "application/pdf"})

    promptParts := []*genai.Part{
        // ⚠️ BOTH FILE URIs in the same Parts array — Gemini reads them together
        genai.NewPartFromURI(file1.URI, file1.MIMEType),
        genai.NewPartFromURI(file2.URI, file2.MIMEType),
        genai.NewPartFromText("Compare the main benchmark results between these two papers. Output a table."),
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

---

## Technical Limits & Tips

| Dimension | Limit / Detail |
|-----------|----------------|
| Max file size | 50 MB (inline) / 2 GB (Files API) |
| Max pages | 1000 pages per request |
| Token cost per page | 258 tokens |
| Page resolution | Scaled to max 3072×3072 (no discount for lower res) |
| Storage (Files API) | 48 hours, free |

**Best practices:**
- Rotate pages to correct orientation before uploading
- Avoid blurry or low-contrast scans
- For single-page documents, place the text prompt **after** the page part
- Use Files API for anything you need to query more than once

---

# Structured Outputs: Guaranteed JSON Schema Compliance

Structured outputs let you configure Gemini to always return responses that match a provided JSON Schema — enforced at the grammar level via **constrained decoding**.

**Ideal for:**
- **Data extraction** — pull specific fields (names, dates, amounts) from unstructured text
- **Classification** — categorize documents into predefined enum values
- **Agentic workflows** — generate structured inputs for tools or APIs

> **Note**: This differs from `ResponseSchema` used in earlier scenarios in one way — you can also pass the schema as raw `map[string]any` JSON Schema (`ResponseJsonSchema`) instead of the typed `*genai.Schema` Go struct. Both approaches achieve the same constrained decoding result.

---

## Go Example: Recipe Extraction

This demonstrates using `ResponseJsonSchema` (raw JSON Schema as `map[string]any`) to extract structured recipe data from free-form text.

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
    // Uses GEMINI_API_KEY env var automatically
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `Please extract the recipe from the following text.
The user wants to make delicious chocolate chip cookies.
They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda...`

    config := &genai.GenerateContentConfig{
        // ⚠️ STEP 1: Force JSON output mode
        ResponseMIMEType: "application/json",

        // ⚠️ STEP 2: Define the schema as raw map[string]any (JSON Schema spec)
        // Unlike ResponseSchema (*genai.Schema), this accepts raw JSON Schema directly.
        // Both achieve the same constrained decoding — choose based on your preference.
        ResponseJsonSchema: map[string]any{
            "type": "object",
            "properties": map[string]any{
                "recipe_name": map[string]any{
                    "type":        "string",
                    "description": "The name of the recipe.",
                },
                "prep_time_minutes": map[string]any{
                    "type":        "integer",
                    "description": "Optional prep time in minutes.",
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

    // ⚠️ STEP 3: GenerateContent — model is constrained to output valid JSON
    result, err := client.Models.GenerateContent(
        ctx,
        "gemini-2.5-flash",
        genai.Text(prompt),
        config,
    )
    if err != nil {
        log.Fatal(err)
    }

    // result.Text() is guaranteed to be a valid JSON string matching the schema
    fmt.Println(result.Text())
}
```

**Expected output (guaranteed schema-compliant):**
```json
{
  "recipe_name": "Delicious Chocolate Chip Cookies",
  "ingredients": [
    {"name": "all-purpose flour", "quantity": "2 and 1/4 cups"},
    {"name": "baking soda", "quantity": "1 teaspoon"}
  ],
  "instructions": [
    "Preheat the oven to 375°F (190°C).",
    "Whisk together flour, baking soda, and salt..."
  ]
}
```

---

## `ResponseSchema` vs `ResponseJsonSchema` — Which to Use?

| | `ResponseSchema` | `ResponseJsonSchema` |
|---|---|---|
| Input type | `*genai.Schema` (typed Go struct) | `map[string]any` (raw JSON Schema) |
| Constrained decoding | ✅ | ✅ |
| Best for | When you have a strongly typed Go model | When schema comes from config/DB or is dynamic |

---

## Supported JSON Schema Types

| Type | Notes |
|------|-------|
| `string` | Supports `enum` (fixed values), `format` (date-time, date) |
| `number` | Floating-point; supports `minimum`, `maximum`, `enum` |
| `integer` | Whole numbers; supports `minimum`, `maximum`, `enum` |
| `boolean` | `true`/`false` |
| `object` | Uses `properties`, `required`, `additionalProperties` |
| `array` | Uses `items`, `minItems`, `maxItems`, `prefixItems` |
| `null` | Allow null via `{"type": ["string", "null"]}` |

Use `description` on any field to guide the model on what to extract.

---

## Best Practices & Limitations

**Best practices:**
- Use `description` on each field — this is the primary way to guide extraction accuracy
- Use `enum` for classification fields to restrict to known values
- State clearly in your prompt what you want extracted ("Extract the following fields from the text...")
- **Always validate semantics in your app code** — structured output guarantees valid JSON *syntax*, not business-logic correctness

**Limitations:**
- Unsupported JSON Schema features are silently ignored
- Very large or deeply nested schemas may be rejected — simplify by shortening names, reducing nesting, or limiting constraints
- Structured outputs work with most Gemini models: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, and the Gemini 3 series





# Structured outputs

You can configure Gemini models to generate responses that adhere to a provided JSON Schema. This ensures predictable, type-safe results and simplifies extracting structured data from unstructured text.

Using structured outputs is ideal for:

Data extraction: Pull specific information like names and dates from text.
Structured classification: Classify text into predefined categories.
Agentic workflows: Generate structured inputs for tools or APIs.

In addition to supporting JSON Schema in the REST API, the Google GenAI SDKs make it easy to define schemas using Pydantic (Python) and Zod (JavaScript).

Recipe Extractor Content Moderation Recursive Structures

This example demonstrates how to extract structured data from text using basic JSON Schema types like object, array, string, and integer.

Python
JavaScript
Go
REST

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
  Please extract the recipe from the following text.
  The user wants to make delicious chocolate chip cookies.
  They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
  1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
  3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
  For the best part, they'll need 2 cups of semisweet chocolate chips.
  First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
  baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
  until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
  ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
  onto ungreased baking sheets and bake for 9 to 11 minutes.
  `
    config := &genai.GenerateContentConfig{
        ResponseMIMEType: "application/json",
        ResponseJsonSchema: map[string]any{
            "type": "object",
            "properties": map[string]any{
                "recipe_name": map[string]any{
                    "type":        "string",
                    "description": "The name of the recipe.",
                },
                "prep_time_minutes": map[string]any{
                    "type":        "integer",
                    "description": "Optional time in minutes to prepare the recipe.",
                },
                "ingredients": map[string]any{
                    "type": "array",
                    "items": map[string]any{
                        "type": "object",
                        "properties": map[string]any{
                            "name": map[string]any{
                                "type":        "string",
                                "description": "Name of the ingredient.",
                            },
                            "quantity": map[string]any{
                                "type":        "string",
                                "description": "Quantity of the ingredient, including units.",
                            },
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

Example Response:

```json
{
  "recipe_name": "Delicious Chocolate Chip Cookies",
  "ingredients": [
    {
      "name": "all-purpose flour",
      "quantity": "2 and 1/4 cups"
    },
    {
      "name": "baking soda",
      "quantity": "1 teaspoon"
    },
    {
      "name": "salt",
      "quantity": "1 teaspoon"
    },
    {
      "name": "unsalted butter (softened)",
      "quantity": "1 cup"
    },
    {
      "name": "granulated sugar",
      "quantity": "3/4 cup"
    },
    {
      "name": "packed brown sugar",
      "quantity": "3/4 cup"
    },
    {
      "name": "vanilla extract",
      "quantity": "1 teaspoon"
    },
    {
      "name": "large eggs",
      "quantity": "2"
    },
    {
      "name": "semisweet chocolate chips",
      "quantity": "2 cups"
    }
  ],
  "instructions": [
    "Preheat the oven to 375°F (190°C).",
    "In a small bowl, whisk together the flour, baking soda, and salt.",
    "In a large bowl, cream together the butter, granulated sugar, and brown sugar until light and fluffy.",
    "Beat in the vanilla and eggs, one at a time.",
    "Gradually beat in the dry ingredients until just combined.",
    "Stir in the chocolate chips.",
    "Drop by rounded tablespoons onto ungreased baking sheets and bake for 9 to 11 minutes."
  ]
}
```

## Streaming

You can stream structured outputs, which allows you to start processing the response as it's being generated, without having to wait for the entire output to be complete. This can improve the perceived performance of your application.

The streamed chunks will be valid partial JSON strings, which can be concatenated to form the final, complete JSON object.

Python
JavaScript

```python
from google import genai
from pydantic import BaseModel, Field
from typing import Literal

class Feedback(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str

client = genai.Client()
prompt = "The new UI is incredibly intuitive and visually appealing. Great job. Add a very long summary to test streaming!"

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

## Structured outputs with tools

Preview: This feature is available only to Gemini 3 series models, gemini-3.1-pro-preview and gemini-3-flash-preview.

Gemini 3 lets you combine Structured Outputs with built-in tools, including Grounding with Google Search, URL Context, Code Execution, File Search, and Function Calling.

Python
JavaScript
REST

```python
from google import genai
from pydantic import BaseModel, Field
from typing import List

class MatchResult(BaseModel):
    winner: str = Field(description="The name of the winner.")
    final_match_score: str = Field(description="The final match score.")
    scorers: List[str] = Field(description="The name of the scorer.")

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="Search for all details for the latest Euro.",
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

## JSON schema support

To generate a JSON object, set the response_mime_type in the generation configuration to application/json and provide a response_json_schema. The schema must be a valid JSON Schema that describes the desired output format.

The model will then generate a response that is a syntactically valid JSON string matching the provided schema. When using structured outputs, the model will produce outputs in the same order as the keys in the schema.

Gemini's structured output mode supports a subset of the JSON Schema specification.

The following values of type are supported:

string: For text.
number: For floating-point numbers.
integer: For whole numbers.
boolean: For true/false values.
object: For structured data with key-value pairs.
array: For lists of items.
null: To allow a property to be null, include "null" in the type array (e.g., {"type": ["string", "null"]}).

These descriptive properties help guide the model:

title: A short description of a property.
description: A longer and more detailed description of a property.

### Type-specific properties

For object values:

properties: An object where each key is a property name and each value is a schema for that property.
required: An array of strings, listing which properties are mandatory.
additionalProperties: Controls whether properties not listed in properties are allowed. Can be a boolean or a schema.

For string values:

enum: Lists a specific set of possible strings for classification tasks.
format: Specifies a syntax for the string, such as date-time, date, time.

For number and integer values:

enum: Lists a specific set of possible numeric values.
minimum: The minimum inclusive value.
maximum: The maximum inclusive value.

For array values:

items: Defines the schema for all items in the array.
prefixItems: Defines a list of schemas for the first N items, allowing for tuple-like structures.
minItems: The minimum number of items in the array.
maxItems: The maximum number of items in the array.

## Model support

The following models support structured output:

Model	Structured Outputs
Gemini 3.1 Pro Preview	✔️
Gemini 3 Flash Preview	✔️
Gemini 2.5 Pro	✔️
Gemini 2.5 Flash	✔️
Gemini 2.5 Flash-Lite	✔️
Gemini 2.0 Flash	✔️*
Gemini 2.0 Flash-Lite	✔️*

* Note that Gemini 2.0 requires an explicit propertyOrdering list within the JSON input to define the preferred structure. You can find an example in this cookbook.

## Structured outputs vs. function calling

Both structured outputs and function calling use JSON schemas, but they serve different purposes:

Feature	Primary Use Case
Structured Outputs	Formatting the final response to the user. Use this when you want the model's answer to be in a specific format (e.g., extracting data from a document to save to a database).
Function Calling	Taking action during the conversation. Use this when the model needs to ask you to perform a task (e.g., "get current weather") before it can provide a final answer.

## Best practices

Clear descriptions: Use the description field in your schema to provide clear instructions to the model about what each property represents. This is crucial for guiding the model's output.
Strong typing: Use specific types (integer, string, enum) whenever possible. If a parameter has a limited set of valid values, use an enum.
Prompt engineering: Clearly state in your prompt what you want the model to do. For example, "Extract the following information from the text..." or "Classify this feedback according to the provided schema...".
Validation: While structured output guarantees syntactically correct JSON, it does not guarantee the values are semantically correct. Always validate the final output in your application code before using it.
Error handling: Implement robust error handling in your application to gracefully manage cases where the model's output, while schema-compliant, may not meet your business logic requirements.

## Limitations

Schema subset: Not all features of the JSON Schema specification are supported. The model ignores unsupported properties.
Schema complexity: The API may reject very large or deeply nested schemas. If you encounter errors, try simplifying your schema by shortening property names, reducing nesting, or limiting the number of constraints.