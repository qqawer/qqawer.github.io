---
title: "AWS Cloud Quest: Cloud Practitioner"
description: "AWS Cloud Quest notes: Cloud Computing Essentials, S3 storage classes, access management, and a hands-on static website hosting lab"
date: 2026-06-21
slug: "aws-cloud-quest-cloud-practitioner"
categories:
    - Documentation
tags:
    - AWS
    - Cloud Practitioner
    - S3
    - Cloud Computing
toc: true
---


# AWS Cloud Quest: Cloud Practitioner

## Section 1: Cloud Computing Essentials

### 1.1 Amazon S3 Overview

Amazon Simple Storage Service (Amazon S3) is an object storage service that stores and protects any amount of data with high scalability, availability, security, and performance. The overview slide highlights:

![Amazon S3 Overview](image.png)

- **Scalability**: storage resources scale automatically to meet fluctuating demands — no upfront investment, no resource-procurement cycles.
- **Durability**: 99.999999999% (eleven 9s) — S3 automatically creates and stores copies of every object across multiple Availability Zones.
- **Security & compliance**: leading security, compliance, and audit capabilities, including encryption features, S3 Block Public Access, access management tools, and auditing; compliance programs include PCI-DSS, FedRAMP, HIPAA/HITECH, FISMA, and the EU Data Protection Directive.
- **Buckets & objects**: data is stored as objects in containers called buckets. Each object holds data plus metadata (name-value pairs such as time created and location) and is uniquely identified; bucket names must be unique across AWS (for example `aws-unique-bucket`).
- **Use cases**: websites, mobile apps, enterprise apps, backup & restore, archive, disaster recovery, big data analytics, and IoT devices.
- **Integration**: widely supported by applications and services, the AWS Partner Network (APN), and AWS Marketplace offerings.

### 1.2 Amazon S3 More Features

#### Storage classes

S3 offers different storage classes based on how often you need to access your data — from frequently accessed data to archived data that is rarely accessed:

![S3 storage classes](image-1.png)

- **S3 Standard**: frequently accessed data, millisecond access.
- **S3 Intelligent-Tiering**: unknown or changing access patterns; automatically moves data between tiers.
- **S3 Standard-IA / One Zone-IA**: infrequently accessed data (One Zone-IA is for re-creatable data in a single Availability Zone).
- **S3 Glacier Instant Retrieval / Flexible Retrieval / Deep Archive**: long-term archives; retrieval from milliseconds to 5-12 hours / 12-48 hours, with free bulk retrievals.

#### Management tools

![S3 management tools](image-2.png)

- **S3 Storage Class Analysis**: discovers data based on access patterns.
- **S3 Lifecycle Policy**: expires objects or transitions them to a lower-cost storage class automatically.
- **S3 Cross-Region Replication (CRR) / Same-Region Replication**: copies data across regions or within the same region.
- **S3 Object Lock**: enforces write-once-read-many (WORM) policies with retention periods — objects cannot be deleted or overwritten.
- **S3 Inventory**: lists objects and metadata (including encryption status), even for billions of objects.
- **S3 Batch Operations**: performs actions such as copy, restore, modify access controls, and tag sets on billions of objects; works with AWS Lambda and sends alerts — without managing additional infrastructure.

#### Query-in-place and versioning

![S3 query-in-place and versioning](image-3.png)

- **Amazon Athena**: runs SQL queries directly against data at rest in S3.
- **Amazon Redshift Spectrum**: queries large data sets in S3 from Redshift.
- **S3 Select**: retrieves subsets of an entire object (up to 5 TB) with up to 400% query performance and querying costs reduced by as much as 80%.
- **Versioning**: buckets can be unversioned (default), versioning-enabled, or versioning-suspended. Every version of every object is stored with a unique version ID, so you can recover from accidental deletions or overwrites; deleting an object creates a delete marker instead of permanently removing it.

![S3 More Features summary](image-4.png)

### 1.3 Amazon S3 Access Management

All S3 resources — buckets, objects, and related subresources — are **private by default**. Only the resource owner can access them unless permissions are granted through an access policy:

![S3 access management](image-5.png)

