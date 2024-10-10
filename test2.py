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

def create_chat_completion(image_paths, messages):
    # Build prompt parts
    prompt_parts = []

    # Upload both images (screenshot and grid_marked_screenshot)
    try:
        for image_path in image_paths:
            image_token = genai.upload_file(image_path)
            prompt_parts.append(image_token)  # Append each image file to the prompt
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
    
    # Generate the response using the model's `generate_content` method
    try:
        response = model.generate_content(prompt_parts)
        return response.text  # Return the generated text
    except Exception as e:
        print("Exception occurred during AI response generation:")
        print(e)
        return ""

def main():
    # Define the paths to the images
    image_paths = ["grid_screenshot.png"]

    # Create an initial message list with the system prompt
    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]

    print("You can now interact with the AI. Type 'exit' to stop.")

    while True:
        # Get user input from the terminal
        user_input = input("You: ")

        # Exit condition
        if user_input.lower() == 'exit':
            print("Exiting the program.")
            break

        # Append the user's input to the messages
        messages.append({"role": "user", "content": user_input})

        # Send both images and the messages to the API
        response = create_chat_completion(image_paths, messages)

        # Display the assistant's response
        if response:
            print(f"Assistant: {response}")
            # Append the assistant's response to the messages for context
            messages.append({"role": "assistant", "content": response})
        else:
            print("No response received from the AI.")

if __name__ == "__main__":
    main()


