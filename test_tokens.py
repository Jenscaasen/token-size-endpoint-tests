import requests
import json
import os
import time
import datetime
from typing import Dict, Optional

CONNECTIONS_FILE = 'saved_connections.json'
REUSED_CONNECTION = False

def load_saved_connections() -> Dict[str, Dict[str, str]]:
    """Load saved connections from JSON file."""
    if os.path.exists(CONNECTIONS_FILE):
        try:
            with open(CONNECTIONS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_connection(config: Dict[str, str], name: str) -> None:
    """Save a connection configuration to JSON file."""
    # Load existing connections as a list
    if os.path.exists(CONNECTIONS_FILE):
        with open(CONNECTIONS_FILE, 'r') as f:
            try:
                connections = json.load(f)
            except json.JSONDecodeError:
                connections = []
    else:
        connections = []
    
    # Add new connection with name
    connections.append({"name": name, "config": config})
    
    with open(CONNECTIONS_FILE, 'w') as f:
        json.dump(connections, f, indent=2)
    print(f"\nConnection saved as '{name}'")

def get_initial_config() -> Dict[str, str]:
    """Get the initial configuration from user input."""
    connections = load_saved_connections()
    if isinstance(connections, dict):
        connections = [{"name": k, "config": v} for k, v in connections.items()]

    if connections:
        print("\n=== Saved Connections ===")
        print("0. Create new connection")
        for i, conn in enumerate(connections, 1):
            print(f"{i}. {conn['name']}")
        
        global REUSED_CONNECTION
        while True:
            choice = input("\nSelect a connection (0 for new): ").strip()
            if choice == "0":
                break
            try:
                index = int(choice) - 1
                if 0 <= index < len(connections):
                    REUSED_CONNECTION = True
                    return dict(connections[index]['config'])
            except ValueError:
                pass
            print("Invalid choice! Please try again.")
    
    # Create new connection
    print("\n=== New API Configuration ===")
    config = {
        "base_url": input("Enter the base URL (e.g., https://example.models.ai.azure.com/v1): ").strip(),
        "api_key": input("Enter your API key: ").strip(),
        "model_name": input("Enter the model name: ").strip()
    }
    
    return config

def offer_save_connection(config: Dict[str, str]) -> None:
    """Offer to save the current connection configuration."""
    save_choice = input("\nWould you like to save this connection for future use? (y/n): ").strip().lower()
    if save_choice == 'y':
        name = input("Enter a name for this connection: ").strip()
        save_connection(config, name)

def load_token_file(token_size: str) -> Optional[str]:
    """Load the content of a token file."""
    filename = f"text_{token_size}_tokens.txt"
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return None

def make_api_request(config: Dict[str, str], token_content: str, token_size: str) -> None:
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
    
    # Initialize timing variables
    start_time = None
    first_token_time = None
    last_token_time = None
    token_count = 0
    
    try:
        print("\nSending streaming request...")
        data["stream"] = True  # Enable streaming
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        if response.status_code == 200:
            print("\nStreaming Response:")
            start_time = time.time()
            
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line.decode('utf-8').lstrip('data: '))
                        if 'choices' in json_response and json_response['choices']:
                            content = json_response['choices'][0].get('delta', {}).get('content')
                            
                            if content:
                                # Record time of first token
                                if first_token_time is None:
                                    first_token_time = time.time()
                                
                                # Update token count and last token time
                                token_count += 1
                                last_token_time = time.time()
                                
                                print(content, end='', flush=True)
                    except json.JSONDecodeError:
                        continue
            print()  # New line after streaming completes
            
            # Calculate metrics
            time_to_first = round(first_token_time - start_time, 2) if first_token_time else 0
            time_to_last = round(last_token_time - start_time, 2) if last_token_time else 0
            tokens_per_second = round(int(token_size) / time_to_last, 2) if time_to_last > 0 else 0
            
            # Create or append results to measurement_results.csv
            csv_file = 'measurement_results.csv'
            file_exists = os.path.isfile(csv_file)
            
            with open(csv_file, 'a') as f:
                # Write header if file is new
                if not file_exists:
                    f.write('server,model,token_size,tokens_per_second,time_to_first_token,time_to_last_token,date_time\n')
                
                # Get current date and time
                current_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Write results with date and time
                f.write(f"\n{config['base_url']},{config['model_name']},{token_size},{tokens_per_second},{time_to_first},{time_to_last},{current_dt}")
                
           # Offer to save the connection if this is a new connection
            if not REUSED_CONNECTION:
                offer_save_connection(config)
            
        else:
            print(f"\nError: Request failed with status code {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"\nError making streaming request: {e}")

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
        make_api_request(config, token_content, token_sizes[choice])
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()