# Getting Started Guide

> A complete beginner's guide to setting up The Private Council from scratch.

This guide assumes no prior experience with Python, Docker, or Ollama. It walks you through every step needed to get the system running on your machine.

**Time required**: 30-60 minutes (depending on download speeds)

---

## Table of Contents

1. [What You're Setting Up](#what-youre-setting-up)
2. [Prerequisites Overview](#prerequisites-overview)
3. [Step 1: Install Git](#step-1-install-git)
4. [Step 2: Install Python](#step-2-install-python)
5. [Step 3: Install Ollama](#step-3-install-ollama)
6. [Step 4: Install Docker (Optional)](#step-4-install-docker-optional)
7. [Step 5: Clone the Repository](#step-5-clone-the-repository)
8. [Step 6: Download AI Models](#step-6-download-ai-models)
9. [Step 7: Run the Application](#step-7-run-the-application)
10. [Step 8: Verify Everything Works](#step-8-verify-everything-works)
11. [Troubleshooting](#troubleshooting)
12. [Next Steps](#next-steps)

---

## What You're Setting Up

The Private Council is a local AI deliberation system. Here's what each component does:

| Component | What It Is | Why You Need It |
|-----------|------------|-----------------|
| **Git** | Version control software | To download the project code |
| **Python** | Programming language | The backend server is written in Python |
| **Ollama** | Local AI model runner | Runs the AI models on your computer |
| **Docker** | Container platform | Simplifies running everything together (optional) |

**How it works**: You ask a question → Multiple AI models give their perspectives → A "chairman" model synthesizes the answers → You see areas of agreement and disagreement.

---

## Prerequisites Overview

Before starting, check what you have:

| Requirement | Minimum | Recommended | How to Check |
|-------------|---------|-------------|--------------|
| RAM | 16 GB | 32 GB | See [Check Your System](#check-your-system) below |
| Storage | 20 GB free | 50 GB free | See [Check Your System](#check-your-system) below |
| GPU | Not required | 8GB+ VRAM | Optional - CPU works too |
| Internet | Required for setup | - | For downloading components |

### Check Your System

**Windows:**
1. Press `Windows + I` to open Settings
2. Go to System → About
3. Look for "Installed RAM"
4. For storage: Open File Explorer, right-click on C: drive, select Properties

**macOS:**
1. Click Apple menu →  About This Mac
2. RAM is shown as "Memory"
3. Click "Storage" tab for disk space

**Linux:**
```bash
# Check RAM
free -h

# Check storage
df -h /
```

---

## Step 1: Install Git

Git is a tool for downloading and managing code. You need it to get The Private Council.

### Windows

1. Download Git from https://git-scm.com/download/windows
2. Run the installer
3. Accept all default options (click "Next" repeatedly)
4. When finished, open a new Command Prompt or PowerShell

**Verify installation:**
```powershell
git --version
```
You should see something like `git version 2.43.0`

### macOS

**Option A: Using Homebrew (recommended if you have it)**
```bash
brew install git
```

**Option B: Install Xcode Command Line Tools**
```bash
xcode-select --install
```
A popup will appear - click "Install" and wait.

**Verify installation:**
```bash
git --version
```
You should see something like `git version 2.43.0`

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install git
```

**Verify installation:**
```bash
git --version
```

---

## Step 2: Install Python

Python is the programming language used for the backend. You need version 3.10 or newer.

### Check If Python Is Already Installed

Open a terminal and run:
```bash
python3 --version
```

If you see `Python 3.10.x` or higher (like 3.11, 3.12), you can skip to [Step 3](#step-3-install-ollama).

### Windows

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or 3.12 (the big yellow button)
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH" at the bottom of the first screen
5. Click "Install Now"

**Verify installation** (open a NEW PowerShell window):
```powershell
python --version
```

### macOS

**Option A: Using Homebrew (recommended)**
```bash
brew install python@3.11
```

**Option B: Direct download**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or 3.12
3. Run the installer package

**Verify installation:**
```bash
python3 --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Verify installation:**
```bash
python3 --version
```

### What Is a Virtual Environment?

When you install Python packages for a project, a "virtual environment" keeps them separate from other projects. This prevents conflicts between different projects that might need different versions of the same package.

Think of it like having separate tool boxes for different jobs - you don't mix your plumbing tools with your electrical tools.

You'll create a virtual environment in [Step 7](#step-7-run-the-application).

---

## Step 3: Install Ollama

Ollama is the software that runs AI models locally on your computer. This is what makes The Private Council work without sending your data to the cloud.

### What Is Ollama?

Ollama is like a local server for AI models. It:
- Downloads AI models to your computer
- Runs them when you ask questions
- Provides an interface for other applications (like The Private Council) to use them

### Windows

1. Go to https://ollama.com/download
2. Click "Download for Windows"
3. Run the installer
4. Ollama will start automatically and appear in your system tray (bottom-right corner)

**Verify installation** (open PowerShell):
```powershell
ollama --version
```

### macOS

1. Go to https://ollama.com/download
2. Click "Download for macOS"
3. Open the downloaded .zip file
4. Drag Ollama to your Applications folder
5. Open Ollama from Applications
6. Click "Open" if you see a security warning

**Verify installation:**
```bash
ollama --version
```

### Linux

Run this single command:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Verify installation:**
```bash
ollama --version
```

### Start Ollama

Ollama needs to be running before you can use The Private Council.

**Windows/macOS:** Ollama starts automatically when you log in. Look for the llama icon in your system tray (Windows) or menu bar (macOS).

**Linux:** Start Ollama manually:
```bash
ollama serve
```
Leave this terminal open, or run it in the background:
```bash
ollama serve &
```

### Verify Ollama Is Running

```bash
curl http://localhost:11434
```

You should see: `Ollama is running`

If you see "connection refused", Ollama isn't running - start it using the instructions above.

---

## Step 4: Install Docker (Optional)

Docker is optional but recommended. It packages everything together so you don't have to worry about configuration details.

**Skip this step if:**
- You prefer manual installation
- You're just testing things out
- You're contributing to frontend development only

### What Is Docker?

Docker runs applications in "containers" - isolated environments that include everything the application needs. Think of it like running an application in a separate, self-contained computer.

### Windows

1. Go to https://www.docker.com/products/docker-desktop/
2. Download "Docker Desktop for Windows"
3. Run the installer
4. Restart your computer when prompted
5. Open Docker Desktop from Start menu
6. Wait for Docker to start (the whale icon stops animating)

**Verify installation** (open PowerShell):
```powershell
docker --version
docker compose version
```

**Note for Windows users:** Docker Desktop requires WSL 2 (Windows Subsystem for Linux). The installer will guide you through setting this up if needed.

### macOS

1. Go to https://www.docker.com/products/docker-desktop/
2. Download "Docker Desktop for Mac"
   - Choose "Apple Silicon" if you have an M1/M2/M3 Mac
   - Choose "Intel" if you have an older Mac
3. Open the downloaded .dmg file
4. Drag Docker to Applications
5. Open Docker from Applications
6. Wait for Docker to start (the whale icon stops animating)

**Verify installation:**
```bash
docker --version
docker compose version
```

### Linux (Ubuntu/Debian)

```bash
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose-v2

# Add yourself to the docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and back in, then verify:
docker --version
docker compose version
```

---

## Step 5: Clone the Repository

Now download The Private Council code to your computer.

### Choose a Location

First, decide where to put the project. Common choices:

- **Windows:** `C:\Users\YourName\Projects\`
- **macOS/Linux:** `~/projects/` or `~/code/`

Create the folder if it doesn't exist:

**Windows (PowerShell):**
```powershell
mkdir C:\Users\$env:USERNAME\Projects
cd C:\Users\$env:USERNAME\Projects
```

**macOS/Linux:**
```bash
mkdir -p ~/projects
cd ~/projects
```

### Clone the Repository

```bash
git clone https://github.com/pawn002/private-llm-council.git
cd private-llm-council
```

**What this does:**
- `git clone` downloads a copy of the project
- `cd private-llm-council` enters the project folder

### Verify the Clone

```bash
ls
```

You should see files like `README.md`, `docker-compose.yml`, and folders like `backend/`, `frontend/`, `docs/`.

---

## Step 6: Download AI Models

Now download the AI models that will participate in deliberations.

### Understanding Model Sizes

Models come in different sizes. Larger = smarter but slower and needs more resources.

| Size | RAM Needed | Speed | Quality | Good For |
|------|------------|-------|---------|----------|
| 0.5-1B | 4-6 GB | Very Fast | Basic | Quick tests, learning |
| 1-3B | 8-12 GB | Fast | Good | Modest hardware, regular use |
| 7-8B | 16+ GB | Medium | Better | Dedicated GPU users |
| 70B | 48+ GB | Slow | Best | High-end hardware |

### Choose Your Setup

**Option A: Modest Hardware (16GB RAM, no dedicated GPU)**

This is the recommended starting point if you're unsure:

```bash
# Fast mode models (2-5 minute deliberations)
ollama pull qwen2.5:0.5b
ollama pull llama3.2:1b
ollama pull tinyllama:1.1b
```

**Option B: Standard Hardware (32GB RAM or 8GB+ GPU)**

```bash
ollama pull llama3.2:8b
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

### Verify Models Downloaded

```bash
ollama list
```

You should see the models you downloaded with their sizes.

### How Long Does This Take?

| Model | Size | Time (fast internet) | Time (slow internet) |
|-------|------|---------------------|---------------------|
| qwen2.5:0.5b | ~400 MB | 1-2 min | 5-10 min |
| llama3.2:1b | ~1 GB | 2-3 min | 10-15 min |
| llama3.2:8b | ~4.5 GB | 5-10 min | 30-45 min |

---

## Step 7: Run the Application

Choose ONE of these methods:

### Method A: Using Docker (Recommended)

This is the easiest way if you installed Docker.

```bash
# Make sure you're in the project folder
cd private-llm-council

# Copy the environment configuration
cp .env.example .env

# Start everything
docker compose up -d
```

**What this does:**
- `cp .env.example .env` creates your configuration file
- `docker compose up -d` starts all services in the background

**Check if it's running:**
```bash
docker compose ps
```

You should see `sovereign-council-api` and `sovereign-council-ui` with status "Up".

**View logs (optional):**
```bash
docker compose logs -f
```

Press `Ctrl+C` to stop viewing logs (the services keep running).

### Method B: Manual Installation (Without Docker)

If you didn't install Docker:

**Terminal 1 - Start the backend:**
```bash
cd private-llm-council/backend

# Create a virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the server
python -m src.main
```

Leave this terminal running.

**Terminal 2 - Start the frontend:**
```bash
cd private-llm-council/frontend

# Install Node.js dependencies
npm install

# Run the development server
npm run dev
```

Leave this terminal running too.

---

## Step 8: Verify Everything Works

### Check the Web Interface

1. Open your web browser
2. Go to http://localhost:3000
3. You should see The Private Council interface

### Test a Deliberation

**Option A: Using the web interface**

1. Type a question in the input box, for example:
   > "What are the pros and cons of working from home?"
2. Click "Deliberate"
3. Wait for the council to respond (this may take 2-15 minutes depending on your hardware)

**Option B: Using the command line**

```bash
curl -X POST http://localhost:8000/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the pros and cons of working from home?"}'
```

### What to Expect

- **First time**: Models may need to load into memory (30-60 seconds)
- **Modest hardware**: Full deliberation takes 5-15 minutes
- **Better hardware**: Full deliberation takes 1-5 minutes

You should see:
1. Individual perspectives from each council member
2. A synthesis from the chairman
3. Highlighted areas of disagreement

---

## Troubleshooting

### "Ollama is not running" or Connection Refused

**Symptom:** Error connecting to Ollama

**Solution:**
1. Check if Ollama is running:
   ```bash
   curl http://localhost:11434
   ```
2. If not, start it:
   - **Windows/macOS:** Open Ollama from Start menu or Applications
   - **Linux:** Run `ollama serve`

### "Model not found"

**Symptom:** Error says a model doesn't exist

**Solution:**
1. Check which models you have:
   ```bash
   ollama list
   ```
2. Download any missing models:
   ```bash
   ollama pull <model-name>
   ```

### Docker Containers Won't Start

**Symptom:** `docker compose up` fails

**Solutions:**

1. **Is Docker running?**
   - Windows/macOS: Look for the whale icon in system tray/menu bar
   - Linux: Run `sudo systemctl start docker`

2. **Port conflict?**
   ```bash
   # Check if port 3000 is in use
   lsof -i :3000
   ```
   If something else is using port 3000, either stop it or edit `.env` to use a different port.

3. **Try rebuilding:**
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

### "Out of Memory" Errors

**Symptom:** System freezes or errors mention memory

**Solutions:**

1. Close other applications (browsers use a lot of RAM!)
2. Use smaller models:
   ```bash
   ollama pull qwen2.5:0.5b  # Very small model
   ```
3. Force CPU mode (uses system RAM instead of GPU):
   ```bash
   export OLLAMA_NUM_GPU=0
   ollama serve
   ```

### Slow Performance

**Symptom:** Deliberations take forever

**This is normal on modest hardware!** Expected times:

| Hardware | Expected Time |
|----------|---------------|
| Laptop (16GB RAM) | 5-15 minutes |
| Desktop (32GB RAM) | 2-5 minutes |
| Gaming PC (8GB+ GPU) | 1-3 minutes |

**Tips to speed up:**
1. Use smaller models (0.5B-1B instead of 7B-8B)
2. Close background applications
3. Use CPU mode if integrated GPU is slow:
   ```bash
   export OLLAMA_NUM_GPU=0
   ```

### Python Virtual Environment Issues

**Symptom:** "No module named" errors

**Solution:**
Make sure you activated the virtual environment:
```bash
# Check if activated (should show venv in prompt)
which python  # Should show path containing "venv"

# If not activated:
cd backend
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

### Windows-Specific Issues

**Problem:** Scripts fail with "execution policy" error

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Problem:** "python" command not found

**Solution:** Use `python3` instead, or reinstall Python and check "Add to PATH".

### macOS-Specific Issues

**Problem:** "Operation not permitted" errors

**Solution:** Go to System Preferences → Security & Privacy → Privacy → Full Disk Access, and add Terminal or your terminal app.

**Problem:** Xcode tools missing

**Solution:**
```bash
xcode-select --install
```

---

## Next Steps

Now that you have The Private Council running:

1. **Read the README** - Understand features and configuration options
   ```
   README.md
   ```

2. **Explore privacy modes** - Learn about Sovereign, Sanctuary, and Citadel modes
   ```
   docs/ARCHITECTURE.md
   ```

3. **Try different models** - Experiment with model combinations
   ```bash
   ollama pull mistral:7b
   ```

4. **Customize configuration** - Edit council composition
   ```
   config/sovereign_council.yaml
   ```

5. **Contribute!** - Even documentation improvements help
   ```
   docs/CONTRIBUTING_MODEST_HARDWARE.md
   ```

---

## Getting Help

**Stuck?** Here's where to get help:

1. **Check the documentation:**
   - `docs/HARDWARE_REQUIREMENTS.md` - Hardware guidance
   - `docs/ARCHITECTURE.md` - How the system works
   - `docs/CONTRIBUTING_MODEST_HARDWARE.md` - For limited hardware

2. **Search existing issues:**
   - https://github.com/pawn002/private-llm-council/issues

3. **Ask a question:**
   - Open a new issue with your setup details
   - Include: OS, RAM, GPU, error messages

---

## Glossary

| Term | Meaning |
|------|---------|
| **Repository** | A folder containing code, managed by Git |
| **Clone** | Download a copy of a repository |
| **Virtual Environment** | Isolated space for Python packages |
| **Container** | Isolated environment running an application (Docker) |
| **Model** | An AI that can answer questions |
| **Inference** | The process of an AI generating a response |
| **VRAM** | Memory on your graphics card |
| **RAM** | Your computer's main memory |

---

*This guide was created to help newcomers get started. If something is unclear or you found a mistake, please open an issue or submit a pull request!*
