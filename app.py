"""
Pulse - Documentation Intelligence System
Streamlit Application for Module Extraction
"""

import streamlit as st
import json
import logging
from datetime import datetime
import os
from pathlib import Path

from crawler import DocumentationCrawler
from module_extractor import ModuleExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Pulse - Module Extraction AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #145a8d;
    }
    .json-output {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'crawled_data' not in st.session_state:
        st.session_state.crawled_data = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'history' not in st.session_state:
        st.session_state.history = []


def save_to_history(urls, results):
    """Save extraction results to history"""
    history_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'urls': urls,
        'num_modules': len(results) if results else 0
    }
    st.session_state.history.insert(0, history_entry)
    
    # Keep only last 10 entries
    if len(st.session_state.history) > 10:
        st.session_state.history = st.session_state.history[:10]


def display_results(results):
    """Display extracted modules in a formatted way"""
    if not results:
        st.warning("No modules extracted.")
        return
    
    st.success(f"✅ Extracted {len(results)} modules successfully!")
    
    # Display each module
    for idx, module in enumerate(results, 1):
        with st.expander(f"📦 {module['module']}", expanded=(idx == 1)):
            st.markdown(f"**Description:** {module['Description']}")
            
            st.markdown("**Submodules:**")
            for submodule_name, submodule_desc in module['Submodules'].items():
                st.markdown(f"- **{submodule_name}**: {submodule_desc}")