- **Resource-based policies**: bucket policies (JSON), Access Control Lists (ACLs), and query-string authentication (time-limited URLs for temporary access).
- **User policies**: IAM user policies attached to users, groups, or roles.
- AWS evaluates all applicable access policies and authorizes or denies the request accordingly.

![Bucket policies and ACLs](image-6.png)

- **Bucket policies** are written in JSON and grant or deny permissions to the S3 bucket and all objects in it. The `Principal` can be the root account, IAM users, other AWS accounts, or `*` (everyone). Example: `Effect: Allow`, `Principal: "*"`, `Action: s3:GetObject`, `Resource: arn:aws:s3:::my_bucket/*`.
- **ACLs** grant basic read/write permissions to other AWS accounts via a default ACL (bucket owner), with options such as List, Read, Write, and Full control.

![IAM user policies](image-7.png)

- **User policies** are JSON policies attached to IAM entities; they do not require a `Principal` because the IAM entity itself is the principal. Example: `Action: s3:ListBucket`, `Resource: arn:aws:s3:::test` allows listing all objects in the test bucket.

![S3 Access Management summary](image-8.png)

### 1.4 Practice: Static Website Hosting on S3

This practice lab builds a static website ("Beach Wave Conditions") hosted on S3, walking through the AWS Management Console step by step.

**Step 1 — Open the S3 console.** In the top navigation search box, type `S3`, and under Services click **S3**.

![Search S3 in the AWS Management Console](image-9.png)

**Step 2 — Open the lab bucket.** On the **General purpose buckets** tab, click the bucket whose name starts with `website-bucket-`. It contains the code required for this lab.

![S3 general purpose buckets](image-10.png)

**Step 3 — Review the bucket and its objects.** S3 stores objects in containers called buckets, and each object must be in a bucket. Copy the bucket name (you will need it later), then review the five files on the **Objects** tab — they contain the static website content: `index.html`, `main.js`, `styles.css`, `target-file.csv`, and `text.html`.

![Bucket objects](image-11.png)

**Step 4 — Rename `text.html` to `error.html`.** Choose the AWS Region that stores the bucket (regions reduce latency, lower costs, or meet regulatory requirements; objects stay in their region unless moved). Rename `text.html` to `error.html` — this becomes the error page shown whenever something goes wrong for website users.

![Rename object](image-12.png)

**Step 5 — Verify the rename and open Permissions.** You can upload files up to 5 GB in a single operation; larger files (up to 5 TB) need multipart upload. Review the success alert, then click the **Permissions** tab.

![Rename succeeded](image-13.png)

**Step 6 — Review Block Public Access.** All S3 resources are private by default. Confirm that **Block all public access** is turned **Off** — turning it off is necessary for static web hosting through the bucket.

![Block public access](image-14.png)

**Step 7 — Review the bucket policy.** Permissions can be granted with bucket policies and user policies, both written in JSON. Every AWS resource has a unique identifier called an **Amazon Resource Name (ARN)**. This bucket policy allows public read-only access (`s3:GetObject`) to anyone for all objects in the bucket — for production, stricter permissions are recommended.

![Bucket policy](image-15.png)

**Step 8 — Open Properties.** To host a static website on S3 you need to configure the bucket for website hosting, set permissions, and add an index document; you can also set up redirects, logging, and custom error pages. Click the **Properties** tab.

![Bucket properties](image-16.png)

**Step 9 — Review default encryption.** Server-side encryption protects your data where it is stored: when you upload data, S3 automatically encrypts it before saving it to AWS data centers, and automatically decrypts it when you access it. The default is **SSE-S3** (S3 managed keys).

![Default encryption](image-17.png)

**Step 10 — Edit static website hosting.** In the **Static website hosting** section of Properties, click **Edit**.

![Static website hosting](image-18.png)

**Step 11 — Enable hosting and set the documents.** Choose **Enable** and **Host a static website**, then set **Index document** to `index.html` and **Error document** to `error.html`. S3 provides two URL formats: virtual-hosted style (`https://bucket-name.s3.Region.amazonaws.com/key`) and path style (`https://s3.Region.amazonaws.com/bucket-name/key`).

![Edit static website hosting](image-19.png)

**Step 12 — Save changes.**

