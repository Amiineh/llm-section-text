# This file contains classes or functions needed to section the input file into N cards
import re
from typing import Optional
from difflib import SequenceMatcher
import logging
logger = logging.getLogger(__name__)
from llm import SectionerAgent

class Cardify:
    def __init__(self, llmAgent=None):
        if llmAgent is None:
            self.sectionerAgent = SectionerAgent()
        else:
            self.sectionerAgent = llmAgent
        self.num_retries = 3
        self.current_attempt = 0
        self.fuzzy_threshold = 0.8

    def _estimate_sections(self, document: str) -> int:
        """ count paragraphs and headings to estimate natural num slides """
        num_paragraphs = document.count("\n\n")
        num_headings = len(re.findall(r'\n#{1,6}\s+', document))
        return max(1, num_headings, num_paragraphs)

    def _fuzzy_find(self, document: str, substring: str) -> tuple[int, str]:
        """
            find substring match with fuzzy threshold in document, use a sliding window approach
            Returns: (position, matched_text) or (-1, "") if not found
        """
        best_ratio = 0
        best_pos = -1
        best_match = ""

        for i in range(len(document) - len(substring) + 1):
            window = document[i:i+len(substring)]
            ratio = SequenceMatcher(None, substring, window).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_pos = i
                best_match = window

        return best_pos, best_match


    def _attempt_sectioning(self, document: str, target_slides: int) -> Optional[list[str]]:
        endings = self.sectionerAgent.get_llm_response(document, target_slides)
        if not isinstance(endings, list):
            logger.info("Response format is not a list, retrying...")
            return None

        sections = []
        pointer = 0
        for i, ending in enumerate(endings):
            search_space = document[pointer:]
            last_chars = search_space.find(ending)

            if last_chars == -1:
                # if exact match not found -> rough match using fuzzy find
                fuzzy_pos, fuzzy_text = self._fuzzy_find(search_space, ending)
                if fuzzy_pos == -1:
                    logger.warning(f"Couldn't find substring {ending} in the document")
                    return sections # return what you have so far

                logger.info(f"Used fuzzy match for section {i+1}: '{fuzzy_text}' instead of '{ending}'")
                last_chars = fuzzy_pos
                ending = fuzzy_text

            split_pos = pointer + last_chars + len(ending)
            if pointer >= split_pos:
                logger.error(f"new split position {split_pos} is not after the previous one {pointer}")
                break
            if i == target_slides-1:
                sections.append(document[pointer:]) # get the rest of the document to include whitespaces
            else:
                sections.append(document[pointer: split_pos])
            pointer = split_pos

        return sections

    def section_document(self, document: str, target_slides: int=10) -> list[str]:
        """
            Split document into exactly target_slides sections.

            Args:
                document: The markdown document to split
                target_slides: Number of sections to create (1-50)

            Returns:
                List of document sections that reconstruct the original

            Raises:
                ValueError: If document or target_slides is invalid
        """
        # edge cases: empty file, invalid target_slides, single slide
        if not document or not document.strip():
            raise ValueError("Document is empty or only contains whitespace")
        if target_slides < 1 or target_slides > 50:
            raise ValueError("Invalid number of target_slides, must be between 1 and 50")
        if target_slides == 1:
            return [document]

        # log warning if number of sections is too high
        estimate_sections = self._estimate_sections(document)
        if target_slides > estimate_sections:
            logger.warning(f"Target slides {target_slides} exceeds natural limit {estimate_sections}")

        backup_sections = [document] + [''] * (target_slides-1)
        while self.current_attempt < self.num_retries:
            logger.info(f"Attempt {self.current_attempt+1}/{self.num_retries}")
            try:
                sections = self._attempt_sectioning(document, target_slides)
                if sections:
                    # check num sections is correct, if not, use sectioning as backup and try again
                    if len(sections) != target_slides:
                        logger.warning(f"Could not create {target_slides} section, created {len(sections)}")
                        backup_sections = sections
                        self.current_attempt += 1
                        continue

                    # check reconstruction, warn but don't halt
                    reconstructed = ''.join(sections)
                    if reconstructed != document:
                        logger.warning(f"Reconstruction failed: reconstructed length: {len(reconstructed)}, original length: {len(document)}")

                    self.current_attempt = 0 # reset for next call
                    return sections
            except Exception as e:
                logger.error(f"Attempt failed with error {e}")
            self.current_attempt += 1
        self.current_attempt = 0  # reset for next call
        logger.error(f"failed to find a valid split after {self.num_retries} attempts, returning backup sectioning")
        return backup_sections

