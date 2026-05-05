"""
wireframe_builder.py

This file is intentionally kept minimal.

AutoForge UI/UX Agent now generates wireframes through the LLM only.
No hardcoded UI screens.
No dynamic templates.
No fallback HTML layouts.

The actual wireframe generation happens in:
- prompt.py
- agent.py
- parser.py
"""


def no_template_wireframes_enabled() -> bool:
    """
    Helper used only for documentation/testing.
    """
    return True