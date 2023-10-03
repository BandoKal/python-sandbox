# Import the modules
import random
import markdown

# Read the markdown file as input
with open("questions.md", "r") as f:
    md_text = f.read()

# Convert the markdown text to HTML
html_text = markdown.markdown(md_text)

# Parse the HTML text and extract the second level list items
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_text, "html.parser")
questions = []
for li in soup.find_all("li"):
    if li.parent.name == "ol" and li.parent.parent.name == "li":
        questions.append(li.text)

# Create an array of questions from the list items
questions = list(set(questions)) # remove duplicates

# Output a random question every time the user hits the enter button in terminal
while True:
    input("Press enter to get a random question: ")
    print(random.choice(questions))
