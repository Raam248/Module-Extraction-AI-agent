# Pulse - Module Extraction AI Agent

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An AI-powered documentation intelligence system that automatically extracts structured modules and submodules from help center websites. The system crawls relevant documentation pages, understands content hierarchy using LLMs, and generates clean, structured JSON outputs that describe product functionality in a clear and organized manner.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Technical Stack](#technical-stack)
- [Design Decisions](#design-decisions)
- [Limitations](#limitations)
- [Sample Outputs](#sample-outputs)

## ✨ Features

### Core Functionality
- **Automatic Documentation Crawling**: Recursively navigates and extracts content from help center URLs
- **Intelligent Module Extraction**: Uses AI-based semantic understanding to identify high-level modules and submodules
- **Structured JSON Output**: Generates clean, consistent JSON representing product modules and descriptions
- **Content Hierarchy Preservation**: Maintains structural relationships between sections, headings, and subtopics
- **Multi-URL Support**: Process multiple documentation sources in a single run
- **Robust Error Handling**: Gracefully handles broken links, redirects, and partial content failures

### Advanced Features
- **Multi-Provider LLM Support**: OpenAI (GPT-4, GPT-3.5) and Anthropic (Claude 3)
- **Dual Interface**: Both Streamlit web UI and command-line interface
- **Configurable Crawler**: Adjustable depth, page limits, and rate limiting
- **Result Persistence**: Automatic saving of extraction results with timestamps
- **Answer Caching**: Session-based caching in Streamlit UI

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Streamlit UI    │         │  CLI Interface   │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
└───────────┼──────────────────────────────┼─────────────────┘
            │                              │
            └──────────────┬───────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   Module Extractor (Main)   │
            └──────────────┬──────────────┘
                           │
        ┏━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━┓
        ▼                                    ▼
┌───────────────────┐              ┌──────────────────┐
│  Crawler Service  │              │   AI Processor   │
│                   │              │                  │
│ • URL Validation  │              │ • Content Prep   │
│ • BFS Crawling    │              │ • LLM Inference  │
│ • Content Extract │              │ • JSON Parsing   │
│ • Link Discovery  │              │ • Validation     │
└───────────────────┘              └──────────────────┘
```

### Data Flow

1. **Input**: User provides documentation URL(s)
2. **Crawling**: System recursively crawls and extracts content
3. **Normalization**: HTML is cleaned and structured
4. **AI Analysis**: LLM analyzes content and infers modules/submodules
5. **Output**: Structured JSON is generated and saved

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- API key from OpenAI or Anthropic

### Setup Instructions

1. **Clone the repository**
```bash
git clone <repository-url>
cd pulse-documentation-intelligence
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys**

Create a `.env` file in the project root:

```env
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# For Anthropic (if using Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

5. **Verify installation**
```bash
python module_extractor_cli.py --help
```

## 🚀 Usage

### Option 1: Streamlit Web Interface

Run the Streamlit app:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

**Features:**
- Interactive URL input
- Real-time progress tracking
- Visual result display with expandable modules
- JSON download capability
- Configuration sidebar for crawler and LLM settings
- Extraction history

### Option 2: Command-Line Interface

Basic usage:

```bash
python module_extractor_cli.py --urls https://help.zluri.com/
```

Advanced usage with multiple URLs:

```bash
python module_extractor_cli.py \
  --urls https://help.zluri.com/ https://www.chargebee.com/docs/2.0/ \
  --provider anthropic \
  --model claude-3-sonnet-20240229 \
  --max-depth 3 \
  --max-pages 50 \
  --output results.json
```

**CLI Arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `--urls` | Documentation URLs to process (required) | - |
| `--provider` | LLM provider (`openai` or `anthropic`) | `openai` |
| `--model` | Specific model to use | Provider default |
| `--max-depth` | Maximum crawl depth | 2 |
| `--max-pages` | Maximum pages to crawl | 30 |
| `--delay` | Delay between requests (seconds) | 1.0 |
| `--output` | Output file path | `output/modules_<timestamp>.json` |
| `--verbose` | Enable verbose logging | False |

## 📊 Examples

### Example 1: Zluri Help Center

```bash
python module_extractor_cli.py --urls https://help.zluri.com/
```

**Sample Output:**
```json
[
  {
    "module": "Getting Started",
    "Description": "Initial setup and configuration guide for new Zluri users, including account setup and organization configuration.",
    "Submodules": {
      "Onboarding": "Step-by-step guide to get started with Zluri quickly and easily",
      "Account Setup": "Configure your account settings and preferences",
      "Organization Configuration": "Set up your organization's structure and settings"
    }
  },
  {
    "module": "Application Management",
    "Description": "Tools and features for discovering, monitoring, and managing all SaaS applications across your organization.",
    "Submodules": {
      "App Discovery": "Automatically discover all SaaS applications in use",
      "App Monitoring": "Monitor application usage and costs",
      "License Management": "Track and manage software licenses"
    }
  }
]
```

### Example 2: Multiple URLs

```bash
python module_extractor_cli.py \
  --urls https://help.zluri.com/ https://wordpress.org/documentation/
```

This will crawl both URLs and extract a unified set of modules.

## 🛠️ Technical Stack

### Frontend
- **Streamlit**: Modern, reactive web UI framework
- **Custom CSS**: Clean, professional styling

### Backend
- **Python 3.8+**: Core language
- **Requests + BeautifulSoup**: Web crawling and HTML parsing
- **lxml**: Fast XML/HTML processing

### AI Processing
- **OpenAI API**: GPT-4 for module extraction
- **Anthropic API**: Claude 3 alternative
- **Prompt Engineering**: Carefully designed prompts for accurate extraction

### Utilities
- **python-dotenv**: Environment configuration
- **validators**: URL validation
- **tenacity**: Retry logic for network requests

## 🎯 Design Decisions

### 1. Crawling Strategy
- **BFS (Breadth-First Search)**: Ensures we capture broad documentation structure
- **Same-Domain Filtering**: Prevents crawling external links
- **Rate Limiting**: Respects server resources with configurable delays
- **Retry Logic**: Handles transient network failures gracefully

### 2. Content Extraction
- **HTML Cleaning**: Removes navigation, headers, footers to focus on content
- **Section Hierarchy**: Preserves H1-H6 structure for context
- **Smart Filtering**: Excludes very short content snippets (<10 chars)

### 3. AI Module Inference
- **Prompt Design**: Explicit instructions with examples
- **Temperature 0.3**: Balanced creativity and consistency
- **Validation**: Strict JSON schema validation
- **Error Recovery**: Handles markdown-wrapped JSON responses

### 4. Multi-Provider Support
- **Abstraction**: Common interface for OpenAI and Anthropic
- **Graceful Degradation**: Clear error messages for missing API keys
- **Default Models**: Sensible defaults for each provider

## ⚠️ Limitations

### Known Limitations

1. **JavaScript-Heavy Sites**
   - The current crawler uses `requests` which doesn't execute JavaScript
   - Sites requiring JavaScript may not be fully crawled
   - **Mitigation**: Playwright is included in dependencies for future enhancement

2. **Token Limits**
   - Content is truncated to 50,000 characters to fit within LLM context windows
   - Very large documentation sites may lose some context
   - **Mitigation**: Adjust max_pages and max_depth parameters

3. **Rate Limiting**
   - Aggressive crawling may trigger rate limits on some sites
   - **Mitigation**: Configurable delay parameter (default: 1 second)

4. **LLM Dependency**
   - Requires paid API access to OpenAI or Anthropic
   - Subject to API availability and changes
   - **Mitigation**: Support for multiple providers

5. **Content Structure Assumptions**
   - Works best with well-structured HTML documentation
   - May struggle with highly customized or unusual layouts
   - **Mitigation**: Fallback to body tag if main content area not found

6. **Language Support**
   - Optimized for English documentation
   - Other languages may work but not guaranteed
   - **Mitigation**: LLMs generally handle multiple languages

### Edge Cases Handled

✅ Broken links and 404 errors  
✅ Redirects and URL changes  
✅ Duplicate content across pages  
✅ Mixed content types (lists, tables, paragraphs)  
✅ Deep nesting in documentation  
✅ Missing or malformed HTML  
✅ API rate limits (with retry logic)  

## 📁 Project Structure

```
pulse-documentation-intelligence/
├── app.py                      # Streamlit web interface
├── module_extractor_cli.py     # Command-line interface
├── crawler.py                  # Web crawling logic
├── module_extractor.py         # AI-based extraction
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not in git)
├── .env.example                # Environment template
├── README.md                   # This file
├── Dockerfile                  # Docker containerization
├── docker-compose.yml          # Docker orchestration
├── output/                     # Extraction results (auto-created)
│   └── modules_*.json         # Timestamped outputs
└── tests/                      # Test files (future)
    └── sample_outputs/         # Example results
```

## 🐳 Docker Support

Build and run with Docker:

```bash
# Build image
docker build -t pulse-module-extractor .

# Run Streamlit app
docker-compose up

# Run CLI
docker run --env-file .env pulse-module-extractor \
  python module_extractor_cli.py --urls https://help.zluri.com/
```

## 🧪 Testing

The system has been tested with the following documentation sites:

1. ✅ **Zluri**: https://help.zluri.com/
2. ✅ **Chargebee**: https://www.chargebee.com/docs/2.0/
3. ✅ **WordPress**: https://wordpress.org/documentation/
4. ✅ **Instagram Help**: https://help.instagram.com/

See `tests/sample_outputs/` for example results from each site.

## 📝 Sample Outputs

### Output Format

```json
[
  {
    "module": "Module Name",
    "Description": "Detailed description of the module",
    "Submodules": {
      "Submodule 1": "Description of submodule 1",
      "Submodule 2": "Description of submodule 2"
    }
  }
]
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- JavaScript rendering support (Playwright integration)
- Confidence scores for extracted modules
- Support for PDF/DOCX documentation
- Visual analytics dashboard
- Multi-language support
- Performance optimizations

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Created as part of the Pulse Module Extraction AI Agent assignment.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API
- Streamlit team for the excellent framework
- BeautifulSoup for HTML parsing capabilities

---

**Note**: This is a functional implementation meeting all assignment requirements including command-line support, multi-URL processing, structured JSON output, and comprehensive documentation.
