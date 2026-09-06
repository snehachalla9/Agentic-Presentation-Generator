# quality_scorer.py

class PipelineQualityScorer:
    def score(self, pipeline_report: dict) -> dict:
        slide_type = pipeline_report.get("slide_type","content")

        # Adaptive weights by slide type
        weights = self._weights_for_slide(slide_type)

        # Collect stage scores
        planner = pipeline_report.get("planner_score", 95)
        research = pipeline_report.get("research_score", 90)
        presentation = pipeline_report.get("presentation_score", 92)
        content = pipeline_report.get("content_score", 91)
        visual = pipeline_report.get("visual_score", 93)
        speaker = pipeline_report.get("speaker_score", 90)
        renderer = pipeline_report.get("renderer_score", 94)
        accessibility = pipeline_report.get("accessibility_score", 88)

        # Weighted overall
        overall = (
            planner*weights["planner"] +
            research*weights["research"] +
            presentation*weights["presentation"] +
            content*weights["content"] +
            visual*weights["visual"] +
            speaker*weights["speaker"] +
            renderer*weights["renderer"] +
            accessibility*weights["accessibility"]
        )

        grade = self._grade(overall)
        render_ready = overall >= 85
        publish_ready = overall >= 90

        # Recommendations
        recommendations = self._recommendations(pipeline_report)

        return {
            "overall": {
                "score": round(overall,1),
                "grade": grade,
                "confidence": "High" if overall>=90 else "Medium" if overall>=75 else "Low",
                "render_ready": render_ready,
                "publish_ready": publish_ready
            },
            "scores": {
                "planner": planner,
                "research": research,
                "presentation": presentation,
                "content": content,
                "visual": visual,
                "speaker": speaker,
                "renderer": renderer,
                "accessibility": accessibility
            },
            "recommendations": recommendations,
            "quality_gates": {
                "pass": overall>=80,
                "critical_issues": len([i for i in recommendations if i["priority"]=="High"]),
                "warnings": len([i for i in recommendations if i["priority"]=="Medium"])
            }
        }

    def _weights_for_slide(self, slide_type):
        if slide_type=="chart":
            return {"planner":0.05,"research":0.2,"presentation":0.1,"content":0.2,"visual":0.25,"speaker":0.1,"renderer":0.05,"accessibility":0.05}
        if slide_type=="definition":
            return {"planner":0.05,"research":0.25,"presentation":0.1,"content":0.3,"visual":0.1,"speaker":0.1,"renderer":0.05,"accessibility":0.05}
        return {"planner":0.1,"research":0.15,"presentation":0.1,"content":0.2,"visual":0.2,"speaker":0.1,"renderer":0.1,"accessibility":0.05}

    def _grade(self, score):
        if score>=95: return "A+"
        if score>=90: return "A"
        if score>=85: return "B+"
        if score>=80: return "B"
        if score>=70: return "C"
        return "D"

    def _recommendations(self, pipeline_report):
        recs = []
        if pipeline_report.get("research_coverage",100)<50:
            recs.append({"priority":"High","module":"Content Synthesizer","issue":"Low research coverage","repair":"Include two additional key facts."})
        if pipeline_report.get("semantic_preservation",100)<70:
            recs.append({"priority":"High","module":"Synthesizer","issue":"Semantic loss","repair":"Preserve missing concepts in summary."})
        if pipeline_report.get("speaker_notes_complete",True)==False:
            recs.append({"priority":"Medium","module":"Speaker Notes","issue":"Incomplete notes","repair":"Add transition and audience question."})
        if pipeline_report.get("visual_ready",True)==False:
            recs.append({"priority":"Medium","module":"Visual Builder","issue":"Visual incomplete","repair":"Add missing metrics or steps."})
        return recs
