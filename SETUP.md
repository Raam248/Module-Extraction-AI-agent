# Quick Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI or Anthropic API key

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd pulse-documentation-intelligence
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your API key:

```env
OPENAI_API_KEY=sk-your-actual-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### 5. Verify Installation

```bash
python module_extractor_cli.py --help
```

You should see the help message with all available options.

## Running the Application

### Option A: Streamlit Web UI

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Option B: Command Line

```bash
python module_extractor_cli.py --urls https://help.zluri.com/
```

## Quick Test

Test with a simple example:

```bash
python module_extractor_cli.py --urls https://help.zluri.com/ --max-pages 10
```

Expected behavior:
1. Crawls up to 10 pages from Zluri help center
2. Extracts modules and submodules using AI
3. Saves results to `output/modules_<timestamp>.json`
4. Prints JSON output to console

## Troubleshooting

### "ModuleNotFoundError"
- Make sure you've installed dependencies: `pip install -r requirements.txt`
- Activate your virtual environment

### "API Key not found"
- Check that `.env` file exists in the project root
- Verify the API key format (starts with `sk-` for OpenAI, `sk-ant-` for Anthropic)
- Ensure no extra spaces or quotes in the `.env` file

### "Failed to crawl any pages"
- Check your internet connection
- Verify the URL is accessible in your browser
- Try with a different documentation URL

### Slow Performance
- Reduce `--max-pages` (default: 30)
- Reduce `--max-depth` (default: 2)
- The delay between requests ensures we don't get blocked

## Docker Alternative

If you prefer Docker:

```bash
# Build
docker build -t pulse-module-extractor .

# Run Streamlit
docker-compose up

# Run CLI
docker run --env-file .env pulse-module-extractor python module_extractor_cli.py --urls https://help.zluri.com/
```

## Next Steps

1. Read the [README.md](README.md) for comprehensive documentation
2. Check [DESIGN.md](DESIGN.md) for technical details
3. Try extracting from different documentation sites
4. Experiment with different LLM providers and models

## Getting Help

If you encounter issues:

1. Check the logs in the console output
2. Verify all prerequisites are met
3. Try with a simpler example first
4. Check that the documentation URL is publicly accessible

## Example Commands

**Single URL:**
```bash
python module_extractor_cli.py --urls https://help.zluri.com/
```

**Multiple URLs:**
```bash
python module_extractor_cli.py --urls https://help.zluri.com/ https://wordpress.org/documentation/
```

**Using Anthropic:**
```bash
python module_extractor_cli.py --urls https://help.zluri.com/ --provider anthropic
```

**Custom Output:**
```bash
python module_extractor_cli.py --urls https://help.zluri.com/ --output my_results.json
```

**Verbose Logging:**
```bash
python module_extractor_cli.py --urls https://help.zluri.com/ --verbose
```

---

You're all set! Start extracting modules from documentation. 🚀
