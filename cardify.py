# This file contains classes or functions needed to section the input file into N cards
from llm import SectionerAgent
import logging
logger = logging.getLogger(__name__)

class Cardify:
    def __init__(self):
        self.sectionerAgent = SectionerAgent()
        self.num_retries = 1
        self.current_attempt = 0

    def section_document(self, document, target_slides=10):
        while self.current_attempt < self.num_retries:
            logger.info(f"attempt {self.current_attempt}/{self.num_retries}")
            endings = self.sectionerAgent.get_llm_response(document, target_slides)
            if not isinstance(endings, list):
                self.current_attempt += 1
                logger.info("Response format is not a json list, retrying...")
                continue
            if len(endings) != target_slides:
                self.current_attempt += 1
                logger.info("Response is not N sections, retrying...")
                continue

            sections = []
            pointer = 0
            for ending in endings:
                last_chars = document[pointer:].find(ending)

                if last_chars == -1:
                    # todo: handle edge? case: exact match not found -> rough match, or retry
                    logger.info(f"Couldn't find substring {ending} in the document")
                    pass

                split_pos = pointer + last_chars + len(ending)
                if pointer >= split_pos:
                    logger.error(f"new split position {split_pos} is not after the previous one {pointer}")
                    break
                sections.append(document[pointer: split_pos])
                pointer = split_pos

            if len(sections) == target_slides:
                return sections
            self.current_attempt += 1
        self.current_attempt = 0 # reset for the next time
        raise ValueError(f"failed to find a valid split after {self.num_retries} attempts")

