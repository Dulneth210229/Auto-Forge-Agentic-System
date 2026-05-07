import json


def build_coder_prompt(context: dict) -> str:
    """
    Build a strict prompt for the Coder Agent using the SRS data.
    """

    srs_json = json.dumps(context.get("srs_data", {}), indent=2)
    project_name = context.get("project_name", "E-Commerce App")

    return f"""You are the AutoForge Coder Agent.

Generate a runnable E-commerce prototype for: {project_name}

You MUST follow the exact file paths below.
Do NOT invent different folders like app/, src/, server/, client/, or root-level index.html.

CRITICAL: Output ONLY the file blocks. Do NOT add any text before, after, or between file blocks.
CRITICAL: Use EXACTLY this format for EVERY file. No exceptions.

Required output format:

<file path="backend/main.py">
FULL FASTAPI BACKEND CODE HERE
</file>

<file path="backend/requirements.txt">
fastapi
uvicorn
pydantic
</file>

<file path="backend/Dockerfile">
FULL DOCKERFILE HERE
</file>

<file path="backend/data/store.json">
FULL JSON DATA STORE HERE
</file>

<file path="frontend/index.html">
FULL HTML CODE HERE
</file>

<file path="frontend/styles.css">
FULL CSS CODE HERE
</file>

<file path="docker-compose.yml">
FULL DOCKER COMPOSE CODE HERE
</file>

<file path=".gitignore">
FULL GITIGNORE CONTENT HERE
</file>

<file path="README.md">
FULL README CONTENT HERE
</file>

Rules:
- Output ONLY file blocks.
- Do not write explanations before the file blocks.
- Do not write explanations after the file blocks.
- Do not use markdown headings.
- Do not use ``` code fences.
- Do not use [file path="..."] format.
- Use only <file path="..."> and </file>.
- Backend must use FastAPI.
- Backend must run on port 9000.
- Backend must include CORS middleware.
- Backend must use Pydantic models.
- Backend must include these endpoints:
  - GET /health
  - GET /products
  - GET /products/{{product_id}}
  - POST /cart/items
  - GET /cart
  - DELETE /cart
  - POST /checkout
  - GET /orders
- Frontend must use plain HTML, CSS, and JavaScript.
- Frontend must call http://127.0.0.1:9000.
- Use backend/data/store.json for the MVP data store.
- Do not include component list diagrams.
- Do not leave pass statements.
- Do not write incomplete placeholder code.
- Do not write comments like "... add more products ...".
- Do not write "Implement logic here".
- All generated Python code must be runnable.

Internal responsibilities:
1. Development Agent:
   - Generate backend API logic.
   - Generate frontend HTML/CSS/JS.
   - Implement catalog, cart, checkout, and orders.

2. Database Agent:
   - Generate Product, CartItem, and Order data structures.
   - Generate backend/data/store.json.
   - Use JSON file storage for MVP.

3. DevOps Agent:
   - Generate backend/Dockerfile.
   - Generate docker-compose.yml.
   - Generate README.md.
   - Generate .gitignore.

Approved SRS:
{srs_json}
"""

