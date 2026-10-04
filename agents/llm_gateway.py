# agents/llm_gateway.py

import os
import time
import threading
from dotenv import load_dotenv
from groq import Groq, RateLimitError


class LLMGateway:
    """
    Shared LLM access layer for the whole project.
    This centralizes API connection, retries, spacing, and concurrency.
    """

    def __init__(
        self,
        model=None,
        max_retries=3,
        min_interval_seconds=1.0,
        max_parallel_calls=2
    ):
        load_dotenv()

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.model = model or os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile"
        )

        self.max_retries = max_retries
        self.min_interval_seconds = min_interval_seconds
        self.max_parallel_calls = max_parallel_calls

        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._active_calls = 0
        self._last_request_at = 0.0

    def _acquire_slot(self):
        with self._cond:
            while self._active_calls >= self.max_parallel_calls:
                self._cond.wait()
            self._active_calls += 1

    def _release_slot(self):
        with self._cond:
            self._active_calls -= 1
            self._cond.notify()

    def _respect_rate_limit(self):
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_at
            if elapsed < self.min_interval_seconds:
                sleep_for = self.min_interval_seconds - elapsed
            else:
                sleep_for = 0
            self._last_request_at = now + sleep_for

        if sleep_for > 0:
            time.sleep(sleep_for)

    def generate(
        self,
        system_prompt,
        user_prompt,
        fallback_value=None,
        **kwargs
    ):
        last_error = None

        for attempt in range(self.max_retries):
            try:
                self._acquire_slot()
                try:
                    self._respect_rate_limit()

                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": user_prompt
                            }
                        ],
                        **kwargs
                    )

                    return response.choices[0].message.content

                finally:
                    self._release_slot()

            except RateLimitError as e:
                last_error = e
                wait = min(2 ** attempt, 10)
                print(f"⚠️ Rate limit hit. Retrying in {wait}s...")
                time.sleep(wait)

            except Exception as e:
                last_error = e
                if attempt == self.max_retries - 1:
                    break
                time.sleep(2 ** attempt)

        if fallback_value is not None:
            print("⚠️ Falling back to non-LLM value because LLM requests failed.")
            return fallback_value

        raise Exception(f"LLM request failed after {self.max_retries} retries") from last_error

    def generate_with_fallback(self, system_prompt, user_prompt, fallback_value=None, **kwargs):
        return self.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_value=fallback_value,
            **kwargs
        )