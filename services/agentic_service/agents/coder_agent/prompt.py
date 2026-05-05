import json

def build_coder_prompt(context: dict) -> str:
    """
    Build a prompt for the Coder Agent using the SRS data.
    """
    srs_json = json.dumps(context.get("srs_data", {}), indent=2)
    project_name = context.get("project_name", "E-Commerce App")
    
    prompt = f"""You are an expert full-stack developer and software architect.
Your task is to generate a fully functional prototype for '{project_name}' based on the provided Software Requirements Specification (SRS).

Here is the SRS:
```json
{srs_json}
```

Please generate the codebase for this application.
Requirements:
1. Use FastAPI for the backend.
2. Use plain HTML, CSS, and JS for the frontend.
3. Provide a docker-compose.yml to run the app.
4. Provide a README.md and a .gitignore.
5. The backend must run on port 9000.
6. For the MVP, use a simple in-memory JSON data store (e.g. `data/store.json`).

Output your response ONLY as a JSON object where the keys are the file paths relative to the project root, and the values are the file contents as strings.
Example output format:
{{
  "backend/requirements.txt": "fastapi\\nuvicorn\\n",
  "backend/main.py": "from fastapi import FastAPI...",
  "frontend/index.html": "<!DOCTYPE html>..."
}}

DO NOT include any markdown formatting around the JSON (no ```json or ```). Return raw valid JSON only.
"""
    return prompt

