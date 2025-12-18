import re
import os

file_path = r'c:\Users\blue2510\자체제작프로그램\ShortsToBenz3\pages\lecture1.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for the Part span
# <span class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">Part 3</span>
pattern = r'<span class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">\s*Part \d+\s*</span>'

new_content = re.sub(pattern, '', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully removed Part spans.")