![Save changes](image-20.png)

**Step 13 — Copy the website endpoint.** Confirm that **Hosting type** is **Bucket hosting**, then copy the **Bucket website endpoint** (for example `http://website-bucket-xxxxx.s3-website-us-east-1.amazonaws.com`).

![Bucket website endpoint](image-21.png)

**Step 14 — Verify the website.** In a new browser tab, paste the endpoint and press Enter. The "Beach Wave Conditions" page loads, showing wave-length data for each hour of the day.

![Static website is live](image-22.png)

**Step 15 — Practice completed.** The static website is now live on S3; continue to the DIY section to complete the solution.

![Practice completed](image-23.png)


Section2: Deploying EC2 Instances Across Multiple Availability Zones"
![alt text](image-24.png)
AWS Global Infrastructure Overview
![alt text](image-25.png)
![alt text](image-26.png)
![alt text](image-27.png)
![alt text](image-28.png)

Amazon EC2 Overview
![alt text](image-29.png)
![alt text](image-30.png)
![alt text](image-31.png)
![alt text](image-32.png)

AWS Global Infrastructure Benefits 
![alt text](image-33.png)
![alt text](image-34.png)
![alt text](image-35.png)
![alt text](image-36.png)
![alt text](image-37.png)

Amazon EBS Overview
![alt text](image-38.png)
![alt text](image-39.png)
![alt text](image-40.png)
![alt text](image-41.png)
![alt text](image-42.png)
![alt text](image-43.png)
![alt text](image-44.png)

DNS Overview
![alt text](image-45.png)
![alt text](image-46.png)
![alt text](image-47.png)
![alt text](image-48.png)

AWS Support, Resources and Documentation Overview
![alt text](image-49.png)
![alt text](image-50.png)
![alt text](image-51.png)
![alt text](image-52.png)
![alt text](image-53.png)
![alt text](image-54.png)

Practice:
![alt text](image-55.png)
![alt text](image-56.png)
![alt text](image-57.png)
![alt text](image-58.png)
![alt text](image-59.png)
![alt text](image-60.png)
![alt text](image-61.png)
![alt text](image-62.png)
![alt text](image-63.png)
![alt text](image-64.png)
![alt text](image-65.png)
![alt text](image-66.png)
![alt text](image-67.png)
![alt text](image-68.png)
![alt text](image-69.png)
![alt text](image-70.png)
![alt text](image-71.png)
![alt text](image-72.png)
![alt text](image-73.png)
![alt text](image-74.png)
![alt text](image-75.png)


Section3: Scaling Up the Amazon EC2 Instance
![alt text](image-76.png)

Amazon Elastic Compute Cloud Overview
![alt text](image-77.png)
![alt text](image-78.png)
![alt text](image-79.png)
![alt text](image-80.png)

AWS Systems Management Overview
![alt text](image-81.png)
![alt text](image-82.png)
![alt text](image-83.png)
![alt text](image-84.png)
![alt text](image-85.png)

![alt text](image-86.png)
![alt text](image-87.png)
![alt text](image-88.png)
![alt text](image-89.png)

Practice：
![alt text](image-90.png)
![alt text](image-91.png)
![alt text](image-92.png)
![alt text](image-93.png)
![alt text](image-94.png)
![alt text](image-95.png)
![alt text](image-96.png)
![alt text](image-97.png)
![alt text](image-98.png)
![alt text](image-99.png)
![alt text](image-100.png)
![alt text](image-101.png)
![alt text](image-102.png)
![alt text](image-103.png)
![alt text](image-104.png)
![alt text](image-105.png)
![alt text](image-106.png)
![alt text](image-107.png)
![alt text](image-108.png)
![alt text](image-109.png)
![alt text](image-110.png)
![alt text](image-111.png)
![alt text](image-112.png)

Section4:Configuring VPC Networking Components for Secure Internet Connectivity
![alt text](image-113.png)

AWS Global Infrastructure Overview
![alt text](image-114.png)
![alt text](image-115.png)
![alt text](image-116.png)
![alt text](image-117.png)

Amazon Virtual Private Cloud VPC Overview
![alt text](image-118.png)
![alt text](image-119.png)
![alt text](image-120.png)
![alt text](image-121.png)

