import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from src import app_constants as app_consts

# Load environment variables from .env
load_dotenv()

bedrock_model = app_consts.BEDROCK_HAIKU
groq_model = "llama-3.3-70b-versatile"  # Default high-performance model for Groq


def set_LLM_model(llm_model):
    # Change the LLM to use
    global bedrock_model, groq_model
    if "claude" in llm_model.lower():
        bedrock_model = llm_model
    else:
        groq_model = llm_model


def get_llm_response(payload):
    groq_api_key = os.environ.get("GROQ_API_KEY")

    if groq_api_key:
        from groq import Groq
        groq_client = Groq(api_key=groq_api_key)

        try:
            # We map temperature and stop sequences to the Groq SDK
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": payload}
                ],
                model=groq_model,
                temperature=0.01,
                max_tokens=1024,
                stop=app_consts.BEDROCK_STOP_SEQUENCE,
            )
            completion = chat_completion.choices[0].message.content
            result = ' '.join(completion.split())  # remove newlines and extra spaces
            return result
        except Exception as err:
            print(f"A Groq error occurred: {err}")
            return None
    else:
        bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=app_consts.BEDROCK_AWS_REGION)
        result = None

        inference_config = {
            "temperature": 0.01,  # Set the temperature for generating consistent responses
            "maxTokens": 1024,  # Set the maximum number of tokens to generate
            "stopSequences": app_consts.BEDROCK_STOP_SEQUENCE,  # Define the stop sequences for generation
        }
        # Define additional model fields
        additional_model_fields = {"top_p": 0.99}

        # Create the converse method parameters
        converse_api_params = {
            "modelId": bedrock_model,
            "messages": [{"role": "user", "content": [{"text": payload}]}],  # Provide the prompt
            "inferenceConfig": inference_config,  # Pass the inference configuration
            "additionalModelRequestFields": additional_model_fields  # Pass additional model fields
        }

        # Send a request to the LLM to generate a response
        try:
            response = bedrock_client.converse(**converse_api_params)

            # Extract the generated text content from the response
            completion = response['output']['message']['content'][0]['text']

            result = ' '.join(completion.split())  # remove newlines and extra spaces

        except ClientError as err:
            message = err.response['Error']['Message']
            print(f"A client error occurred: {message}")

        return result