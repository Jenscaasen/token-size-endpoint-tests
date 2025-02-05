import requests
import json
import os
from typing import Dict, Optional

def get_initial_config() -> Dict[str, str]:
    """Get the initial configuration from user input."""
    print("\n=== API Configuration ===")
    base_url = input("Enter the base URL (e.g., https://example.models.ai.azure.com/v1): ").strip()
    api_key = input("Enter your API key: ").strip()
    model_name = input("Enter the model name: ").strip()
    
    return {
        "base_url": base_url,
        "api_key": api_key,
        "model_name": model_name
    }

def load_token_file(token_size: str) -> Optional[str]:
    """Load the content of a token file."""
    filename = f"text_{token_size}_tokens.txt"
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return None

def make_api_request(config: Dict[str, str], token_content: str) -> None:
    """Make the API request with the given configuration and token content."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}"
    }
    
    data = {
        "model": config["model_name"],
        "messages": [
            {
                "role": "user",
                "content": f"return only the word 'OK'. Ignore the rest of this message. {token_content}"
            }
        ]
    }
    
    url = f"{config['base_url']}/chat/completions"
    
    try:
        print("\nSending request...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nError: Request failed with status code {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"\nError making request: {e}")

def main():
    print("=== OpenAI Endpoint Token Test ===")
    
    # Get initial configuration
    config = get_initial_config()
    
    while True:
        # Show token size menu
        print("\n=== Select Token Size ===")
        print("1. 1,000 tokens")
        print("2. 5,000 tokens")
        print("3. 10,000 tokens")
        print("4. 15,000 tokens")
        print("5. 20,000 tokens")
        print("6. 30,000 tokens")
        print("7. 40,000 tokens")
        print("8. 50,000 tokens")
        print("9. 100,000 tokens")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ").strip()
        
        if choice == "10":
            print("\nExiting...")
            break
            
        token_sizes = {
            "1": "1000",
            "2": "5000",
            "3": "10000",
            "4": "15000",
            "5": "20000",
            "6": "30000",
            "7": "40000",
            "8": "50000",
            "9": "100000"
        }
        
        if choice not in token_sizes:
            print("Invalid choice! Please select a number between 1 and 10.")
            continue
        
        # Load token file content
        token_content = load_token_file(token_sizes[choice])
        if token_content is None:
            continue
            
        # Make API request
        make_api_request(config, token_content)
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()