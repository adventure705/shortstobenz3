path = r'c:\Users\blue2510\자체제작프로그램\ShortsToBenz3\pages\lecture1.html'
toc_path = r'c:\Users\blue2510\자체제작프로그램\ShortsToBenz3\new_toc.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

with open(toc_path, 'r', encoding='utf-8') as f:
    new_toc = f.read()

start_marker = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">'
end_marker_str = '<div id="part-1"'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker_str)

if start_idx == -1 or end_idx == -1:
    print(f"Markers not found. Start: {start_idx}, End: {end_idx}")
    exit()

# The grid ends with </div> just before <div id="part-1"
# We want to replace everything from start_marker up to (but not including) <div id="part-1"
# minus the whitespace between them.
# Wait, content[start_idx:end_idx] contains the grid AND the whitespace/newlines after it.
# The grid block starts at start_idx.
# Find where the grid block ends. It's a single big div.
# But inside can be nested divs.
# Simpler: The structure is:
# ...
# </div> (header)
# <div class="grid ..."> ... </div> (toc)
# <div id="part-1" ...>

# So we can just replace everything from start_idx up to end_idx with new_toc + '\n    '
# Just make sure we don't eat the <div id="part-1" tag.
# end_idx points to the '<' of <div id="part-1".
# So content[:start_idx] + new_toc + "\n    " + content[end_idx:] should be correct.

new_content = content[:start_idx] + new_toc + "\n    " + content[end_idx:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated TOC successfully.")
