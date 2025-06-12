import os
import sys
from dotenv import load_dotenv

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser

# Assuming these files exist in the same directory or a configured path
from .types import DetectionDocumentation
from .prompts import SYSTEM_PROMPT_TEMPLATE, HUMAN_PROMPT_TEMPLATE

load_dotenv()


class DetectionDocAgent:
    """
    Agent that takes a Sigma rule (in YAML format) and generates structured,
    analyst-friendly detection documentation using an LLM.

    The output follows the Palantir detection strategy framework format
    and is parsed into a Pydantic model: DetectionDocumentation.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the DetectionDocAgent with a specified OpenAI model.

        Args:
            model_name (str): The name of the OpenAI model to use (default: gpt-4o-mini).
        """
        self.model = ChatOpenAI(
            name=model_name
        )

        # Define the system and human message templates
        self.system_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_TEMPLATE)
        self.human_prompt = HumanMessagePromptTemplate.from_template(
            template=HUMAN_PROMPT_TEMPLATE,
            input_variables=["sigma_rule"]
        )

        # Combine prompts into a single chat prompt template
        self.chat_prompt = ChatPromptTemplate.from_messages([self.system_prompt, self.human_prompt])

        # Define the parser to convert LLM output into DetectionDocumentation
        self.parser = PydanticOutputParser(pydantic_object=DetectionDocumentation)

        # Chain: Prompt → Model → Parser
        self.chain = self.chat_prompt | self.model | self.parser

    def process(self, sigma_rule: str) -> DetectionDocumentation:
        """
        Convert a Sigma rule into structured detection documentation.

        Args:
            sigma_rule (str): Raw Sigma rule in YAML format.

        Returns:
            DetectionDocumentation: Parsed and structured detection content.

        Raises:
            RuntimeError: If parsing fails.
        """
        try:
            return self.chain.invoke({"sigma_rule": sigma_rule})
        except Exception as e:
            raise RuntimeError(f"Failed to process Sigma rule: {str(e)}")

    def display_prompt(self, sigma_rule: str) -> str:
        """
        Render the formatted prompt (system + human) that will be sent to the LLM.

        Args:
            sigma_rule (str): The Sigma rule to be converted.

        Returns:
            str: Fully formatted prompt as a string.
        """
        messages = self.chat_prompt.format_messages(sigma_rule=sigma_rule)

        def content_to_string(content) -> str:
            """
            Helper to safely convert message content to a readable string.
            """
            if content is None:
                return ""
            elif isinstance(content, str):
                return content
            elif isinstance(content, list):
                result = ""
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        result += item["text"]
                    elif isinstance(item, str):
                        result += item
                return result
            else:
                return str(content)

        prompt_display = "=== SYSTEM PROMPT ===\n"
        prompt_display += content_to_string(messages[0].content) + "\n\n"
        prompt_display += "=== HUMAN PROMPT ===\n"
        prompt_display += content_to_string(messages[1].content) + "\n"

        return prompt_display


def main():
    """
    Main function to run the agent from the command line.
    """
    yaml_text = """
    title: PowerShell Download From URL

id: d60e8bd9-a305-4dd3-a2fb-4c392c95f52f

description: Detects PowerShell command used to download files from a URL using common methods.

references:

  - <https://threatpost.com/powershell-security-pitfalls/157345/>
  - <https://attack.mitre.org/techniques/T1059/001/>
status: stable

author: Florian Roth

date: 2022/04/10

tags:

  - attack.execution

  - attack.t1059.001

logsource:

  category: process_creation

  product: windows

detection:

  selection:

    Image|endswith:

      - '\\powershell.exe'

      - '\\pwsh.exe'

    CommandLine|contains:

      - 'Invoke-WebRequest'

      - 'Invoke-Expression'

      - 'System.Net.WebClient'

  condition: selection

falsepositives:

  - Admin scripts

  - Penetration testing activity

level: high

    """

    # --- The following lines have been activated ---

    # 1. Initialize the agent
    agent = DetectionDocAgent()

    # 2. (Optional) Display the exact prompt being sent to the LLM
    # print("\n--- LLM PROMPT PREVIEW ---")
    print(agent.display_prompt(yaml_text))

    # 3. Process the rule to get structured documentation
    print("\n--- Processing rule with the LLM. Please wait... ---")
    try:
        result = agent.process(yaml_text)

        # 4. Print the final, structured JSON output
        print("\n=== STRUCTURED DETECTION DOCUMENTATION ===")
        print(result.model_dump_json(indent=2))

    except RuntimeError as e:
        print(f"\n--- ERROR ---")
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()