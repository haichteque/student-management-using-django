import os
import json
from google import genai

# --- Configuration ---
CODE_DIR = "main_app"   # no recursion
OUTPUT_DIR = "cypress/e2e"
BASE_URL = "http://127.0.0.1:8000/"

# Login credentials
CREDENTIALS = {
    "admin": {"email": "qasim@admin.com", "password": "admin"},
    "staff": {"email": "bill@ms.com", "password": "123"},
    "student": {"email": "qasim@nu.edu.pk", "password": "123"},
}

SYSTEM_PROMPT = f"""
You are an expert QA engineer. Generate **Cypress E2E test code** for the following Python/Django file.
Use the base URL: {BASE_URL}
Use the following login credentials:

- Admin: {CREDENTIALS['admin']['email']} / {CREDENTIALS['admin']['password']}
- Staff: {CREDENTIALS['staff']['email']} / {CREDENTIALS['staff']['password']}
- Student: {CREDENTIALS['student']['email']} / {CREDENTIALS['student']['password']}

The code must be ready to run in Cypress 12+, using proper `describe`/`it` blocks.
Automatically detect whether a test is for admin, staff, or student login.
Output must be only JS code, no extra comments or explanations.
"""

# --- Initialize Gemini client ---
try:
    client = genai.Client()
except Exception:
    print("!!! ERROR: GEMINI_API_KEY not set or client failed to initialize.")
    exit()

# --- Helper: Clean Gemini JS output by removing first and last line ---
def clean_cypress_code(code: str) -> str:
    lines = code.strip().splitlines()
    if len(lines) > 2:  # remove first and last line if present
        lines = lines[1:-1]
    return "\n".join(lines)

# --- Gemini call ---
def get_cypress_code_from_gemini(file_content: str, filename: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\n\n--- CODE START ---\n{file_content}\n--- CODE END ---"
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        js_code = response.text.strip()
        return clean_cypress_code(js_code)
    except Exception as e:
        print(f"[ERROR] Gemini failed for {filename}: {e}")
        return ""

# --- Generate Cypress tests ---
def generate_cypress_tests(code_directory, output_directory):
    if not os.path.exists(code_directory):
        print(f"!!! ERROR: Directory '{code_directory}' not found")
        return

    os.makedirs(output_directory, exist_ok=True)

    for file in os.listdir(code_directory):
        if file.endswith(".py"):
            filepath = os.path.join(code_directory, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"!!! Could not read {filepath}: {e}")
                continue

            js_code = get_cypress_code_from_gemini(content, file)
            if js_code:
                out_file = os.path.join(output_directory, f"{os.path.splitext(file)[0]}.cy.js")
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(js_code)
                print(f"✅ Saved Cypress test for {file} -> {out_file}")
            else:
                print(f"⚠️ No code generated for {file}")

if __name__ == "__main__":
    generate_cypress_tests(CODE_DIR, OUTPUT_DIR)
