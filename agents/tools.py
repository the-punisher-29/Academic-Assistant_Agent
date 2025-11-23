import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def search_curriculum(query: str) -> str:
    """Search for curriculum information in the data files."""
    results = []
    # Search all txt files in data dir
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    
    query_words = query.lower().split()
    # Filter out common stop words to improve keyword matching
    stop_words = {"search", "for", "find", "check", "look", "what", "is", "are", "the", "of", "in", "about", "tell", "me"}
    keywords = [w for w in query_words if w not in stop_words]
    
    if not keywords:
        keywords = query_words

    MAX_RESULT_LENGTH = 4000 # Limit total output size to avoid 413 errors
    current_length = 0

    for filename in files:
        if current_length >= MAX_RESULT_LENGTH:
            break
            
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                content_lower = content.lower()
                
                # Check if any of the keywords are present
                if any(k in content_lower for k in keywords):
                    # Extract relevant snippets instead of full file
                    snippets = []
                    for k in keywords:
                        start_idx = content_lower.find(k)
                        if start_idx != -1:
                            # Take 500 chars before and after
                            start = max(0, start_idx - 500)
                            end = min(len(content), start_idx + 1000)
                            snippet = content[start:end].replace("\n", " ")
                            snippets.append(f"...{snippet}...")
                    
                    if snippets:
                        # Deduplicate snippets roughly
                        unique_snippets = list(set(snippets))
                        combined_snippets = "\n".join(unique_snippets[:3]) # Limit snippets per file
                        
                        result_entry = f"Found in {filename}:\n{combined_snippets}\n"
                        if current_length + len(result_entry) < MAX_RESULT_LENGTH:
                            results.append(result_entry)
                            current_length += len(result_entry)
    
    if not results:
        return "No curriculum information found matching the query."
    return "\n\n".join(results)

def read_calendar(query: str = "") -> str:
    """Read the academic calendar."""
    filepath = os.path.join(DATA_DIR, "academic_calendar.txt")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            return content
    return "Academic calendar not found."

def web_search(query: str) -> str:
    """Simulated web search."""
    return f"Simulated web search result for: {query}. (In a real scenario, this would call a search API)"

def save_plan(plan: str) -> str:
    """Save the generated plan to a file."""
    filepath = os.path.join(DATA_DIR, "current_plan.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(plan)
    return f"Plan saved to {filepath}"

def log_critique(critique: str) -> str:
    """Log the critic's feedback/response to a file."""
    filepath = os.path.join(DATA_DIR, "critique_log.txt")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n---\n{critique}\n")
    return "Critique logged."
