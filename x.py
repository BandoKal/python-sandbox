import re
import os
import requests
import base64
from unidecode import unidecode

# Function to fetch the ReadMe content from a public GitHub repository
def get_github_readme_content(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/readme"
    response = requests.get(url)
    response_json = response.json()

    # Decode the content from base64
    content = response_json['content']
    decoded_content = base64.b64decode(content).decode('utf-8')
    return decoded_content

markdown_content = get_github_readme_content('BandoKal', 'bando-apis')

sections = re.split(r'### ', markdown_content)[1:]  # Splits content into different sections starting with '### '

# Create a directory for the apis
output_directory = 'apis'
os.makedirs(output_directory, exist_ok=True)

generated_files = []

for section in sections:
    # Extract the system name from the markdown header
    header_match = re.match(r'(.+)', section)
    if not header_match:
        print("No header found in the section!")
        continue
    
    header_words = header_match.group(1).split()
    header_name = "-".join(word.lower() for word in header_words) + "-apis"
    system_name = f"system: {header_name}"

    table_lines = section.split("\n")[1:]
    for line in table_lines:
        match = re.match(r'\| \[(.+?)\]\((.+?)\) \| (.+?) \|', line)
        if match:
            api_name = unidecode(match.group(1).lower()).replace("/ ","").replace(" ", "-")
            if api_name.endswith("-"):
              api_name = api_name[:-1]
            api_title = match.group(1)
            api_link = match.group(2)
            description = match.group(3)
            
            yaml_content = f"""
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: {api_name}
  description: {description}
  annotations:
    {system_name}
spec:
  type: openapi
  lifecycle: production
  owner: unknown
  system: {header_name}
  definition: |
    openapi: 3.0.0
    info:
      title: {api_title}
      version: 1.0.0
      description: {description}
    externalDocs:
      url: {api_link}
"""
            filename = os.path.join(output_directory, api_name + '.yaml')
            with open(filename, 'w') as file:
                file.write(yaml_content)
            generated_files.append(filename)


def chunker(seq, size):
    """Split a sequence into chunks of the given size."""
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

# Format the list of targets for root_yaml_content
chunks = list(chunker(generated_files, 100))

for index, chunk in enumerate(chunks):
    formatted_targets = '\n    - '.join(['./' + f for f in chunk])
    root_yaml_content = f"""
apiVersion: backstage.io/v1alpha1
kind: Location
metadata:
  name: bando-apis-{index}
  description: A collection of all Public apis from https://github.com/public-apis/public-apis
spec:
  targets:
    - {formatted_targets}
"""
    with open(f'catalog-info-{index}.yaml', 'w') as root_file:
        root_file.write(root_yaml_content)


print("YAML files generated successfully!")
