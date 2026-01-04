# This file contains client that will send reqs to llm, we use Claud

import os
import anthropic
import logging

from anthropic.types.beta.message_create_params import OutputFormat
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class OutputFormat(BaseModel):
    endings: list[str]

class SectionerAgent:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY', None)
        if api_key is None:
            raise ValueError('ANTHROPIC_API_KEY not defined in .env')
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5"
        self.max_token = 4000 # for model definition
        self.max_input_tokens = 180000  # Approximate limit for inference


    def _get_prompt(self, document, target_slides):
        prompt = f"""
                You are helping split a markdown document into exactly {target_slides} sections for a presentation slide deck, by specifying the ending of each section. 
                Each section should represent one cohesive idea that could become a single slide.

                TASK: Return a JSON object with an 'endings' array containing EXACTLY {target_slides} unique text snippets. Each snippet marks where one section ENDS.

                CRITICAL REQUIREMENTS:
                1. You must return exactly {target_slides} snippets (one for each section ending)
                2. Each snippet is the LAST 40-60 characters of a section
                3. Only section at natural semantic boundaries (use headers, ideas, or paragraphs as cues)
                4. DO NOT split in the middle of words, sentences, list items, or tables
                5. The content must be preserved exactly (don't fix typos or omit leading whitespaces)
                6. Each snippet must be unique (appear only once in the document)

                OUTPUT FORMAT:
                Return a JSON object with an 'endings' array containing EXACTLY {target_slides} strings. No explanation, no markdown code blocks, just the array:
                ['snippet 1', 'snippet 2', ..., 'snippet {target_slides}']
                
                EXAMPLE:
                If asked for 3 sections, return 3 snippets:
                {{
                    'endings': [
                        'text ending section 1',
                        'text ending section 2', 
                        'text ending section 3'
                    ]
                }}

                SNIPPETS SHOULD:
                - Be 40-60 characters long
                - Include trailing newlines/punctuation if present
                - Come from natural section boundaries
                - Be unique (not repeated elsewhere in document)

                Document to split:
                {document}

                Return only the JSON array, no other text.
            """
        return prompt


    def get_llm_response(self, document, target_slides):
        # Warn if document is too long (can use divide and induction to counteract this)
        estimated_tokens = len(document) // 4  # Rough estimate
        if estimated_tokens > self.max_input_tokens:
            logger.warning(f"Document may exceed token limit (~{estimated_tokens} tokens)")

        if os.getenv('DEBUG') == '1':
            return ['workflows faster than ever before.', 'economic actors in the fiell.\n']

        try:
            prompt = self._get_prompt(document, target_slides)
            message = self.client.beta.messages.parse(
                model=self.model,
                max_tokens=self.max_token,
                messages=[{"role": "user", "content": prompt}],
                betas=['structured-outputs-2025-11-13'],
                output_format=OutputFormat
            )
            response_dict = message.parsed_output
            logger.info(f"llm response: {response_dict}")
            if isinstance(response_dict, OutputFormat):
                endings = response_dict.endings
                logger.info(f"Extracted {len(endings)} endings")
                return endings
            else:
                logger.error(f"Response missing 'endings' key: {response_dict}")
                return None

        except anthropic.BadRequestError as e:
            logger.error(f"Bad request error (possibly schema validation): {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling LLM: {e}")
            return None
