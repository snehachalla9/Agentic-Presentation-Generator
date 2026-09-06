
AUDIENCE_PROFILES = {
    "Executive": {
        "max_words": 60,
        "bullet_limit": 3,
        "technical_level": "low",
        "examples": "business",
        "tone": "strategic"
    },

    "Technical": {
        "max_words": 120,
        "bullet_limit": 5,
        "technical_level": "high",
        "examples": "implementation",
        "tone": "engineering"
    },

    "Student": {
        "max_words": 80,
        "bullet_limit": 4,
        "technical_level": "simple",
        "examples": "analogy",
        "tone": "educational"
    },

    "Research": {
        "max_words": 100,
        "bullet_limit": 5,
        "technical_level": "rigorous",
        "examples": "evidence",
        "tone": "academic"
    },

    "Business": {
        "max_words": 90,
        "bullet_limit": 4,
        "technical_level": "medium",
        "examples": "ROI",
        "tone": "practical"
    },

    # Planner audience
    "University Lecture": {
        "max_words": 100,
        "bullet_limit": 5,
        "technical_level": "medium",
        "examples": "academic",
        "tone": "educational"
    }
}


DEFAULT_PROFILE = {
    "max_words": 100,
    "bullet_limit": 5,
    "technical_level": "medium",
    "examples": "general",
    "tone": "educational"
}


class AudienceAdapter:

    def adapt(self, content: dict, slide_blueprint: dict) -> dict:

        # -----------------------------------
        # Debug
        # -----------------------------------
        print("\n========== AUDIENCE ADAPTER ==========")
        print("Blueprint Keys:", list(slide_blueprint.keys()))

        # -----------------------------------
        # Extract audience
        # -----------------------------------
        audience = slide_blueprint.get("audience", "Student")

        # Handle nested dictionary
        if isinstance(audience, dict):
            audience = audience.get("type", "Student")

        # Handle invalid values
        if not isinstance(audience, str):
            audience = "Student"

        print("Audience:", audience)

        # -----------------------------------
        # Get profile
        # -----------------------------------
        profile = AUDIENCE_PROFILES.get(audience, DEFAULT_PROFILE)

        print("Profile:", profile)
        print("======================================\n")

        # Store profile
        content["presentation_profile"] = profile

        # -----------------------------------
        # Word count
        # -----------------------------------
        word_count = 0

        for value in content.values():

            if isinstance(value, str):
                word_count += len(value.split())

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        word_count += len(item.split())

        if word_count > profile["max_words"]:

            content["validation_warning"] = (
                f"Word count ({word_count}) exceeds "
                f"{profile['max_words']} words "
                f"for {audience} audience."
            )

        # -----------------------------------
        # Bullet validation
        # -----------------------------------
        bullets = content.get("bullets", [])

        if isinstance(bullets, list):

            if len(bullets) > profile["bullet_limit"]:

                content["bullets"] = bullets[:profile["bullet_limit"]]

                content["validation_warning"] = (
                    f"Bullet count trimmed to "
                    f"{profile['bullet_limit']} bullets."
                )

        # -----------------------------------
        # Speaker notes
        # -----------------------------------
        notes = content.get("speaker_notes", "")

        if isinstance(notes, str):

            tone = profile.get("tone", "educational")

            content["speaker_notes"] = (
                notes +
                f"\n\nPresentation tone: {tone}."
            )

        return content