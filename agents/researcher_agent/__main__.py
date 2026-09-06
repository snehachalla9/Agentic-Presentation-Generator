#!/usr/bin/env python3
"""
Entry point for Researcher Agent when run as a module
"""

from .researcher import research_from_file

if __name__ == "__main__":
    print("🔬 Researcher Agent")
    print("=" * 50)
    
    # Research from the default planner file
    result = research_from_file()
    
    if result:
        categories = len(result.get("research_output", {}))
        print(f"\n✅ Research complete! {categories} categories researched.")
    else:
        print("\n❌ Research failed. Check if planner file exists.")