Amazon Virtual Private Cloud VPC Concepts
![alt text](image-129.png)
![alt text](image-122.png)
![alt text](image-123.png)
![alt text](image-124.png)

Amazon Virtual Private Cloud(VPC) - Network Access Control Lists & Security Groups
![alt text](image-130.png)
![alt text](image-125.png)
![alt text](image-126.png)
![alt text](image-127.png)

Amazon Virtual Private CLoud (VPC) - Internet Connectivity
![alt text](image-128.png)
![alt text](image-131.png)
![alt text](image-132.png)
![alt text](image-133.png)
![alt text](image-134.png)

Amazon Virtual Private CLoud (VPC) - Network Access COntrol Lists & Security Groups
![alt text](image-135.png)
![alt text](image-136.png)
![alt text](image-137.png)
![alt text](image-138.png)

Practice:
![alt text](image-139.png)
![alt text](image-140.png)
![alt text](image-141.png)
![alt text](image-142.png)
![alt text](image-143.png)
![alt text](image-144.png)
![alt text](image-145.png)
![alt text](image-146.png)
![alt text](image-147.png)
![alt text](image-148.png)
![alt text](image-149.png)
![alt text](image-150.png)
![alt text](image-151.png)
![alt text](image-152.png)
![alt text](image-153.png)
![alt text](image-154.png)
![alt text](image-155.png)
![alt text](image-156.png)
![alt text](image-157.png)
![alt text](image-158.png)
![alt text](image-159.png)

Section5: Cloud Economics
![alt text](image-160.png)
AWS Price:
![alt text](image-161.png)
![alt text](image-162.png)
![alt text](image-163.png)
![alt text](image-164.png)
![alt text](image-165.png)
![alt text](image-166.png)
![alt text](image-167.png)
![alt text](image-168.png)
![alt text](image-169.png)
![alt text](image-170.png)
![alt text](image-171.png)
![alt text](image-172.png)
AWS Cloud Adoption Framework Overview
![alt text](image-173.png)
![alt text](image-174.png)
![alt text](image-175.png)
![alt text](image-176.png)
![alt text](image-177.png)
![alt text](image-178.png)
![alt text](image-179.png)
![alt text](image-180.png)
![alt text](image-181.png)
![alt text](image-182.png)
![alt text](image-183.png)
![alt text](image-184.png)

Practice:
![alt text](image-185.png)
![alt text](image-186.png)
![alt text](image-187.png)
![alt text](image-188.png)
![alt text](image-189.png)
![alt text](image-190.png)
![alt text](image-191.png)
![alt text](image-192.png)
![alt text](image-193.png)
![alt text](image-194.png)
![alt text](image-195.png)
![alt text](image-196.png)
![alt text](image-197.png)
![alt text](image-198.png)
![alt text](image-199.png)
![alt text](image-200.png)
![alt text](image-201.png)
![alt text](image-202.png)
![alt text](image-203.png)
![alt text](image-204.png)
![alt text](image-205.png)
![alt text](image-206.png)
![alt text](image-207.png)
![alt text](image-208.png)
![alt text](image-209.png)


Section6: Database in Practice
![alt text](image-210.png)

Amazon Relational Database Service(Amazon RDS) Overview:
![alt text](image-211.png)
![alt text](image-212.png)
![alt text](image-213.png)
![alt text](image-214.png)
![alt text](image-215.png)

Amazon RDS - Lower Admin Burden Performance
![alt text](image-216.png)
![alt text](image-217.png)
![alt text](image-218.png)
![alt text](image-219.png)

Amazon RDS - Availability & Durability
![alt text](image-220.png)
![alt text](image-221.png)
![alt text](image-222.png)
![alt text](image-223.png)

![alt text](image-224.png)

DNS Overview
![alt text](image-225.png)
![alt text](image-226.png)
![alt text](image-227.png)

Amazon RDS - S caScalability
![alt text](image-228.png)
![alt text](image-229.png)
![alt text](image-230.png)
![alt text](image-231.png)
![alt text](image-232.png)