def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">📚 Pulse - Module Extraction AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Extract structured modules from documentation automatically</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # LLM Provider selection
        provider = st.selectbox(
            "LLM Provider",
            ["OpenAI", "Anthropic"],
            help="Choose your preferred LLM provider"
        )
        
        # Model selection
        if provider == "OpenAI":
            model_options = ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"]
            default_model = "gpt-4-turbo-preview"
        else:
            model_options = ["claude-3-sonnet-20240229", "claude-3-opus-20240229"]
            default_model = "claude-3-sonnet-20240229"
        
        model = st.selectbox("Model", model_options, index=0)
        
        # Crawler settings
        st.subheader("🕷️ Crawler Settings")
        max_depth = st.slider("Max Depth", 1, 5, 2, help="Maximum depth for recursive crawling")
        max_pages = st.slider("Max Pages", 10, 100, 30, help="Maximum number of pages to crawl")
        delay = st.slider("Delay (seconds)", 0.5, 3.0, 1.0, 0.5, help="Delay between requests")
        
        # API Key check
        st.subheader("🔑 API Key Status")
        if provider == "OpenAI":
            api_key = os.getenv("OPENAI_API_KEY")
            key_name = "OPENAI_API_KEY"
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            key_name = "ANTHROPIC_API_KEY"
        
        if api_key:
            st.success(f"✓ {key_name} found")
        else:
            st.error(f"✗ {key_name} not found")
            st.info("Please set your API key in a .env file")
        
        # History
        st.subheader("📜 Recent Runs")
        if st.session_state.history:
            for entry in st.session_state.history[:5]:
                st.text(f"{entry['timestamp']}")
                st.caption(f"Modules: {entry['num_modules']}")
        else:
            st.info("No history yet")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🔍 Extract Modules", "📊 View Results", "ℹ️ About"])
    
    with tab1:
        st.header("Extract Modules from Documentation")
        
        # URL input
        st.subheader("Enter Documentation URLs")
        url_input = st.text_area(
            "URLs (one per line)",
            height=150,
            placeholder="https://help.zluri.com/\nhttps://www.chargebee.com/docs/2.0/\nhttps://wordpress.org/documentation/",
            help="Enter one or more documentation URLs, each on a new line"
        )
        
        # Quick examples
        st.markdown("**Quick Examples:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Zluri"):
                url_input = "https://help.zluri.com/"
        with col2:
            if st.button("Chargebee"):
                url_input = "https://www.chargebee.com/docs/2.0/"
        with col3:
            if st.button("WordPress"):
                url_input = "https://wordpress.org/documentation/"
        with col4:
            if st.button("Instagram"):
                url_input = "https://help.instagram.com/"
        
        # Process button
        col1, col2 = st.columns([3, 1])
        with col1:
            process_button = st.button("🚀 Start Extraction", disabled=st.session_state.processing)
        with col2:
            if st.session_state.processing:
                st.spinner("Processing...")
        
        # Processing logic
        if process_button and url_input:
            # Parse URLs
            urls = [url.strip() for url in url_input.split('\n') if url.strip()]
            
            if not urls:
                st.error("Please enter at least one URL")
            elif not api_key:
                st.error(f"Please set {key_name} in your .env file")
            else:
                st.session_state.processing = True
                
                try:
                    # Create output directory
                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Step 1: Crawl documentation
                    status_text.text("🕷️ Crawling documentation...")
                    progress_bar.progress(20)
                    
                    crawler = DocumentationCrawler(
                        max_depth=max_depth,
                        max_pages=max_pages,
                        delay=delay
                    )
                    
                    all_crawled_data = []
                    for idx, url in enumerate(urls):
                        status_text.text(f"🕷️ Crawling {url} ({idx+1}/{len(urls)})...")
                        crawled_data = crawler.crawl(url)
                        all_crawled_data.extend(crawled_data)
                        progress_bar.progress(20 + (30 * (idx + 1) // len(urls)))
                    
                    st.session_state.crawled_data = all_crawled_data
                    
                    if not all_crawled_data:
                        st.error("Failed to crawl any pages. Please check the URLs and try again.")
                        st.session_state.processing = False
                        return
                    
                    status_text.text(f"✓ Crawled {len(all_crawled_data)} pages successfully")
                    
                    # Step 2: Extract modules using AI
                    status_text.text("🤖 Analyzing content with AI...")
                    progress_bar.progress(60)
                    
                    extractor = ModuleExtractor(
                        provider=provider.lower(),
                        model=model
                    )
                    
                    results = extractor.extract_modules(all_crawled_data)
                    progress_bar.progress(90)
                    
                    if not results:
                        st.error("Failed to extract modules. The LLM may have returned invalid data.")
                        st.session_state.processing = False
                        return
                    
                    # Save results
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = output_dir / f"modules_{timestamp}.json"
                    extractor.save_results(results, str(output_file))
                    
                    st.session_state.results = results
                    save_to_history(urls, results)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Extraction complete!")
                    
                    st.success(f"🎉 Successfully extracted {len(results)} modules!")
                    st.info(f"Results saved to: {output_file}")
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    logger.exception("Error during processing")
                
                finally:
                    st.session_state.processing = False
    
    with tab2:
        st.header("Extraction Results")
        
        if st.session_state.results:
            # Download button
            col1, col2 = st.columns([3, 1])
            with col2:
                json_str = json.dumps(st.session_state.results, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"modules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            # Display results
            display_results(st.session_state.results)
            
            # Raw JSON view
            with st.expander("📄 View Raw JSON"):
                st.json(st.session_state.results)
        else:
            st.info("No results yet. Extract modules from the 'Extract Modules' tab.")
    
    with tab3:
        st.header("About Pulse")
        
        st.markdown("""
        **Pulse** is an AI-powered documentation intelligence system that automatically extracts 
        structured modules and submodules from help center websites.
        
        ### Features
        - 🕷️ **Automatic Crawling**: Recursively crawls documentation pages
        - 🤖 **AI-Powered Analysis**: Uses LLM for semantic understanding
        - 📊 **Structured Output**: Generates clean JSON with modules and submodules
        - 🔄 **Multi-URL Support**: Process multiple documentation sources
        - 💾 **Export Results**: Download results as JSON
        
        ### How It Works
        1. Enter one or more documentation URLs
        2. The system crawls linked pages automatically
        3. AI analyzes content structure and relationships
        4. Modules and submodules are identified and described
        5. Structured JSON output is generated
        
        ### Supported LLM Providers
        - OpenAI (GPT-4, GPT-3.5)
        - Anthropic (Claude 3)
        
        ### Technical Stack
        - **Frontend**: Streamlit
        - **Crawler**: BeautifulSoup + Requests
        - **AI**: OpenAI/Anthropic APIs
        - **Language**: Python 3.8+
        """)
        
        st.divider()
        
        st.markdown("""
        ### Setup Instructions
        1. Clone the repository
        2. Install dependencies: `pip install -r requirements.txt`
        3. Create `.env` file with your API key:
           - For OpenAI: `OPENAI_API_KEY=your_key`
           - For Anthropic: `ANTHROPIC_API_KEY=your_key`
        4. Run the app: `streamlit run app.py`
        """)


if __name__ == "__main__":
    main()
