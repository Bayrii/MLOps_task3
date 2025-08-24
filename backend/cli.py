import json
import os

import boto3

ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
KBI = os.environ.get("KBI") 
REGION = os.environ.get("REGION") 



AWS_CONFIG = {
    'region': REGION,
    'access_key': ACCESS_KEY,
    'secret_key': SECRET_KEY,
}

model='us.anthropic.claude-3-7-sonnet-20250219-v1:0'

client = boto3.client(
        "bedrock-runtime",
        region_name=AWS_CONFIG['region'],
        aws_access_key_id=AWS_CONFIG['access_key'],
        aws_secret_access_key=AWS_CONFIG['secret_key'],
    )



def add_user_message(messages, prompt):
    user_message = {'role': 'user', 'content': prompt}
    messages.append(user_message)

def add_assistant_message(messages, prompt):
    assistant_message = {'role': 'assistant', 'content': prompt}
    messages.append(assistant_message)


def create_body_json(messages, max_tokens=1024, system=None, temperature=0.5, thinking=False):
    body_dict = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": max_tokens,
    "temperature": temperature,
    "messages": messages,
    }
    if system:
        body_dict['system'] = system
    
    if thinking:
        body_dict['thinking'] = {
                                "type": "enabled",
                                "budget_tokens": 1024,
                                }
    body_json = json.dumps(body_dict)
    return body_json


def create_body_json_with_tool(messages, max_tokens=1024, system=None, temperature=0.5, thinking=False, tools=None):
    body_dict = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": max_tokens,
    "temperature": temperature,
    "messages": messages,
    "tools": [tools]
    }
    if system:
        body_dict['system'] = system
    
    if thinking:
        body_dict['thinking'] = {
                                "type": "enabled",
                                "budget_tokens": 1024,
                                }
    body_json = json.dumps(body_dict)
    return body_json

def chat(messages, model=model, system=None, temperature=0.5, tools=None):
    params = {
        "max_tokens": 1014,
        "system": system,
        "temperature": temperature,
        "messages": messages,
        "tools": tools,
    }

    body_json = create_body_json_with_tool(**params)
    response = client.invoke_model(
        modelId=model,
        body=body_json
    )

    message = json.loads(response['body'].read().decode('utf-8'))
    return message['content'][0]['text']


bedrock_knowlegde_base = boto3.client(
    "bedrock-agent-runtime",
    region_name=AWS_CONFIG['region'],
    aws_access_key_id=AWS_CONFIG['access_key'],
    aws_secret_access_key=AWS_CONFIG['secret_key'],
)

knowledge_base_id = KBI   



def get_knowledge_base_data(user_query):
    """Retrieve Azercell policy and corporate information from the Bedrock Knowledge Base.

    Sends the user's query to the knowledge base (vector search) and returns the
    top matches as a single formatted string (e.g., "Document 1: ...") that
    concatenates the retrieved passages.

    Intended topics include ethics, code of conduct, compliance policies, Core Values,
    CEO messages, and other Azercell-related materials.

    Args:
        user_query (str): Natural-language question describing what to look up.

    Returns:
        str: Concatenated text of the retrieved documents/passages.
    """
    
    req = {
            "knowledgeBaseId": knowledge_base_id,
            "retrievalQuery": {"text": user_query},
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {
                    "numberOfResults": 3
                }
            }
    }
    response = bedrock_knowlegde_base.retrieve(**req)
    candidates = response.get("retrievalResults")
    vec_response = '\n\n'.join([f'Document {ind+1}: ' + i.get('content').get('text') for ind, i in enumerate(candidates)])
    return vec_response


get_knowledge_base_data_schema = {
  "name": "get_knowledge_base_data",
  "description": "Retrieve Azercell policy and corporate information from the Bedrock Knowledge Base (ethics, code of conduct, compliance, Core Values, CEO messages, etc.).",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_query": {
        "type": "string",
        "description": "Natural-language question to search in the Azercell knowledge base."
      }
    },
    "required": ["user_query"],
    "additionalProperties": False
  }
}


def make_stream(model, body_json):
    stream = client.invoke_model_with_response_stream(
                modelId=model,
                contentType="application/json",
                accept="application/json",
                body=body_json
            )
    return stream

def main():

    messages = []

    user_query = "Does Azercell lie to people?"

    messages.append({'role': 'user', 'content': user_query})

    body_json = create_body_json_with_tool(messages=messages, tools=get_knowledge_base_data_schema)
    
    response = client.invoke_model(
        modelId=model,
        body=body_json
    )

    message = json.loads(response['body'].read().decode('utf-8'))

    messages.append({"role": "assistant", "content": message['content']})
    
    result = get_knowledge_base_data(**message['content'][1]['input'])
    print(result)
    messages.append({
        "role": "user",
        "content": [
            {
            "type": "tool_result",
            "tool_use_id": message['content'][1]['id'],
            "content": str(result),
            "is_error": False
            }
        ]
})


    body_json = create_body_json_with_tool(messages=messages, tools=get_knowledge_base_data_schema)

    response = client.invoke_model(
        modelId=model,
        body=body_json
    )

    message = json.loads(response['body'].read().decode('utf-8'))
    print(message['content'][0]['text'])


    

if __name__ == "__main__":
    main()
