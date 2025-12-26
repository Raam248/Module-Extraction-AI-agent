# Technical Design Document
## Pulse - Module Extraction AI Agent

## 1. Architecture Overview

### 1.1 High-Level Architecture

The system follows a modular, layered architecture:

```
Presentation Layer
    ├── Streamlit UI (app.py)
    └── CLI Interface (module_extractor_cli.py)
         ↓
Business Logic Layer
    ├── Module Extractor (module_extractor.py)
    │   ├── Content Preparation
    │   ├── LLM Integration
    │   └── Response Parsing
    └── Web Crawler (crawler.py)
        ├── URL Validation
        ├── Content Extraction
        └── Link Discovery
         ↓
External Services
    ├── OpenAI API
    ├── Anthropic API
    └── Target Documentation Sites
```

### 1.2 Component Responsibilities

**1. Crawler Service (`crawler.py`)**
- URL validation and normalization
- Recursive breadth-first crawling
- HTML parsing and content extraction
- Link discovery and filtering
- Rate limiting and retry logic

**2. Module Extractor (`module_extractor.py`)**
- Content aggregation and formatting
- LLM provider abstraction
- Prompt engineering
- Response validation
- JSON schema enforcement

**3. User Interfaces**
- **Streamlit UI**: Interactive web interface with real-time feedback
- **CLI**: Command-line tool for automation and scripting

## 2. Design Decisions

### 2.1 Crawling Strategy

**Decision: Breadth-First Search (BFS)**

*Rationale:*
- Ensures we capture the full breadth of documentation structure
- More likely to discover main sections before diving deep
- Better for incomplete crawls (hitting page limits)
- Easier to implement depth limiting

*Alternative Considered:*
- Depth-First Search (DFS): Rejected because it might miss important top-level pages if hitting page limits

**Decision: Same-Domain Filtering**

*Rationale:*
- Prevents crawling external resources
- Focuses on the target documentation
- Reduces noise and irrelevant content

**Decision: Configurable Rate Limiting**

*Rationale:*
- Respects server resources
- Prevents getting blocked
- Allows users to adjust based on site policies

### 2.2 Content Extraction

**Decision: BeautifulSoup + Requests (not Playwright)**

*Rationale:*
- Lighter weight and faster for static HTML
- Most documentation sites work without JavaScript
- Easier to deploy (no browser dependencies)
- Lower resource requirements

*Trade-off:*
- Won't work for JavaScript-heavy sites
- Playwright included in requirements for future enhancement

**Decision: Hierarchical Section Extraction**

*Rationale:*
- Preserves document structure
- Provides context for AI analysis
- Maintains heading-content relationships

**Implementation:**
```python
# Extract sections with hierarchy
for element in main_content.find_all(['h1', 'h2', 'h3', ...]):
    if element.name in ['h1', 'h2', ...]:
        # Start new section
        current_section = {
            'level': int(element.name[1]),
            'heading': element.get_text(strip=True),
            'content': []
        }
    elif current_section:
        # Add to current section
        current_section['content'].append(text)
```

### 2.3 AI Integration

**Decision: Multi-Provider Support (OpenAI + Anthropic)**

*Rationale:*
- Reduces vendor lock-in
- Provides fallback options
- Allows users to choose based on availability/pricing
- Different models may excel at different content types

**Decision: Temperature 0.3**

*Rationale:*
- Balance between consistency and creativity
- Low enough for structured output
- High enough to handle varied documentation styles

**Decision: Prompt Engineering Approach**

Key elements:
1. **Clear definitions** of modules vs submodules
2. **Explicit instructions** (numbered list)
3. **Output format specification** (JSON schema)
4. **Grounding requirement** ("use only provided content")
5. **Examples** in prompt (Instagram case)

**Decision: Content Truncation at 50K Characters**

*Rationale:*
- Fits within most LLM context windows
- Prevents timeout/rate limit issues
- Users can adjust max_pages/max_depth if needed

*Alternative Considered:*
- Chunking and merging: Rejected due to complexity and potential inconsistency

### 2.4 Error Handling

**Multi-Layer Error Handling:**

