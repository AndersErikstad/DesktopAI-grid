import os
import google.generativeai as genai

# Configure the API key
genai.configure(api_key='AIzaSyDOgG3PjicRTDuQuBFGLP4lreWBxJqfuMo') 


# Set up the generation configuration
generation_config = {
    "temperature": 0.01,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2997,
}

# Instantiate the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config,
)

def create_chat_completion(image_path, messages, request_plan=True):
    # Build prompt parts
    prompt_parts = []
    
    # Upload the image and include it in prompt_parts
    image_file = genai.upload_file(image_path)
    prompt_parts.append(image_file)
    
    # Build the conversation in the prompt parts
    for message in messages:
        role = message['role']
        content = message['content']
        if role == 'system':
            prompt_parts.append(content)
        elif role == 'user':
            prompt_parts.append(f"User: {content}")
        elif role == 'assistant':
            prompt_parts.append(f"Assistant: {content}")
    
    # Add request for plan or commands
    if request_plan:
        prompt_parts.append("Provide a concise plan for completing the task.")
    else:
        prompt_parts.append("Provide only the commands without explanations or additional steps.")
    
    # Generate the response using the working example method
    try:
        response = model.generate_content(prompt_parts)
        return response.text  # Access the generated text content
    except Exception as e:
        print("Exception occurred during AI response generation:")
        print(e)
        return ""