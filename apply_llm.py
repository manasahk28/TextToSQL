import boto3
from botocore.exceptions import ClientError

import app_constants as app_consts

# The run method of this class will take a LLM_PROMPT_PAYLOAD and invoke an LLM with the payload
# It will then return a dictionary that includes: the JSON output from the LLM, plus processing status


bedrock_model=app_consts.BEDROCK_HAIKU


def set_LLM_model(llm_model):
    # Change the bedrock LLM to use

    global bedrock_model
    bedrock_model = llm_model


def get_llm_response(payload):
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