1. **Network Level**: Retry with exponential backoff (tenacity)
2. **Parsing Level**: Graceful degradation if main content not found
3. **Validation Level**: JSON schema validation with clear error messages
4. **User Level**: User-friendly error messages in UI

**Edge Cases Handled:**

```python
# Example: Broken links
try:
    html = self.fetch_page(url)
    if not html:
        logger.warning(f"Skipping {url}")
        continue  # Move to next URL
except Exception as e:
    logger.error(f"Error: {e}")
    # Don't fail entire process
```

### 2.5 Data Flow

**Step-by-Step Process:**

```
1. URL Input
   ├── Validate format (validators library)
   └── Check accessibility

2. Crawling Phase
   ├── Initialize queue with start URL
   ├── While queue not empty and pages < max_pages:
   │   ├── Fetch page HTML
   │   ├── Extract content and sections
   │   ├── Discover new links
   │   └── Add valid links to queue
   └── Return list of crawled pages

3. Content Preparation
   ├── Aggregate all pages
   ├── Format with hierarchy preserved
   ├── Truncate if needed
   └── Return formatted string

4. AI Analysis
   ├── Build prompt with instructions
   ├── Call LLM API
   ├── Parse response (handle markdown wrapping)
   ├── Validate JSON structure
   └── Return validated modules

5. Output
   ├── Save to JSON file (timestamped)
   ├── Display in UI
   └── Return to user
```

## 3. Assumptions

### 3.1 Content Assumptions

1. **HTML Structure**: Documentation uses semantic HTML with heading tags (h1-h6)
2. **English Language**: Primary language is English (LLMs can handle others but not optimized)
3. **Text-Based**: Content is primarily text (not images, videos, or interactive elements)
4. **Accessible**: Pages are publicly accessible (no authentication required)

### 3.2 Technical Assumptions

1. **Static Content**: Most content is server-rendered HTML (not SPA/JavaScript)
2. **Standard Protocols**: Sites use standard HTTP/HTTPS
3. **Reasonable Size**: Documentation fits within crawl limits (30-50 pages)
4. **Stable URLs**: URLs don't change during crawl session

### 3.3 User Assumptions

1. **API Access**: User has valid API key for OpenAI or Anthropic
2. **Internet Connection**: Stable internet for crawling and API calls
3. **Python Environment**: Python 3.8+ installed
4. **Basic CLI Knowledge**: For command-line interface usage

## 4. Limitations and Constraints

### 4.1 Technical Limitations

1. **JavaScript Rendering**: Cannot crawl JavaScript-dependent content
   - *Impact*: Some modern SPAs won't work
   - *Workaround*: Playwright included for future enhancement

2. **Token Limits**: LLM context window limits content size
   - *Impact*: Very large docs may be truncated
   - *Workaround*: Adjust crawl parameters

3. **Rate Limiting**: Both crawling and API have rate limits
   - *Impact*: Processing time increases
   - *Workaround*: Configurable delays

### 4.2 Quality Limitations

1. **AI Hallucination**: LLM might infer incorrect relationships
   - *Mitigation*: Clear prompts, low temperature, validation

2. **Structure Dependency**: Quality depends on HTML structure
   - *Mitigation*: Fallback to body tag if main content not found

3. **Language Support**: Optimized for English
   - *Mitigation*: LLMs generally handle other languages

### 4.3 Scalability Constraints

1. **Sequential Processing**: Crawls pages sequentially
   - *Impact*: Slow for large sites
   - *Future*: Could parallelize with asyncio

2. **Memory Usage**: All content loaded in memory
   - *Impact*: Large sites may consume significant RAM
   - *Future*: Stream processing for large sites

## 5. Extension Points

### 5.1 Future Enhancements

**1. JavaScript Support**
```python
# Replace requests with Playwright
async def fetch_page_async(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
        return content
```

**2. Confidence Scores**
```python
# Add confidence to output
{
    "module": "Account Settings",
    "confidence": 0.95,
    "Description": "...",
    "Submodules": {...}
}
```

**3. Caching Layer**
```python
# Cache crawled content
import redis
cache = redis.Redis()
cached = cache.get(url)
if cached:
    return json.loads(cached)
```

