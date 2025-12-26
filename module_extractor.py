"""
AI-Powered Module Extraction System
Uses LLMs to infer modules and submodules from documentation content
"""

import json
import logging
import os
import subprocess
import sys
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# ============================
# ENV + ENCODING FIX
# ============================

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

# ============================
# LOGGING
# ============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ============================
# OPTIONAL PROVIDERS
# ============================

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ModuleExtractor:
    """
    Extracts modules and submodules using AI-based semantic understanding.
    """

    def __init__(self, provider: str = "local", model: Optional[str] = None):
        self.provider = provider.lower()

        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI SDK not installed")

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY not found")

            self.client = OpenAI(api_key=api_key)
            self.model = model or "gpt-4o"

        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic SDK not installed")

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY not found")

            self.client = Anthropic(api_key=api_key)
            self.model = model or "claude-3-sonnet-20240229"

        elif self.provider == "local":
            self.model = model or "llama3"

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        logger.info(f"ModuleExtractor initialized with provider={self.provider}")

    # --------------------------------------------------
    # CONTENT PREP
    # --------------------------------------------------

    def prepare_content_for_analysis(self, crawled_data: List[Dict]) -> str:
        blocks = []

        for page in crawled_data:
            block = f"\n## Page: {page.get('title', 'Untitled')}\n"
            block += f"URL: {page.get('url', 'N/A')}\n"

            for section in page.get("sections", []):
                indent = "  " * (section.get("level", 1) - 1)
                block += f"{indent}### {section.get('heading', '')}\n"

                for item in section.get("content", []):
                    block += f"{indent}{item}\n"

            blocks.append(block)

        return "\n".join(blocks)

    # --------------------------------------------------
    # MAIN EXTRACTION
    # --------------------------------------------------

    def extract_modules(self, crawled_data: List[Dict]) -> List[Dict]:
        if not crawled_data:
            logger.warning("No crawled data provided.")
            return []

        content = self.prepare_content_for_analysis(crawled_data)

        if len(content) > 50000:
            logger.warning("Content truncated to avoid token overflow.")
            content = content[:50000] + "\n\n[TRUNCATED CONTENT]"

        prompt = self._create_prompt(content)

        try:
            if self.provider == "openai":
                response = self._call_openai(prompt)
            elif self.provider == "anthropic":
                response = self._call_anthropic(prompt)
            else:
                response = self._call_local_llm(prompt)

            return self._parse_llm_response(response)

        except Exception as e:
            logger.error(f"Module extraction failed: {e}")
            return []

    # --------------------------------------------------
    # PROMPT
    # --------------------------------------------------

    def _create_prompt(self, content: str) -> str:
        return f"""
You are analyzing software documentation to identify product modules and submodules.

RULES:
- Identify 5–10 major modules
- Each module should have 2–8 submodules
- Use only provided content
- Do NOT hallucinate
- Be concise and accurate

DOCUMENTATION:
{content}

OUTPUT FORMAT (JSON ONLY):

[
  {{
    "module": "Module Name",
    "Description": "Description of this module",
    "Submodules": {{
      "Submodule Name": "Description",
      "Submodule Name 2": "Description"
    }}
  }}
]
"""

    # --------------------------------------------------
    # LLM CALLS
    # --------------------------------------------------

    def _call_openai(self, prompt: str) -> str:
        logger.info("Calling OpenAI API")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a technical documentation analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        return response.choices[0].message.content

    def _call_anthropic(self, prompt: str) -> str:
        logger.info("Calling Anthropic API")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def _call_local_llm(self, prompt: str) -> str:
        logger.info("Calling local LLM (Ollama)")

        try:
            result = subprocess.run(
                f'ollama run {self.model}',
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                shell=True
            )

            if result.returncode != 0:
                logger.error(f"Ollama error: {result.stderr}")
                return ""

            return result.stdout

        except Exception as e:
            logger.error(f"Local LLM execution failed: {e}")
            return ""

    # --------------------------------------------------
    # PARSING
    # --------------------------------------------------

    def _parse_llm_response(self, response: str) -> List[Dict]:
        try:
            response = response.strip()

            if response.startswith("```"):
                response = response.split("```")[1]

            parsed = json.loads(response)

            if not isinstance(parsed, list):
                return []

            return [m for m in parsed if self._validate_module(m)]

        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return []

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    def _validate_module(self, module: Dict) -> bool:
        return (
            isinstance(module, dict)
            and "module" in module
            and "Description" in module
            and isinstance(module.get("Submodules"), dict)
        )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    def save_results(self, modules: List[Dict], output_path: str):
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(modules, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
