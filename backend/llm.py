import time
import requests
import logging

logger = logging.getLogger("llm")

SYSTEM_PROMPT = """You are an advanced grounded Question-Answering system.
Your goal is to answer the user's question using ONLY the provided text chunks.

STRICT RULES:
1. Do NOT guess, assume, or hallucinate.
2. Use ONLY the facts directly mentioned in the provided chunks.
3. If answer is not in chunks, say: "Information not found in the available knowledge base."
4. If partially available, say: "The required information is not available in the provided sources."
5. Always stay grounded.

Context Chunks:
{context}
"""


class LLMManager:
    def __init__(self,
                 ollama_model="mistral:latest",
                 groq_api_key=None,
                 groq_model="llama-3.3-70b-versatile"):

        self.ollama_model = ollama_model
        self.groq_api_key = groq_api_key
        self.groq_model = groq_model

        # FIX 1: correct Ollama endpoint (IMPORTANT)
        self.ollama_url = "http://localhost:11434/api/generate"

    # -----------------------------
    # FORMAT CONTEXT (UNCHANGED)
    # -----------------------------
    def format_context(self, chunks):
        formatted_blocks = []

        for idx, chunk in enumerate(chunks):
            meta = chunk.get("metadata", {})
            source = meta.get("source", "Unknown")
            source_type = meta.get("source_type", "Unknown")
            heading = meta.get("heading", "")
            timestamp = meta.get("timestamp", "")

            ref_info = f"Source: {source} ({source_type})"
            if heading:
                ref_info += f" | Heading: {heading}"
            if timestamp:
                ref_info += f" | Timestamp: {timestamp}"

            block = f"--- CHUNK {idx+1} ({ref_info}) ---\n{chunk['text']}\n"
            formatted_blocks.append(block)

        return "\n".join(formatted_blocks)

    # -----------------------------
    # MAIN GENERATION FUNCTION
    # -----------------------------
    def generate_answer(self, question, chunks, mode="hybrid"):

        context = self.format_context(chunks)
        system_prompt = SYSTEM_PROMPT.format(context=context)

        start_time = time.time()

        # =====================================================
        # 1. OLLAMA PRIMARY (FIXED)
        # =====================================================
        try:
            logger.info(f"Using Ollama ({self.ollama_model})...")

            payload = {
                "model": self.ollama_model,

                # FIX 2: correct prompt format (NO messages)
                "prompt": system_prompt + "\n\nQuestion:\n" + question,

                "stream": False,
                "options": {
                    "temperature": 0.0
                }
            }

            response = requests.post(
                self.ollama_url,
                json=payload,

                # FIX 3: increased timeout (VERY IMPORTANT)
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()

                # Ollama generate response format
                answer = data.get("response", "").strip()

                latency_ms = int((time.time() - start_time) * 1000)
                logger.info(f"Ollama success in {latency_ms}ms")

                return answer, "ollama", latency_ms

            else:
                logger.warning(f"Ollama error {response.status_code}")

        except Exception as e:
            logger.warning(f"Ollama failed: {e}")

        # =====================================================
        # 2. GROQ FALLBACK (FIXED)
        # =====================================================
        if self.groq_api_key:
            try:
                logger.info(f"Using Groq fallback ({self.groq_model})...")

                headers = {
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.0
                }

                response = requests.post(

                    # FIX 4: correct Groq endpoint
                    "https://api.groq.com/openai/v1/chat/completions",

                    headers=headers,
                    json=payload,

                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()

                    latency_ms = int((time.time() - start_time) * 1000)
                    logger.info(f"Groq success in {latency_ms}ms")

                    return answer, "groq_fallback", latency_ms

                else:
                    logger.error(f"Groq error {response.status_code}: {response.text}")

            except Exception as e:
                logger.error(f"Groq failed: {e}")

        # =====================================================
        # 3. FINAL FAILURE
        # =====================================================
        latency_ms = int((time.time() - start_time) * 1000)

        return (
            "Error: Both Ollama and Groq failed. Please ensure Ollama is running or check API key.",
            "error",
            latency_ms
        )