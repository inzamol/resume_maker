import os
import json
import httpx
from typing import Optional, Dict, Any

class LLMClient:
    def __init__(
        self,
        provider: str = "gemini",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.provider = provider.lower()
        self.api_key = api_key or self._get_default_api_key(self.provider)
        self.model = model or self._get_default_model(self.provider)
        self.base_url = base_url or self._get_default_base_url(self.provider)

    def _get_default_api_key(self, provider: str) -> Optional[str]:
        if provider == "gemini":
            return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        elif provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        return None

    def _get_default_model(self, provider: str) -> str:
        if provider == "gemini":
            return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        elif provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif provider == "anthropic":
            return os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        elif provider == "ollama":
            return os.getenv("OLLAMA_MODEL", "llama3.2")
        return "default"

    def _get_default_base_url(self, provider: str) -> Optional[str]:
        if provider == "ollama":
            return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return None

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call the configured LLM provider and return response text."""
        async with httpx.AsyncClient(timeout=90.0) as client:
            if self.provider == "gemini":
                return await self._call_gemini(client, prompt, system_prompt)
            elif self.provider == "openai":
                return await self._call_openai(client, prompt, system_prompt)
            elif self.provider == "anthropic":
                return await self._call_anthropic(client, prompt, system_prompt)
            elif self.provider == "ollama":
                return await self._call_ollama(client, prompt, system_prompt)
            elif self.provider == "custom":
                return await self._call_custom_openai(client, prompt, system_prompt)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def _call_gemini(self, client: httpx.AsyncClient, prompt: str, system_prompt: Optional[str]) -> str:
        if not self.api_key:
            raise ValueError("Gemini API key is required. Please set it in Settings or GEMINI_API_KEY environment variable.")
        
        # Use Gemini 2.5 Flash / 1.5 Flash API endpoint
        model_name = self.model or "gemini-2.5-flash"
        # If user passed "gemini-1.5-flash" or other models
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.95
            }
        }
        
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            err_msg = response.text
            try:
                err_json = response.json()
                err_msg = err_json.get("error", {}).get("message", response.text)
            except Exception:
                pass
            raise RuntimeError(f"Gemini API error ({response.status_code}): {err_msg}")

        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected response structure from Gemini: {data}")

    async def _call_openai(self, client: httpx.AsyncClient, prompt: str, system_prompt: Optional[str]) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please set it in Settings or OPENAI_API_KEY environment variable.")
            
        url = "https://api.openai.com/v1/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model or "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.2
        }
        
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            err_msg = response.text
            try:
                err_json = response.json()
                err_msg = err_json.get("error", {}).get("message", response.text)
            except Exception:
                pass
            raise RuntimeError(f"OpenAI API error ({response.status_code}): {err_msg}")
            
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_anthropic(self, client: httpx.AsyncClient, prompt: str, system_prompt: Optional[str]) -> str:
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Please set it in Settings or ANTHROPIC_API_KEY environment variable.")
            
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": self.model or "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Anthropic API error ({response.status_code}): {response.text}")
            
        data = response.json()
        return data["content"][0]["text"]

    async def _call_ollama(self, client: httpx.AsyncClient, prompt: str, system_prompt: Optional[str]) -> str:
        base = self.base_url or "http://localhost:11434"
        url = f"{base.rstrip('/')}/api/generate"
        
        payload = {
            "model": self.model or "llama3.2",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = await client.post(url, json=payload)
        except httpx.ConnectError:
            raise RuntimeError(f"Could not connect to Ollama at {base}. Is the Ollama server running locally?")
            
        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error ({response.status_code}): {response.text}")
            
        data = response.json()
        return data.get("response", "")

    async def _call_custom_openai(self, client: httpx.AsyncClient, prompt: str, system_prompt: Optional[str]) -> str:
        if not self.base_url:
            raise ValueError("Custom OpenAI-compatible provider requires a Base URL.")
            
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }
        
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Custom LLM API error ({response.status_code}): {response.text}")
            
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def test_connection(self) -> Dict[str, Any]:
        """Send a quick hello test prompt to check authentication and responsiveness."""
        try:
            res = await self.generate("Reply with exactly: 'OK'", system_prompt="You are a connection test.")
            return {"success": True, "message": f"Connected successfully to {self.provider} ({self.model}). Response: {res.strip()[:30]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