Practice:
![alt text](image-233.png)
![alt text](image-234.png)
![alt text](image-235.png)
![alt text](image-236.png)
![alt text](image-237.png)
![alt text](image-238.png)
![alt text](image-239.png)
![alt text](image-240.png)
![alt text](image-241.png)
![alt text](image-242.png)
![alt text](image-243.png)
![alt text](image-244.png)
![alt text](image-245.png)
![alt text](image-246.png)
![alt text](image-247.png)
![alt text](image-248.png)
![alt text](image-249.png)
![alt text](image-250.png)
![alt text](image-251.png)
![alt text](image-252.png)

Section7: First NoSQl Database

NoSQL
![alt text](image-253.png)

Different Between SQL and NoSQL
![alt text](image-254.png)
![alt text](image-255.png)

How To Create A NoSQL Table
![alt text](image-256.png)
![alt text](image-257.png)


![alt text](image-258.png)


Amazon DynameDB Overview
![alt text](image-259.png)
![alt text](image-260.png)

Amazon DynameDB Queries Overview
![alt text](image-261.png)
![alt text](image-262.png)
![alt text](image-263.png)
![alt text](image-264.png)


![alt text](image-265.png)


Practice:
![alt text](image-266.png)


Section8: File Systems in the Cloud

Amazon EFS Overview
![alt text](image-267.png)
![alt text](image-268.png)

Amazon EFS Benefits
![alt text](image-269.png)
![alt text](image-270.png)

Amazon EFS Features
![alt text](image-271.png)
![alt text](image-272.png)

![alt text](image-273.png)

![alt text](image-274.png)

![alt text](image-275.png)

Practice：
![alt text](image-276.png)
![alt text](image-277.png)
![alt text](image-278.png)
![alt text](image-279.png)
![alt text](image-280.png)
![alt text](image-281.png)
![alt text](image-282.png)
![alt text](image-283.png)
![alt text](image-284.png)
![alt text](image-285.png)
![alt text](image-286.png)
![alt text](image-287.png)
![alt text](image-288.png)
![alt text](image-289.png)
![alt text](image-290.png)
![alt text](image-291.png)
![alt text](image-292.png)
![alt text](image-293.png)
![alt text](image-294.png)
![alt text](image-295.png)
![alt text](image-296.png)
![alt text](image-297.png)
![alt text](image-298.png)
![alt text](image-299.png)
![alt text](image-300.png)
![alt text](image-301.png)
![alt text](image-302.png)
![alt text](image-303.png)
![alt text](image-304.png)
![alt text](image-305.png)
![alt text](image-306.png)
![alt text](image-307.png)
![alt text](image-308.png)
![alt text](image-309.png)
![alt text](image-310.png)
![alt text](image-311.png)
![alt text](image-312.png)
![alt text](image-313.png)
![alt text](image-314.png)
![alt text](image-315.png)
![alt text](image-316.png)
![alt text](image-317.png)
![alt text](image-318.png)
![alt text](image-319.png)
![alt text](image-320.png)
![alt text](image-321.png)


Section9: Core Security Concepts
![alt text](image-322.png)

AWS Security and Compliance Overview
![alt text](image-323.png)

AWS IAM - Overview
![alt text](image-324.png)
![alt text](image-325.png)

AWS IAM - Manage Permissions
![alt text](image-326.png)
![alt text](image-327.png)
![alt text](image-328.png)
![alt text](image-329.png)
![alt text](image-330.png)

AWS IAM Features - Access Analysis
![alt text](image-331.png)
![alt text](image-332.png)


![alt text](image-333.png)

![alt text](image-334.png)

![alt text](image-335.png)

Practice
![alt text](image-336.png)
![alt text](image-337.png)
![alt text](image-338.png)
![alt text](image-339.png)
![alt text](image-340.png)
![alt text](image-341.png)
![alt text](image-342.png)
![alt text](image-343.png)
![alt text](image-344.png)
![alt text](image-345.png)
![alt text](image-346.png)
![alt text](image-347.png)
![alt text](image-348.png)
![alt text](image-349.png)
![alt text](image-350.png)
![alt text](image-351.png)
![alt text](image-352.png)
![alt text](image-353.png)
![alt text](image-354.png)
![alt text](image-355.png)
![alt text](image-356.png)
![alt text](image-357.png)