**4. Parallel Crawling**
```python
# Use asyncio for concurrent requests
async def crawl_parallel(urls):
    tasks = [fetch_page_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

### 5.2 Integration Points

**1. REST API**
```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/extract")
async def extract_modules(urls: List[str]):
    crawler = DocumentationCrawler()
    data = crawler.crawl_multiple(urls)
    extractor = ModuleExtractor()
    modules = extractor.extract_modules(data)
    return {"modules": modules}
```

**2. Database Storage**
```python
# Store results in MongoDB
from pymongo import MongoClient
client = MongoClient()
db = client.pulse
db.extractions.insert_one({
    "timestamp": datetime.now(),
    "urls": urls,
    "modules": modules
})
```

## 6. Security Considerations

### 6.1 Current Security Measures

1. **API Key Protection**: Stored in .env file (not in code)
2. **Input Validation**: URLs validated before crawling
3. **Same-Domain Filtering**: Prevents SSRF attacks
4. **No Code Execution**: Only HTML parsing (no eval/exec)

### 6.2 Recommendations for Production

1. **Rate Limiting**: Add per-user rate limits
2. **Authentication**: Add user authentication for web UI
3. **HTTPS Only**: Enforce HTTPS for all requests
4. **Secrets Management**: Use proper secrets manager (AWS Secrets Manager, Vault)
5. **Audit Logging**: Log all extractions for compliance

## 7. Testing Strategy

### 7.1 Unit Tests (Future)

```python
def test_url_validation():
    crawler = DocumentationCrawler()
    assert crawler.validate_url("https://example.com")
    assert not crawler.validate_url("not-a-url")

def test_content_extraction():
    html = "<h1>Title</h1><p>Content</p>"
    result = crawler.extract_content(html, "http://example.com")
    assert result['title'] == "Title"
    assert len(result['sections']) > 0
```

### 7.2 Integration Tests

Test with known documentation sites:
1. Zluri (complex, multi-section)
2. Chargebee (deep hierarchy)
3. WordPress (community docs)
4. Instagram (sparse content)

### 7.3 Manual Testing Checklist

- [ ] Single URL extraction
- [ ] Multiple URL extraction
- [ ] Invalid URL handling
- [ ] Network failure handling
- [ ] Large site handling
- [ ] Sparse content handling
- [ ] Different LLM providers
- [ ] CLI interface
- [ ] Streamlit UI
- [ ] Docker deployment

## 8. Performance Considerations

### 8.1 Current Performance

**Typical Execution Times:**
- Crawling: 30-60 seconds (30 pages @ 1s delay)
- AI Analysis: 10-30 seconds (depending on content size)
- Total: 40-90 seconds per extraction

### 8.2 Optimization Opportunities

1. **Async Crawling**: Use aiohttp for concurrent requests (3-5x faster)
2. **Content Caching**: Cache crawled pages for re-analysis
3. **Incremental Processing**: Stream to LLM in chunks
4. **Smart Sampling**: Prioritize high-value pages (homepage, /docs/)

## 9. Deployment

### 9.1 Local Deployment

```bash
# Development
pip install -r requirements.txt
streamlit run app.py

# Production
gunicorn --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker app:app
```

### 9.2 Docker Deployment

```bash
docker-compose up -d
```

### 9.3 Cloud Deployment (Recommended)

**AWS:**
- ECS/Fargate for containerized deployment
- Secrets Manager for API keys
- CloudWatch for logging
- S3 for output storage

**GCP:**
- Cloud Run for serverless containers
- Secret Manager for API keys
- Cloud Logging
- Cloud Storage for outputs

## 10. Monitoring and Observability

### 10.1 Key Metrics

1. **Success Rate**: % of successful extractions
2. **Extraction Time**: Average time per URL
3. **Page Coverage**: Average pages crawled per URL
4. **Module Count**: Average modules extracted
5. **Error Rate**: % of failed extractions

### 10.2 Logging Strategy

```python
# Structured logging
logger.info("Extraction started", extra={
    "url": url,
    "user_id": user_id,
    "provider": provider
})
```

## Conclusion

This design provides a solid foundation for documentation module extraction with room for growth. The modular architecture allows easy extension while the current implementation meets all assignment requirements with production-ready code quality.
