# compressor.py

class ContentCompressor:
    # Fields that appear on the slide and count toward the word limit
    COUNTED = [
        "headline", "subtitle", "main_message", "bullets", "callout",
        "key_takeaway", "supporting_evidence", "examples", "statistics",
        "case_studies", "references",
    ]

    # Trim order: least important first. headline is never trimmed.
    TRIM_ORDER = [
        "references", "case_studies", "statistics", "examples",
        "supporting_evidence", "callout", "subtitle",
        "bullets", "main_message", "key_takeaway",
    ]

    MIN_BULLETS = 2
    MIN_STRING_WORDS = 8

    def _count_words(self, content: dict) -> int:
        total = 0
        for key in self.COUNTED:
            val = content.get(key)
            if isinstance(val, str):
                total += len(val.split())
            elif isinstance(val, list):
                total += sum(len(v.split()) for v in val if isinstance(v, str))
        return total

    def _trim_one(self, content: dict, field: str, report: dict) -> bool:
        """Trim one step from a field. Returns True if something was removed."""
        val = content.get(field)
        if isinstance(val, list):
            floor = self.MIN_BULLETS if field == "bullets" else 0
            if len(val) > floor:
                content[field] = val[:-1]
                key = f"removed_{field}"
                report[key] = report.get(key, 0) + 1
                return True
            elif isinstance(val, str):
                if field in ("callout", "supporting_evidence", "subtitle"):
                    if val:
                        content[field] = ""
                        return True
            else:
                words = val.split()
                if len(words) > self.MIN_STRING_WORDS:
                    content[field] = " ".join(words[:-5])
                    return True

    def compress(self, content: dict, slide_blueprint: dict) -> dict:
        plan = slide_blueprint["slide"]["presentation_plan"]
        word_limit = plan.get("word_limit", 120)
        bullet_limit = plan.get("bullet_limit", 5)
        cognitive_load = plan.get("cognitive_load", "medium")
        slide_type = plan.get("template", "content")

        compressed = content.copy()
        original_words = self._count_words(compressed)

        report = {
            "original_words": original_words,
            "compressed_words": original_words,
            "compression_ratio": 1.0,
            "removed_bullets": 0,
            "removed_examples": 0,
            "removed_statistics": 0,
            "removed_references": 0,
        }

        trim_order = list(self.TRIM_ORDER)
        if slide_type == "chart" and "statistics" in trim_order:
            trim_order.remove("statistics")
            trim_order.insert(len(trim_order) - 2, "statistics")
        elif slide_type in ("workflow", "process") and "bullets" in trim_order:
            trim_order.remove("bullets")
            trim_order.insert(len(trim_order) - 2, "bullets")

        # Bounded loop: always ends, even if nothing more can be trimmed
        for _ in range(200):
            words = self._count_words(compressed)
            if words <= word_limit:
                break
            if not any(self._trim_one(compressed, f, report) for f in trim_order):
                break  # nothing left that is safe to trim

        # Enforce bullet limit
        bullets = compressed.get("bullets") or []
        if len(bullets) > bullet_limit:
            compressed["bullets"] = bullets[:bullet_limit]
            report["removed_bullets"] += len(bullets) - bullet_limit

        # Cognitive load adjustments (safe if fields are missing)
        if cognitive_load == "low":
            compressed["bullets"] = (compressed.get("bullets") or [])[:3]
            compressed["examples"] = (compressed.get("examples") or [])[:1]
            compressed["statistics"] = (compressed.get("statistics") or [])[:1]
        elif cognitive_load == "high":
            compressed["bullets"] = (compressed.get("bullets") or [])[:bullet_limit + 2]

        final_words = self._count_words(compressed)
        report["compressed_words"] = final_words
        report["compression_ratio"] = (
            round(final_words / original_words, 2) if original_words else 1.0
        )

        compressed["compression_report"] = report
        return compressed