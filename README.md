# Document splitter for slide presentation
This python project takes a Markdown file and number N (between 1 and 50) and uses an LLM agent to section the document into N parts for a slide presentation.

## Design
The LLM is instructed to find the ending part of each section (as opposed to index position of split sections which can be hallucinated and inaccurate).
The LLM takes the input document and N and returns a JSON object including 'endings' array containing N substrings. Structured output is used to ensure llm responds in the correct format.

For each substring, we search the document from the last section's ending: if an exact match is found, a new section is added to results, otherwise we look for a fuzzy match.
SequenceMatcher with a threshold of 80% is used to find the alternative match (in case llm made a mistake). Then the search space is adjusted to the rest of the documents (excluding the sections already found) for efficiency.

A backup sectioning including the document in first section, and empty sections following is constructed in the beginning. If the sectioning fails, e.g. there are less than N sections, or the sections don't reconstruct the original document, we store that sectioning as backup and try again.
The sectioning is attempted a maximum of three times, and if no ideal sectioning is found, we return the backup to give user something to work with.

### Project files:
* `cardify.py`: Main splitting logic with exact and fuzzy text-matching (includes retries)
* `llm.py`: LLM client wrapper (Claude Sonnet 4.5 with structured output)
* `main.py`: CLI interface
* `test_cardify.py`: Unit tests (mock LLM)
* `test_integration.py`: Integration tests (real LLM)

## Features
* **Content Preservation**: the output sections match the original document when concatenated back together
* **Retry Mechanism**: if the sectioning encounters a problem, we call llm again (with a cap number of tries)
* **Backup sectioning**: if the sectioning fails, we return the full document in the first section and empty sections for the next N-1 ones (as observed in Gamma's product implementation)
* **Fuzzy text match**: we ask llm to give us ending snippets for each section, but the fallback is a fuzzy search in case llm doesn't return the exact match.
* **Edge case handling**: for empty files, too many sectioning, repetitive files, etc.
* **Tests**: unit tests (without llm call) and integration test (with llm) to ensure reliability

## Usage
### Installation
```commandline
# clone repo
git clone git@github.com:Amiineh/llm-section-text.git
cd llm-section-text

# install dependencies
pip install -r requirements.txt

# add your ANTHROPIC_API_KEY to .env
cp .env.example .env
```

To run on your input, you can paste it in `sample.txt`. Then run main.py: 
```commandline
python main.py
```
 you'll be prompted to enter N. The result is printed in N sections.

## Test Cases
Unit tests mock LLM and check for edge case handling in the code: empty files, N out of range, exact and fuzzy substring matches, and repetitions in the document or ending predictions.

Integration tests run on the files in `test_files` and call llm on different files and target_slides (N) to make sure the section numbers match N and reconstruct the original document.
Tests include: special characters <$#?.., unicodes (emojis and more), empty files, long files, files with repetition and nested headings.

## Known Limitations
* Very large input files might exceed llm token limit. Currently a warning is shown but it could be improved by chunking it and feeding multiple sections with Ni where Sum Ni = N
* If N is significantly large for a smaller document, the sections might not look natural. For example, bullet points are separated into multiple slides. At the moment, I count number of paragraphs and headings to suggest N and log a warning if N exceeds this suggestion.
* If the document is ambiguous, e.g. has many repetitions with slight changes, the llm might get confused or the fuzzy match might not improve sectioning.
* The result, as is with LLMs, is not deterministic, and multiple submissions might result in different sectionings.

## Future Directions
* Cache responses in case we get the same request (don't interfere with the retry mechanism)
* Improve prompt or add more LLMs