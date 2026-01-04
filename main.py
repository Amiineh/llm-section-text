import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
from cardify import Cardify

with open("sample.txt", 'r') as f:
    document = f.read()
    print(f"Successfully opened text document: {document[:30]}...")

    presentation_maker = Cardify()
    target_slides = int(input("Enter the number for target slides (N): "))
    sections = presentation_maker.section_document(document, target_slides)
    for i in range(target_slides):
        print(f"\n--- Section {i+1} ---")
        print(sections[i])

