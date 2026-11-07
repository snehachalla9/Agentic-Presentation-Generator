# agents/llm_gateway.py

import os
import time
import threading
from dotenv import load_dotenv
from groq import Groq, RateLimitError
# USD per 1 million tokens.
# Keep these configurable because provider pricing can change.
MODEL_PRICING = {
    "openai/gpt-oss-120b": {
        "input": 0.15,
        "output": 0.60,
    },
    "openai/gpt-oss-20b": {
        "input": 0.075,
        "output": 0.30,
    },
}


class LLMGateway:
    """
    Shared LLM access layer for the whole project.
    This centralizes API connection, retries, spacing, and concurrency.
    """
    def _empty_metrics(self):
        return {
            "model": self.model,
            "request_count": 0,
            "failed_request_count": 0,
            "rate_limit_count": 0,
            "retry_count": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "llm_latency_seconds": 0.0,
            "estimated_cost_usd": 0.0,
    }

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
            "openai/gpt-oss-120b"
        )

        self.max_retries = max_retries
        self.min_interval_seconds = min_interval_seconds
        self.max_parallel_calls = max_parallel_calls

        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._active_calls = 0
        self._last_request_at = 0.0
        self._metrics_lock = threading.Lock()
        self._metrics = self._empty_metrics()
        # self._metrics = {
        #     "request_count": 0,
        #     "input_tokens": 0,
        #     "output_tokens": 0,
        #     "total_tokens": 0,
        #     "llm_latency_seconds": 0.0,
        # }

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
    def reset_metrics(self):
        with self._metrics_lock:
            self._metrics = self._empty_metrics()
    # def reset_metrics(self):
    #     with self._metrics_lock:
    #         self._metrics = {
    #             "request_count": 0,
    #             "input_tokens": 0,
    #             "output_tokens": 0,
    #             "total_tokens": 0,
    #             "llm_latency_seconds": 0.0,
    #         }

    def get_metrics(self):
        with self._metrics_lock:
            return self._metrics.copy()

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
                    llm_started = time.perf_counter()

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

                    llm_elapsed = time.perf_counter() - llm_started
                    usage = response.usage
                    if usage:
                        input_tokens = usage.prompt_tokens or 0
                        output_tokens = usage.completion_tokens or 0
                        total_tokens = usage.total_tokens or 0
                        pricing = MODEL_PRICING.get(self.model, {})
                        input_rate = pricing.get("input")
                        output_rate = pricing.get("output")
                        estimated_cost = 0.0
                        if input_rate is not None and output_rate is not None:
                             estimated_cost = (
                                  input_tokens * input_rate / 1_000_000
                                  + output_tokens * output_rate / 1_000_000)

                    with self._metrics_lock:
                         self._metrics["request_count"] += 1
                         self._metrics["input_tokens"] += input_tokens
                         self._metrics["output_tokens"] += output_tokens
                         self._metrics["total_tokens"] += total_tokens
                         self._metrics["llm_latency_seconds"] += llm_elapsed
                         self._metrics["estimated_cost_usd"] += estimated_cost
                    return response.choices[0].message.content


                finally:
                    self._release_slot()
            except RateLimitError as e:
                last_error = e
                with self._metrics_lock:
                    self._metrics["rate_limit_count"] += 1
                    self._metrics["retry_count"] += 1
                    wait = min(2 ** attempt, 10)
                    print(f"Rate limit hit. Retrying in {wait}s...")
                    time.sleep(wait)
            except Exception as e:
                last_error = e
                with self._metrics_lock:
                    if attempt < self.max_retries - 1:
                        self._metrics["retry_count"] += 1
                if attempt == self.max_retries - 1:
                    break
                time.sleep(2 ** attempt)
        with self._metrics_lock:
            self._metrics["failed_request_count"] += 1

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