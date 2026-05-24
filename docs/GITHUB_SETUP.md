# Git and GitHub setup

## Create local Git repo

From inside the project folder:

```bash
git init
git add .
git commit -m "Initial local MVP data stack"
```

## Create GitHub repo

On GitHub:

1. Click **New repository**.
2. Name it `jakan-phone-data-stack`.
3. Choose Private.
4. Do not initialize with README if you already have this repo locally.

## Link local repo to GitHub

Replace `YOUR_USERNAME`:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/jakan-phone-data-stack.git
git push -u origin main
```

## GitHub CLI option

```bash
gh auth login
gh repo create jakan-phone-data-stack --private --source=. --remote=origin --push
```

## Daily workflow

```bash
git status
git add .
git commit -m "Describe the change"
git push
```

## Safety

Never commit `.env`, raw Excel files, credentials, API keys, or customer data.
