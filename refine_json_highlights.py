import json
import re
import os
import glob

# Configuration
DATA_DIR = r'c:\Users\blue2510\자체제작프로그램\ShortsToBenz3\data'

# Terms to Highlight (Concepts over Tools)
HIGHLIGHT_TERMS = [
    "본질", 
    "생산성", 
    "워크플로우", 
    "기획력", 
    "글쓰기 구조", 
    "기승전결", 
    "일관성", 
    "저품질 콘텐츠", 
    "콘텐츠 제작 가이드라인",
    "클멍", 
    "수익화", 
    "나만의 것",
    "시스템",
    "자동화",
    "대본",
    "스토리보드",
    "실행력"
]

# Terms specifically NOT to highlight (even if they might match partials, though unlikely for these)
# We handle this by just not including them in the list.
# But we must ensure we remove existing marks around "58", "음팔", "오팔", "Opal".

def clean_and_highlight(text):
    if not isinstance(text, str):
        return text
    
    # 1. Remove existing <mark> tags
    cleaned = re.sub(r'</?mark>', '', text)
    
    # 2. Apply new highlights
    # We use a placeholder to avoid double highlighting or nested tags during processing
    # But simple replacement is usually fine if terms don't overlap.
    
    # Sort terms by length (descending) to handle longer phrases first
    terms = sorted(HIGHLIGHT_TERMS, key=len, reverse=True)
    
    for term in terms:
        # Regex to match the term, avoiding already marked areas if we were doing complex stuff
        # For simplicity, we just replace. 
        # Note: This might highlight "본질" inside "기획력의 본질" resulting in nested or weird marks if not careful.
        # But given the list, overlaps are minimal. "콘텐츠 제작 가이드라인" vs "콘텐츠".
        
        # We use a temporary token to prevent re-matching
        # actually, just direct replacement is risky if specific order matters.
        # Let's try to be smart.
        pass

    # A better approach: 
    # Tokenize or just do sequential replacement with check?
    # Simple sequential replacement is often robust enough for this scale if sorted by length.
    
    for term in terms:
        # Check if term exists to save regex cost
        if term in cleaned:
             # Use a regex that ignores already marked sections? 
             # It's hard to do correctly with simple regex. 
             # Let's just do simple replace, but verify we don't break HTML.
             # The source text has strictly no HTML other than what we add (and maybe **bold**).
             
             # Case: "기획력" and "기획". If we highlight "기획력" first: <mark>기획력</mark>
             # Then "기획": <mark><mark>기획</mark>력</mark> -> BAD.
             
             # Example: "본질" is in list.
             # If "기획의 본질" appears. 
             
             # We should wrap specific keywords.
             # Let's simple replace, but only if NOT already inside a tag.
             # Since we start with clean text, we can just replace.
             # BUT we have to be careful not to highlight inside an existing tag attribute (unlikely here)
             # or inside a previously added <mark>.
             
             # Strategy: Use a compiled regex that matches ANY of the terms, and replace using a callback.
             pass
             
    # Compile one giant regex for all terms
    pattern = re.compile('|'.join(re.escape(term) for term in terms))
    
    def replace_func(match):
        return f"<mark>{match.group(0)}</mark>"
        
    # This ensures we process the string once from left to right, finding the longest match (if regex is ordered)
    # Re-compiling pattern with sorted terms ensures longest match wins in standard regex engines usually, 
    # but 're' module tries alternatives in order.
    
    final_text = pattern.sub(replace_func, cleaned)
    
    return final_text

def process_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Recursive function to traverse JSON
    def traverse(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str):
                    if k == 'content' or k == 'title': # Only highlight content and title
                        obj[k] = clean_and_highlight(v)
                elif isinstance(v, list):
                     # content is often a list of strings
                    if k == 'content':
                         new_list = []
                         for item in v:
                             if isinstance(item, str):
                                 new_list.append(clean_and_highlight(item))
                             else:
                                 new_list.append(item)
                         obj[k] = new_list
                    else:
                        traverse(v)
                else:
                    traverse(v)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item)

    traverse(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    for f in files:
        process_file(f)
    print("All files processed.")

if __name__ == "__main__":
    main()
