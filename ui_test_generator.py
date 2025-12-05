import os
import re
import json

# Paths
DJANGO_APP_PATH = './main_app'  # replace with your app path
OUTPUT_CYPRESS_PATH = './cypress/e2e/generated_tests'

if not os.path.exists(OUTPUT_CYPRESS_PATH):
    os.makedirs(OUTPUT_CYPRESS_PATH)

# Regex patterns
view_pattern = re.compile(r'def (\w+)\(request[^\)]*\):')
template_pattern = re.compile(r'render\(request,\s*[\'"]([\w/_\-]+\.html)[\'"]')
form_pattern = re.compile(r'(\w+) = (\w+)\(request\.POST or None')

def parse_views(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    views = []
    for view_match in view_pattern.finditer(content):
        view_name = view_match.group(1)
        view_start = view_match.end()
        view_body = content[view_start:]
        template_match = template_pattern.search(view_body)
        form_matches = form_pattern.findall(view_body)

        template_name = template_match.group(1) if template_match else None
        forms = [f[1] for f in form_matches]

        views.append({
            'view_name': view_name,
            'template': template_name,
            'forms': forms
        })
    return views

# Generate Cypress test
def generate_cypress_test(view):
    view_name = view['view_name']
    template = view['template']
    forms = view['forms']

    test_code = f"describe('{view_name}', () => {{\n"
    test_code += f"  it('Visits the page', () => {{\n"
    test_code += f"    cy.visit('/{view_name}/')\n"
    test_code += f"    cy.contains('{view_name.replace('_',' ').title()}')\n"
    test_code += "  });\n\n"

    for form in forms:
        test_code += f"  it('Fills the {form} form', () => {{\n"
        test_code += f"    cy.visit('/{view_name}/')\n"
        # We cannot parse exact form fields, so placeholder:
        test_code += "    // TODO: Fill the form fields\n"
        test_code += "    cy.get('form').submit()\n"
        test_code += "  });\n\n"

    test_code += "});\n"
    return test_code

# Walk through app folder and parse views
for root, dirs, files in os.walk(DJANGO_APP_PATH):
    for file in files:
        if file.endswith('.py') and 'views' in file:
            file_path = os.path.join(root, file)
            views = parse_views(file_path)
            for view in views:
                test_code = generate_cypress_test(view)
                output_file = os.path.join(OUTPUT_CYPRESS_PATH, f"{view['view_name']}.spec.js")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(test_code)
                print(f"Generated test for {view['view_name']} -> {output_file}")

print("Cypress test generation completed!")
