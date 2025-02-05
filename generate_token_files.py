import random
import tiktoken
import os

def get_token_count(text):
    """Count tokens in text using tiktoken"""
    enc = tiktoken.get_encoding("cl100k_base")  # Using GPT-4's encoding
    return len(enc.encode(text))

def generate_random_text(min_length=100):
    """Generate random text of at least min_length words"""
    words = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I',
             'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
             'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
             'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what']
    
    text = []
    while len(text) < min_length:
        text.append(random.choice(words))
    return ' '.join(text)

def create_file_with_tokens(target_tokens, filename):
    """Create a file with approximately target_tokens count"""
    current_tokens = 0
    text = []
    
    while current_tokens < target_tokens:
        # Generate a chunk of text
        new_text = generate_random_text(100)
        text.append(new_text)
        
        # Count tokens in current text
        current_text = ' '.join(text)
        current_tokens = get_token_count(current_text)
        
        print(f"Current token count for {filename}: {current_tokens}")
    
    # Write to file
    with open(filename, 'w') as f:
        f.write(' '.join(text))
    
    return current_tokens

def main():
    # Target token counts
    targets = [1000, 5000, 10000, 15000, 20000, 30000, 40000, 50000, 100000]
    
    for target in targets:
        filename = f"text_{target}_tokens.txt"
        if not os.path.exists(filename):
            actual_tokens = create_file_with_tokens(target, filename)
            print(f"Created {filename} with {actual_tokens} tokens")
        else:
            print(f"Skipping {filename} as it already exists")

if __name__ == "__main__":
    main()