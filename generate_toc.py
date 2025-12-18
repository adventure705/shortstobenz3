import re

path = r'c:\Users\blue2510\자체제작프로그램\ShortsToBenz3\pages\lecture1.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to capture the 3 cards
# They start with <div class="flex flex-col h-full
# End with </div> inside the grid.
# Actually, the grid is bounded by <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"> ... </div>
# I will capture the whole grid block content.

start_marker = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">'
end_marker = '<!-- Generated Lecture Content -->' # No, this is before.
# Let's find the specific block.
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Grid not found")
    exit()

# The grid ends before <div id="part-1"
end_marker_str = '<div id="part-1"'
end_idx = content.find(end_marker_str)

grid_content = content[start_idx:end_idx]
# Remove the last closing div of the grid
# The grid has <div ...> [Card 1] [Card 2] [Card 3] </div> <div id=...>
# content[start_idx:end_idx] includes the opening tag, content, and the closing tag </div> right before <div id="part-1"
# Let's clean the grid_content.
# Actually, I'll just iterate through the "flex flex-col" blocks in the file content within that range.

card_pattern = re.compile(r'<div class="flex flex-col h-full.*?<h4.*?>(.*?)</h4>.*?<ul.*?>(.*?)</ul>', re.DOTALL)

cards = card_pattern.findall(grid_content)

new_html = '<div class="space-y-4">\n'

for title, list_items in cards:
    clean_title = re.sub(r'<.*?>', '', title).strip()
    
    # Reconstruct UL
    # Make sure we keep the list items intact.
    # The 'list_items' capture group is the inner content of UL? No, regex above is likely fragile.
    # Let's match the UL block.
    
    pass

# Simplified Approach:
# Just take the huge chunks of strings for each card manually.
# Card 1: Lines 21-235 (approx)
# Card 2: Lines 237-332
# Card 3: Lines 334-443

# I will assume the structure is consistent and just use regex to extract title and UL body.
card_matches = re.findall(r'(<div class="flex flex-col h-full.*?)(?=<div class="flex flex-col h-full|</div>\s*</div>)', grid_content, re.DOTALL)
# This regex is hard.

# Let's go with the simpler Python script that just reads valid HTML lines
# logic:
# 1. extract lines 21-235 -> section 1
# 2. extract lines 237-332 -> section 2
# 3. extract lines 334-443 -> section 3
# 4. wrap each.

lines = content.splitlines()

# 0-indexed: line 1 is index 0.
# Card 1
s1 = lines[20:235]  # Line 21 to 235
# Card 2
s2 = lines[236:332] # Line 237 to 332
# Card 3
s3 = lines[333:443] # Line 334 to 443

sections = [s1, s2, s3]
new_html = '<div class="space-y-4">\n'

for section_lines in sections:
    text = "\n".join(section_lines)
    # Extract Title
    title_match = re.search(r'<h4.*?>(.*?)</h4>', text, re.DOTALL)
    title = re.sub(r'<.*?>', '', title_match.group(1)).strip() if title_match else "Part"
    
    # Extract UL
    ul_match = re.search(r'<ul.*?>(.*?)</ul>', text, re.DOTALL)
    ul_content = ul_match.group(1).strip() if ul_match else ""
    
    accordion_item = f'''
    <div class="border border-gray-200 dark:border-dark-border rounded-xl overflow-hidden">
        <button class="accordion-btn w-full px-6 py-4 flex justify-between items-center bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors" onclick="toggleAccordion(this)">
            <h4 class="font-bold text-lg text-gray-800 dark:text-gray-200">{title}</h4>
            <i class="fas fa-chevron-down accordion-icon text-gray-400"></i>
        </button>
        <div class="accordion-content bg-white dark:bg-dark-card" style="display:none;">
            <div class="p-6">
                <ul class="space-y-2">
                    {ul_content}
                </ul>
            </div>
        </div>
    </div>'''
    new_html += accordion_item + "\n"

new_html += "</div>"

with open('new_toc.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
