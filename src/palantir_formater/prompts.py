from .types import DetectionDocumentation
import json

# Get the JSON schema from the Pydantic model
detection_schema = DetectionDocumentation.model_json_schema()

# Format it nicely for the prompt
formatted_schema = json.dumps(detection_schema, indent=2)

# Escape curly braces for LangChain compatibility
escaped_schema = formatted_schema.replace("{", "{{").replace("}", "}}")

# Format the system template using Python's .format() BEFORE passing it to LangChain
SYSTEM_PROMPT_TEMPLATE = f"""
You are a senior detection engineer assisting in writing high-quality security detection documentation. 
Your job is to transform structured threat detection rules (written in Sigma format) into analyst-friendly documentation 
following the Palantir Detection Strategy Framework.

For better insights refer to the following documentation for sigma rules:
https://github.com/SigmaHQ/sigma

For better insights refer to the following documentation for the Palantir Detection Strategy Framework:
https://www.palantir.com/docs/detection-strategy-framework/


Write clearly, accurately, and concisely for a SOC (Security Operations Center) analyst audience. 
Stick to the framework's tone: professional, explanatory, and focused on actionable insights.
Use the following schema:
{escaped_schema}
"""

# The human prompt still uses LangChain templating
HUMAN_PROMPT_TEMPLATE = """
Please transform the detection rule into a structured documentation following the Palantir Detection Strategy Framework.
{sigma_rule}
"""
