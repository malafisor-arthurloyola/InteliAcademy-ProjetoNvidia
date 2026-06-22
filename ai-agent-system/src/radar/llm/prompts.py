EXTRACTION_PROMPT = """You are an expert analyst extracting structured data about a Brazilian startup from public web sources.

Given the collected text below, extract the following fields. Return ONLY valid JSON (no markdown, no code blocks):

{{
  "name": "<startup/company name or null>",
  "sector": "<one of: Healthcare, Fintech, Agrotech, Edtech, Logistics, Retail, Legal, Real Estate, Energy, Cybersecurity, Gaming, Robotics, Data & Analytics, Voice AI, Sales & Marketing, Customer Service, or null>",
  "product": "<product name or null>",
  "founders": ["<founder name or empty list>"],
  "funding": "<funding info or null>",
  "technologies": ["<technology name or empty list>"],
  "ai_usage_summary": "<2-3 sentence summary of AI usage based on evidence>"
}}

Be conservative: only extract what is explicitly mentioned. Use null for unknown fields. If the search query is generic, infer the startup name from the collected source text, not from the query.
For technologies, list both NVIDIA and non-NVIDIA technologies cited.
Keep ai_usage_summary factual, citing specific evidence from the text."""

CLASSIFICATION_PROMPT = """You are an expert analyst classifying Brazilian startups by their AI maturity level.

Given the extracted startup profile and collected text, classify as one of:

- "AI-Native": Product DEPENDS on AI to deliver value. Signs: proprietary data, custom fine-tuning, multi-agent systems, deep learning models, autonomous workflows, NVIDIA technologies.
- "AI-Enabled": Uses AI operationally but doesn't depend on it as core business. Signs: LLM APIs, chatbots, workflow automation, content generation.
- "Non-AI": No meaningful AI usage found in available evidence.

Return ONLY valid JSON (no markdown, no code blocks):

{{
  "label": "<AI-Native|AI-Enabled|Non-AI>",
  "confidence": <float between 0.0 and 1.0>,
  "rationale": "<2-3 sentence justification referencing specific evidence>",
  "caveats": ["<list of caveats or empty list>"]
}}

Be conservative: if evidence is thin, lean toward AI-Enabled or Non-AI.
If NVIDIA technologies are cited, add a caveat about NVIDIA Inception eligibility."""
