import os
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyDOgG3PjicRTDuQuBFGLP4lreWBxJqfuMo")

# Set up the generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.8,
    "top_k": 10,
    "max_output_tokens": 8192,
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",  # Specify the model name
    generation_config=generation_config
)

def create_chat_completion(image_path, messages, request_plan=True):
    # Build prompt parts
    prompt_parts = []

    # Upload the image and handle the response
    try:
        image_token = genai.upload_file(image_path)
        prompt_parts.append(image_token)  # Append the image file to the prompt
    except Exception as e:
        print(f"Error uploading image: {e}")
        return ""
    
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
    
    # Generate the response using the model's `generate_content` method
    try:
        response = model.generate_content(prompt_parts)
        return response.text  # Return the generated text
    except Exception as e:
        print("Exception occurred during AI response generation:")
        print(e)
        return ""

# Example usage
if __name__ == "__main__":
    # Define the path to the image (screenshot.png)
    image_path = "screenshot.png"

    # Define the conversation messages
    messages = [
        {"role": "system", "content": "You are an AI assistant helping the user control their computer."},
        {"role": "user", "content": "I want to open Google Chrome and search for AI research papers."}
    ]

    # Call the function and print the result
    result = create_chat_completion(image_path, messages, request_plan=True)
    print(result)
