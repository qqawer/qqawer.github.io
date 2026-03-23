---
title: "Git Master Guide: From Basics to Advanced Actions and Rescue Missions"
description: "A comprehensive guide to Git's basic commands, core operations, real-world PR workflows, commit rescue techniques, and mastering the .gitignore file. Truly understand Git and become the version control master in your team."
date: 2026-03-23
slug: "git-master-guide"
categories:
    - Tech
tags:
    - Git
    - GitHub
image: git-cover.jpg
toc: true
---

For every modern developer, Git is an indispensable productivity tool. But it’s not just a tool for saving code; mastering Git can save you in critical moments—like code conflicts or accidentally deleting commits—and can drastically improve team collaboration efficiency.

This article takes you from the basics of Git installation, deep dives into the most frequently used core commands, walks through a real-world Pull Request (PR) scenario, and finally teaches you advanced "undo" tricks, repository migration techniques, and the secrets of the `.gitignore` file.

---

## 1. Git Basics: Download & Installation

To become a master, you first need the right tools.

### For Mac
On macOS, using [Homebrew](https://brew.sh/) is the easiest and most recommended way:
```bash
brew install git
```
If you prefer not to use the command line, you can download the official graphical installer directly:
👉 [Git for Mac Official Download Link](https://git-scm.com/download/mac)

### For Windows
On Windows, simply download the official executable installer and click "Next" all the way. It comes with the highly useful Git Bash command-line tool.
👉 [Git for Windows Official Download Link](https://git-scm.com/download/win)

After installation, remember to configure your global username and email:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global --list
```

---

## 2. Git Core Operations Cheat Sheet

Before heading into battle, we need to master the most common moves.

### 1. State and Commit (Status, Add, Commit)
- `git status`: Check the status of your current working directory and staging area. This is the command you'll type the most; it tells you which files have been modified.
- `git add <file>`: Add a specific file to the staging area. Use `git add .` to add all modified files at once.
- `git commit -m "feat: xxx"`: Officially commit the staged contents to your local repository with a clear descriptive message.

### 2. Branch Control (Branch, Checkout)
- `git branch`: List all local branches. Add `-a` to see remote branches as well.
- `git checkout <branch-name>`: Switch to a specific branch.
- `git checkout -b <new-branch>`: **Create and instantly switch** to a new branch. (In newer Git versions, you can use `git switch -c <new-branch>` for better semantic clarity).

### 3. Sync and Merge (Push, Pull, Merge)
- `git push origin <branch-name>`: Push your local branch to the remote repository.
- `git pull origin <branch-name>`: Fetch the latest code from the remote repository and merge it into your current branch.
- `git merge <branch-name>`: Merge the specified branch into your *current* branch. (e.g., if you are on branch A and want to bring in changes from branch B, run `git merge B`).

### 4. Advanced Workflows & Magic (Rebase, Cherry-Pick)
- `git rebase <branch-name>`: Rebase. Unlike `merge`, which creates a new merge commit, `rebase` "grafts" the commits from your current branch onto the tip of the target branch, keeping the commit history perfectly linear and clean. If you are on branch A and run `git rebase B`, it replays A's commits on top of B's latest state.
- `git cherry-pick <commit-hash>`: "Cherry-picking." If you only want one specific commit from another branch, grab that commit's hash and run `cherry-pick`. It will precisely copy that exact change into your current branch.

### 5. Stashing Your Work (Stash, Pop)
Imagine you are halfway through developing feature A, and a critical production bug B comes up. You don't want to commit half-finished code, right?
- `git stash`: "Stash" all uncommitted changes (including those already added) to instantly give yourself a clean working directory.
- `git stash status / list`: View all your current stashes.
- `git stash pop`: After fixing the bug and switching back to your feature branch, run this to restore the most recent stash and automatically delete it from the stash list.

---

## 3. Real-World Scenario: From Git Pull to PR Merge

Theory is fine, but practice makes perfect. Let’s simulate a classic team workflow: **Your lead asks you to develop a new login page, submit a PR on GitHub for review, and merge it into the main branch**.

**Step 1. Sync the latest main branch code**
First, ensure your foundation is up-to-date.
```bash
git checkout main
git pull origin main
```

**Step 2. Create a dedicated feature branch**
Never write code directly on the `main` branch.
```bash
git checkout -b feature/login-page
```

**Step 3. Develop and Commit**
You furiously write code and finish the login page.
```bash
git status # Confirm which files were changed
git add .
git commit -m "feat: add user login page"
```

**Step 4. (Critical Step) Resolve potential conflicts and keep code synced**
While you were coding, your colleagues might have merged other code into `main`. To ensure a smooth PR, let's sync up locally first.
```bash
git fetch origin main              # Fetch the latest main from remote. Updates 'origin/main' safely.
git rebase origin/main             # Rebase your commits on top of the latest remote main.
```
*(If a conflict occurs, Git will pause and ask you to resolve it manually. After fixing the conflict, run `git add .` and then `git rebase --continue`)*

**Step 5. Push to your remote branch**
```bash
git push -u origin feature/login-page
```

**Step 6. Submit a Pull Request and Merge**
1. Log in to GitHub. The repository simply will show a prompt for the branch you just pushed. Click **"Compare & pull request"**.
2. Fill out a clear PR Title and description.
3. Click **Create pull request**.

Wait for team review. Once approved, click **Merge pull request** (Using "Squash and merge" is highly recommended to keep the main branch history clean with a single commit).

4. Finally, switch back to `main` locally, pull the latest code, and delete your local feature branch:
   `git checkout main && git pull origin main && git branch -d feature/login-page`

---

## 4. Saving Your Code: The Advanced "Undo" Arsenal

Everyone makes mistakes. As a master, you must be proficient in various undo methods.

### 1. Working directory messed up (Not added yet)
You want to discard all the messy changes you just made and go back to the state of your last commit:
```bash
git restore <file>     # Undo changes to a single file
git checkout .         # Undo all un-added changes
```

### 2. Accidentally added to staging (Not committed yet)
You accidentally ran `git add` on a huge file or a file containing private config data:
```bash
git restore --staged <file>  # Kicks the file out of the staging area, but your local changes are kept intact
# Or the older command: git reset HEAD <file>
```

### 3. Committed locally, but forgot a file or made a typo in the message
This trick is extremely useful! You simply `git add` the forgotten files, and then run:
```bash
git commit --amend -m "New message (if needed)"
```
This mixes the current changes with your last commit, preventing ugly "fix typo" or "forgot file" commits.

### 4. Three ways to Undo a Commit (Soft / Mixed / Hard)
Regret committing? Choose your poison:
- **Soft Delete (Soft)**: `git reset --soft HEAD~1`
  Cancels the commit command, but **keeps your code changes and keeps them in the staging area (added state)**. Very useful if you want to split your last commit into two.
- **Mixed Delete (Mixed, Default)**: `git reset --mixed HEAD~1`
  Cancels the commit and clears the staging area, but **keeps your code modifications in the working directory (un-added state)**. Use this when you want to fine-tune exactly which files to re-commit.
- **Hard Delete (Hard)**: `git reset --hard HEAD~1`
  **EXTREMELY DANGEROUS!** Cancels the commit and **completely wipes out all your physical file modifications**. The code is brutally rolled back to the state of the previous commit. If you accidentally use this, you'll likely need `git reflog` to save your life.

### 5. Already pushed to remote, can I still undo it?
Scenario A: It's your personal branch.
You can roll back locally with `git reset --hard HEAD~1` and then force push:
```bash
git push origin <branch-name> --force
```

Scenario B: It’s a public branch (like `main`). Force pushing will get you physically assaulted by your team.
You must neutralize it by "committing the opposite change".
```bash
git revert <commit-hash>
git push origin main
```
This safely generates a brand new commit that reverses everything the specified commit did. It preserves history and keeps your colleagues happy.

---

## 5. Changing Repositories and Untracking Files (Troubleshooting)

### Scenario A: Connected to an old repo locally, but the GitHub repo was deleted. I want to bind a new URL.
Just "unplug the old cable and plug in the new one":
```bash
# 1. View current remote repo info
git remote -v

# 2. Option 1: Directly modify the existing Origin URL (fastest)
git remote set-url origin <new-repo-url.git>

# Option 2: Delete then add
git remote rm origin
git remote add origin <new-repo-url.git>

# 3. Push to the new repo (and bind your local branch)
git push -u origin main
```

### Scenario B: I want Git to stop tracking a file, but I DO NOT want to delete it from my disk!
(For example, you accidentally pushed `error.log` or your IDE's `.idea/` configs).
```bash
# Stop tracking a single file
git rm --cached error.log

# Stop tracking an entire directory
git rm -r --cached .idea/
```
**Warning:** Merely executing `git rm --cached .idea/` does not fully detach it from Git! In VSCode's Source Control panel on the left, you'll see two things happen:
1. In the Staged Changes, a **"Deleted"** `.idea` appears (because it was removed from Git's history).
2. Simultaneously, in the Working Tree, a bunch of **"Untracked / U"** files pop up for `.idea`.

To make it magically disappear and restore your Source Control panel, you must perform a one-two punch: **First, add `.idea/` to your `.gitignore` file. Second, commit that staged "Deleted" modification.** Only then will it safely vanish from Git's radar.

### Scenario C: I want this entire project to sever all ties with Git!
If you cloned someone else's project or used a boilerplate CLI tool and want to completely rip it off the VSCode Source Control tree—erasing Git and all commit history (turning it into a totally normal, unversioned folder):
It's incredibly simple. Git's "soul" lives entirely in the hidden `.git` folder at the root directory. You just need to delete it:
```bash
# Mac / Linux
rm -rf .git

# Windows Command Line
rmdir /s /q .git
```
Once executed, this project completely escapes Git's control and becomes a pure, ordinary folder.

---

## 6. Mastering the `.gitignore` File: Your Project's "Invisibility Cloak"

In Git, not all files need to be version-controlled (e.g., dependencies like `node_modules`, compilation outputs like `build`, sensitive database passwords, or hidden OS configs). This is where `.gitignore` makes its grand entrance.

### 1. Where should `.gitignore` be placed?
Usually, you need to create a text file named exactly `.gitignore` (with no extension) **in the root directory of your project**.
Technically, you can create it in any subdirectory, and its rules will only apply to that folder and its descendants. However, centralizing all rules in the root `.gitignore` is the most common and standard practice.

### 2. How do `.gitignore` matching rules map to file paths?
In a `.gitignore` file, you write file path rules line by line (wildcards are supported). Each line essentially tells Git: "If a file's relative path matches this rule, please don't track it."

- **Ignore a specific file (by filename or relative path):**
  `secret.json` (Ignores all files named `secret.json` anywhere in the project)
  `config/database.yml` (Ignores only `database.yml` perfectly inside the root's `config` folder)

- **Ignore an entire folder (append a slash `/`):**
  `node_modules/` (Ignores all dependency packet folders—**extremely important**)
  `dist/` or `build/` (Ignores compiled output folders)
  `.idea/` (Ignores local IDE configuration folders)

- **Unpredictable magic using wildcards:**
  `*.log` (Ignores all files ending with `.log`, like `error.log` or `app.log`)
  `*.class` (Ignores all intermediate class files produced during Java compilation)

- **Exception Rules (Negation):**
  If you want to ignore all files inside a directory but keep just one specific file, start the rule with `!`:
  `logs/*`
  `!logs/important.log` (Everything in the `logs` folder is ignored, except for `important.log` which continues to be tracked)

**The Master's Final Advice:**
If a file **has already been tracked by Git (whether it was committed or just staged)**, adding it to the `.gitignore` file does absolutely nothing! Just like in Scenario B of the previous section, you must first remove it from version control using `git rm --cached <file-or-dir>` before your `.gitignore` rules can officially take effect.

---

## 7. The Git Master's Secret Stash (Bonus Tips)

- **The Time Machine: `git reflog`**
  Don't panic if you accidentally use `reset --hard` and delete an uncommitted branch or lose an important commit. `git reflog` secretly records every movement of your local `HEAD` pointer (including those abandoned ghosts). Find the target commit hash, jump back, and you've saved a life.
  
- **The Scapegoat Finder: `git blame <file>`**
  Want to know exactly who wrote that weird line of code, on what date, and in which commit? Use `git blame`. Not only is it essential for debugging, but it's also the ultimate tool for passing the buck.

- **Viewing the Ultimate Beautiful Commit Tree**
  The default `git log` is ugly. Cast this spell in your terminal:
  ```bash
  git log --graph --oneline --decorate --all
  ```
  You can also alias it: `git config --global alias.dog "log --all --decorate --oneline --graph"`. From now on, just typing `git dog` summons a gorgeous, colorful commit graph.

- **Fast Travel Command**
  `git checkout -` allows you to rapidly jump back and forth between your two most recent branches, much like the "Previous Channel" button on a TV remote.

> Mastering all of the above will not only allow you to navigate the version control network with ease, but also give you the calm confidence to type in world-saving commands when your teammates inevitably break the code. May your journey in the Git world be free of conflicts!
