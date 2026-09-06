# compressor.py

class ContentCompressor:
    def compress(self, content: dict, slide_blueprint: dict) -> dict:
        plan = slide_blueprint["slide"]["presentation_plan"]
        word_limit = plan.get("word_limit", 120)
        bullet_limit = plan.get("bullet_limit", 5)
        cognitive_load = plan.get("cognitive_load", "medium")
        slide_type = plan.get("template", "content")
        # slide_type = plan.get("presentation_intent", {}).get("layout", "content")

        compressed = content.copy()

        # Calculate total words across slide
        total_words = 0
        for key, val in compressed.items():
            if isinstance(val, str):
                total_words += len(val.split())
            elif isinstance(val, list):
                total_words += sum(len(v.split()) for v in val if isinstance(v, str))

        # Priority map: what to keep/remove first
        priority = [
            "headline",
            "key_takeaway",
            "main_message",
            "bullets",
            "examples",
            "statistics",
            "case_studies",
            "references"
        ]

        # Slide-type awareness
        if slide_type == "chart":
            # Never remove statistics
            priority.remove("statistics")
            priority.insert(3, "statistics")
        elif slide_type == "workflow":
            # Never remove bullets (steps)
            priority.remove("bullets")
            priority.insert(3, "bullets")

        # Compression logic
        compression_report = {
            "original_words": total_words,
            "compressed_words": total_words,
            "compression_ratio": 1.0,
            "removed_bullets": 0,
            "removed_examples": 0,
            "removed_statistics": 0,
            "removed_references": 0
        }

        # If over word limit, trim lower-priority items first
        while compression_report["compressed_words"] > word_limit:
            for field in reversed(priority):  # start from lowest priority
                if field in compressed and compressed[field]:
                    if isinstance(compressed[field], list) and len(compressed[field]) > 0:
                        compressed[field] = compressed[field][:-1]
                        key = f"removed_{field}"
                        compression_report[key] = compression_report.get(key, 0) + 1
                        # compression_report[f"removed_{field}"] += 1
                    elif isinstance(compressed[field], str):
                        compressed[field] = " ".join(compressed[field].split()[:-5])
                    break
            # Recalculate word count
            total_words = 0
            for key, val in compressed.items():
                if isinstance(val, str):
                    total_words += len(val.split())
                elif isinstance(val, list):
                    total_words += sum(len(v.split()) for v in val if isinstance(v, str))
            compression_report["compressed_words"] = total_words
            compression_report["compression_ratio"] = round(
                compression_report["compressed_words"] / compression_report["original_words"], 2
            )

        # Enforce bullet limits
        bullets = compressed.get("bullets", [])
        if len(bullets) > bullet_limit:
            compressed["bullets"] = bullets[:bullet_limit]
            compression_report["removed_bullets"] += len(bullets) - bullet_limit

        # Cognitive load adjustments
        if cognitive_load == "low":
            compressed["bullets"] = compressed["bullets"][:3]
            compressed["examples"] = compressed.get("examples", [])[:1]
            compressed["statistics"] = compressed.get("statistics", [])[:1]
        elif cognitive_load == "high":
            # allow more detail
            compressed["bullets"] = compressed["bullets"][:bullet_limit+2]

        compressed["compression_report"] = compression_report
        return compressed
