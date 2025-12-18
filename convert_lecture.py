import json
import re
import os
import glob
from pathlib import Path

# --- Configuration ---
DATA_DIR = 'data'
PAGES_DIR = 'pages'
OUTPUT_FILENAME_PATTERN = 'lecture{}.html'

# --- Text Cleaning Rules ---
# --- Text Cleaning Rules ---
def clean_text(text):
    if not text:
        return ""
    
    # 1. Remove timestamps like <<123,456>>
    text = re.sub(r'<<.*?>>', '', text)
    
    # 2. Replace specific terms
    replacements = {
        '음팔(58)': 'Opal (오팔)',
        '음팔': 'Opal (오팔)',
        '58': 'Opal (오팔)'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # 3. Handle Markdown Bold (**text**) -> <strong>text</strong>
    # This prevents raw ** from showing up in final HTML
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
    return text.strip()

# --- Money & Chart Logic ---
def extract_money_values(text):
    """
    Extracts money values and returns a dataset for the chart.
    Returns None if fewer than 2 distinct values are found (no comparison possible).
    """
    if not text:
        return None
        
    # Regex to find money patterns (e.g., 300만 원, 1억, 5천만)
    pattern = r'(\d+(?:[.,]\d+)?)\s*([만억천]+)?\s*원?'
    matches = re.findall(pattern, text)
    
    values = []
    
    for num_str, unit_str in matches:
        try:
            val = float(num_str.replace(',', ''))
            original_unit = unit_str if unit_str else ""
            label = f"{num_str}{original_unit}원"
            
            mult = 1
            if '억' in unit_str:
                mult *= 100000000
            elif '만' in unit_str:
                mult *= 10000
            elif '천' in unit_str:
                mult *= 1000
                
            final_val = val * mult
            
            # Filter distinct values close to each other to avoid duplicates
            if not any(abs(v['value'] - final_val) < 10 for v in values):
                values.append({'label': label, 'value': final_val})
        except:
            continue
            
    if len(values) < 2:
        return None
        
    return values

def generate_css_chart(money_data):
    if not money_data:
        return ""
        
    # Sort by value
    sorted_data = sorted(money_data, key=lambda x: x['value'])
    max_val = sorted_data[-1]['value']
    
    html = f"""
    <div class="mt-6 mb-4 bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-100 dark:border-gray-700">
        <div class="flex items-center mb-4">
            <div class="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mr-3">
                <i class="fas fa-chart-line text-emerald-600 dark:text-emerald-400"></i>
            </div>
            <h4 class="text-sm font-bold text-gray-800 dark:text-gray-200">수익/비용 시뮬레이션</h4>
        </div>
        <div class="space-y-3">
    """
    
    for item in sorted_data:
        # Calculate percentage (prevent 0%)
        percent = max(10, (item['value'] / max_val) * 100)
        is_max = (item['value'] == max_val)
        bar_color = "bg-emerald-500" if is_max else "bg-gray-300 dark:bg-gray-600"
        text_cls = "text-emerald-600 dark:text-emerald-400 font-bold" if is_max else "text-gray-600 dark:text-gray-300"
        
        html += f"""
        <div class="relative">
            <div class="flex justify-between text-xs mb-1">
                <span class="font-medium {text_cls}">{item['label']}</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div class="{bar_color} h-2.5 rounded-full transition-all duration-1000" style="width: {percent}%"></div>
            </div>
        </div>
        """
        
    html += """
        </div>
    </div>
    """
    return html

# --- HTML Generation Helpers ---
# --- Rendering Components ---

# --- Rendering Components (Neon/Dark Mode Style) ---

def get_card_theme(title):
    """
    Returns (border_color, text_color, icon, bg_hue, title_gradient) based on title keywords.
    Matches the user's reference image style.
    """
    t = title.lower()
    
    # Semantic Categories Only (No specific brands unless they are strictly 'Tools')
    
    # 1. Warning/Danger (Red)
    if any(x in t for x in ["경고", "금지", "주의", "trash", "쓰레기", "안되는", "실패", "절대"]):
        return "border-rose-600", "text-rose-500", "fa-ban", "bg-rose-900/10", "from-rose-500 to-red-500"
        
    # 2. Success/Profit/Goal (Green)
    elif any(x in t for x in ["목표", "성공", "달성", "생산성", "속도", "돈", "수익", "매출", "1억"]):
        return "border-emerald-500", "text-emerald-400", "fa-bullseye", "bg-emerald-900/10", "from-emerald-400 to-green-400"
        
    # 3. Tips/Deep Dive/Structure (Blue/Amber)
    elif any(x in t for x in ["tip", "팁", "노하우", "해결책", "비결", "핵심", "전략"]):
        return "border-blue-500", "text-blue-400", "fa-lightbulb", "bg-blue-900/10", "from-blue-400 to-cyan-400"
    
    # 4. Tools/Tech/AI (Purple - Generic)
    elif any(x in t for x in ["ai", "툴", "도구", "업무", "시스템", "자동화", "역할", "팀", "직원"]):
        return "border-indigo-500", "text-indigo-400", "fa-robot", "bg-indigo-900/10", "from-indigo-400 to-purple-400"
    
    # Default
    return "border-gray-700", "text-gray-300", "fa-cube", "bg-gray-800", "from-gray-200 to-gray-400"

def render_alert_box(title, content_list):
    """
    Renders the top 'Warning/Insight' box (Red/Blue block).
    Matches the reference image's Red Warning Box style.
    """
    clean_tit = title.replace('📌', '').replace('💡', '').strip()
    
    is_warning = "경고" in clean_tit or "trash" in clean_tit.lower() or "금지" in clean_tit
    
    if is_warning:
         # Strong Red Box
         bg_cls = "bg-[#7f1d1d] border-red-900" 
         icon = "fa-exclamation-triangle"
         tit_col = "text-white"
         text_col = "text-red-100"
    else:
         # Blue/Info Box
         bg_cls = "bg-slate-800 border-slate-700"
         icon = "fa-info-circle"
         tit_col = "text-blue-400"
         text_col = "text-slate-300"

    full_text = ""
    for c in content_list:
        cleaned = clean_text(c)
        if not cleaned: continue
        # Highlight logic
        cleaned = re.sub(r'<mark>(.*?)</mark>', r'<span class="font-bold underline Decoration-2">\1</span>', cleaned)
        cleaned = re.sub(r'<strong>(.*?)</strong>', r'<span class="font-bold text-white">\1</span>', cleaned)
        full_text += f"<p class='{text_col} leading-relaxed mb-2 last:mb-0'>{cleaned}</p>"

    return f"""
    <div class="{bg_cls} rounded-xl p-8 border mb-10 shadow-lg relative overflow-hidden">
        <h3 class="text-2xl font-bold {tit_col} mb-4 flex items-center">
            <i class="fas {icon} mr-3"></i>{clean_tit}
        </h3>
        <div class="text-lg">
            {full_text}
        </div>
    </div>
    """

def render_neon_card(title, items):
    """
    Smart Card Renderer.
    Parses content to detect:
    - Subtitles (Role: ...)
    - Sections (Why? Features)
    - Side Boxes (Tips, Strategies)
    """
    border_col, text_col, icon, bg_col, gradient_col = get_card_theme(title)
    
    # Internal Organization
    subtitle = ""
    main_section_title = ""
    main_items = []
    box_section = None # (title, items)
    
    # Parse Items to categorize them
    current_target = "main" # 'main' or 'box'
    
    for item in items:
        cleaned = clean_text(item)
        if not cleaned: continue
        
        # 1. Detect Subtitle (Role)
        # Matches "역할: ..." or "Role: ..."
        role_match = re.match(r'^(역할|Role)\s*[:：]\s*(.*)', cleaned, re.IGNORECASE)
        if role_match and not subtitle:
            subtitle = role_match.group(2)
            continue
            
        # 2. Detect Box Triggers (Tips, Strategy)
        if "Tip" in cleaned or "전략" in cleaned or "활용" in cleaned:
            # If it looks like a header logic
            if len(cleaned) < 30 and (":" not in cleaned or cleaned.endswith(":")):
                 current_target = "box"
                 box_section = {'title': cleaned.replace(':', ''), 'items': []}
                 continue
        
        # 3. Detect Main Section Headers (Why? Features)
        if ("왜" in cleaned or "특징" in cleaned or "장점" in cleaned) and "?" in cleaned or ":" in cleaned:
             if len(cleaned) < 40: # It's likely a header
                 main_section_title = cleaned.replace(':', '')
                 current_target = "main" # Switch back to main if we were in box (rare but possible)
                 continue
                 
        # 4. Add to target
        if current_target == "box" and box_section:
            box_section['items'].append(cleaned)
        else:
            main_items.append(cleaned)
            
    # --- HTML Rendering ---
    
    # 1. Header Area
    header_html = f"""
    <div class="flex items-start mb-6">
        <div class="w-12 h-12 rounded-lg {bg_col} {text_col} flex items-center justify-center text-xl mr-4 flex-shrink-0 border border-current border-opacity-30">
            <i class="fas {icon}"></i>
        </div>
        <div>
            <h4 class="text-xl font-bold text-gray-100">{title}</h4>
            {f'<p class="text-sm {text_col} font-medium mt-1">역할: {subtitle}</p>' if subtitle else ''}
        </div>
    </div>
    """
    
    # 2. Body Grid (Main + Box)
    # If there is a box, we layout as Grid (if space allows) or Stack
    # Reference image showing "Claude" has left content + right box.
    
    grid_cls = "grid grid-cols-1 lg:grid-cols-2 gap-6" if box_section else "block"
    
    # A. Main Content Column
    main_html = ""
    if main_section_title:
        main_html += f'<h5 class="text-md font-bold {text_col} mb-3 flex items-center"><i class="fas fa-thumbtack mr-2 text-xs"></i>{main_section_title}</h5>'
        
    main_html += '<ul class="space-y-2 text-gray-400 text-sm leading-relaxed">'
    for mi in main_items:
        # Style Bolds
        mi = re.sub(r'<strong>(.*?)</strong>', r'<span class="text-gray-200 font-bold">\1</span>', mi)
        main_html += f'<li class="flex items-start"><span class="mr-2 mt-1.5 w-1 h-1 rounded-full bg-gray-500 flex-shrink-0"></span><span>{mi}</span></li>'
    main_html += '</ul>'
    
    # B. Box Content Column
    box_html = ""
    if box_section:
        box_items_html = ""
        for bi in box_section['items']:
            bi = re.sub(r'<strong>(.*?)</strong>', r'<span class="text-gray-200 font-bold">\1</span>', bi)
            box_items_html += f'<li class="block text-gray-400 mb-2 last:mb-0 text-sm">{bi}</li>'
            
        box_html = f"""
        <div class="bg-gray-800/80 rounded-lg p-5 border border-gray-700 h-full">
            <h5 class="text-sm font-bold {text_col} mb-3 flex items-center">
                <i class="fas fa-lightbulb mr-2"></i>{box_section['title']}
            </h5>
            <ul class="space-y-1">
                {box_items_html}
            </ul>
        </div>
        """

    # Combine into Card
    return f"""
    <div class="bg-[#1e293b] rounded-xl p-6 border {border_col} shadow-xl relative overflow-hidden h-full">
        {header_html}
        
        <div class="{grid_cls}">
            <div class="mb-4 lg:mb-0">
                {main_html}
            </div>
            <div>
                {box_html}
            </div>
        </div>
    </div>
    """

def render_section(section_data, index):
    """
    Renders Level 1 Section using the Neon Layout.
    """
    title = clean_text(section_data.get('title', ''))
    title = re.sub(r'<mark>(.*?)</mark>', r'<strong>\1</strong>', title)
    
    # Insight Block Check (Top Level Warning/Quote)
    if any(x in title for x in ['📌', '💡']):
        return render_alert_box(title, section_data.get('content', []))

    section_id = f"lecture-part-{index}"
    content_raw_list = section_data.get('content', [])

    # Grouping Logic (Parse into Cards)
    cards_data = []
    loose_content = []

    for raw_text in content_raw_list:
        if not raw_text or raw_text.strip() == "![image]()": continue
        cleaned = clean_text(raw_text)
        if not cleaned: continue
        
        lines = cleaned.split('\n')
        first_line = lines[0].strip()
        # Header Heuristic: "1. Title" or "**Title**"
        header_match = re.match(r'^(\d+\.)?\s*(?:\*\*)?(.*?)(?:\*\*)?(:)?$', first_line)
        
        if header_match and (len(lines) > 1 or "**" in first_line):
             # It is a card
             card_title = header_match.group(2).strip()
             card_items = [re.sub(r'^\d+\.\s*', '', l.strip()) for l in lines[1:] if l.strip()]
             cards_data.append({'title': card_title, 'items': card_items})
        else:
             loose_content.append(cleaned)

    # HTML Assembly
    intro_html = ""
    for lc in loose_content:
        # Style loose text as "Lead Paragraphs"
        lc = re.sub(r'<mark>(.*?)</mark>', r'<span class="text-brand font-bold">\1</span>', lc)
        intro_html += f'<p class="text-gray-400 text-lg leading-relaxed mb-6 pl-4 border-l-2 border-gray-700">{lc}</p>'

    inner_cards = ""
    for card in cards_data:
        inner_cards += render_neon_card(card['title'], card['items'])
        
    return f"""
    <section id="{section_id}" class="max-w-7xl mx-auto mb-20 pt-10 border-t border-gray-800">
        <div class="mb-10">
            <span class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">Part {index+1}</span>
            <h2 class="text-3xl md:text-4xl font-black text-white mb-4 tracking-tight flex items-center">
                 {title}
            </h2>
        </div>
        
        {intro_html}
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {inner_cards}
        </div>
    </section>
    """

# --- Main Parsing Loop ---
# --- Main Parsing Loop ---
def process_lecture_data(lec_num, parts_files):
    # Pass 1: Collect Metadata for TOC
    # Structure: [ {'part_title': '...', 'id': 'part-X', 'sections': [ {'id':..., 'title':...} ]}, ... ]
    toc_structure = []
    
    if not parts_files:
        return "<div class='text-center p-10'>데이터 파일이 없습니다.</div>"

    parts_files.sort()
    
    temp_sections = [] # Store HTML chunks
    processed_count = 0
    section_index = 0
    
    for i, file_path in enumerate(parts_files):
        try:
            filename = os.path.basename(file_path)
            part_title = f"PART {i+1}"
            if "부" in filename:
                match = re.search(r'(\d+부.*?)\.', filename)
                if match:
                    part_title = match.group(1).strip()
                else:
                     part_title = os.path.splitext(filename)[0]

            part_id = f"part-{i+1}"
            
            # Start new Part Group
            current_part = {
                'title': part_title,
                'id': part_id,
                'sections': []
            }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # anchor for file
            file_anchor_html = f'<div id="{part_id}" class="scroll-mt-32"></div>'
            temp_sections.append(file_anchor_html)

            for item in data:
                if item.get('type') == 'section':
                    # Extract title for TOC
                    raw_title = clean_text(item.get('title', ''))
                    clean_tit = raw_title.replace('📌', '').replace('💡', '').strip()
                    clean_tit = re.sub(r'<mark>(.*?)</mark>', r'\1', clean_tit) # Clean marks
                    clean_tit = re.sub(r'<strong>(.*?)</strong>', r'\1', clean_tit) # Clean bolds
                    
                    # Filtering Logic for TOC
                    is_valid_toc = True
                    
                    if not clean_tit: 
                        is_valid_toc = False # Empty
                    elif clean_tit.endswith("?"):
                        is_valid_toc = False # Question titles (likely sub-content)
                    elif len(clean_tit) > 35:
                        is_valid_toc = False # Too long = likely a sentence/question
                    elif "Section" in clean_tit and any(char.isdigit() for char in clean_tit):
                        is_valid_toc = False # Generic fallback name
                    
                    sec_id = f"lecture-part-{section_index}"
                    
                    if is_valid_toc:
                        current_part['sections'].append({'id': sec_id, 'title': clean_tit})
                    
                    # Store HTML
                    html = render_section(item, section_index)
                    temp_sections.append(html)
                    
                    section_index += 1
                    processed_count += 1
            
            # Only add part if it has sections or is just a container
            toc_structure.append(current_part)
                    
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    if processed_count == 0:
         return "<div class='text-center text-gray-500 py-10'>변환할 콘텐츠가 없습니다. JSON 구조를 확인해주세요.</div>"

    # Generate Structured TOC HTML
    # If a part has NO valid TOC sections, maybe we just show the Part Title?
    
    toc_html = """
    <div class="bg-white dark:bg-dark-card rounded-2xl p-8 mb-20 shadow-xl border border-gray-100 dark:border-dark-border">
        <div class="flex items-center justify-between mb-8 border-b border-gray-100 dark:border-gray-800 pb-6">
            <h3 class="text-2xl font-black text-gray-900 dark:text-gray-100 flex items-center">
                <i class="fas fa-stream text-brand mr-3"></i>목차 (Table of Contents)
            </h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
    """
    
    for part in toc_structure:
        # If no sections, maybe skip or show empty list
        sections_html = ""
        if not part['sections']:
            sections_html = "<li class='text-xs text-gray-400 italic'>세부 목차 없음 (본문 참조)</li>"
        else:
            for sec in part['sections']:
                 sections_html += f"""
                 <li>
                    <a href="#{sec['id']}" class="flex items-start text-sm text-gray-600 dark:text-gray-400 hover:text-brand dark:hover:text-brand transition-colors py-1">
                        <span class="mr-2 mt-1.5 w-1.5 h-1.5 rounded-full bg-gray-300 dark:bg-gray-600 flex-shrink-0"></span>
                        <span class="leading-relaxed hover:underline">{sec['title']}</span>
                    </a>
                 </li>
                 """
        
        toc_html += f"""
        <div class="flex flex-col h-full bg-gray-50 dark:bg-gray-800/50 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
            <a href="#{part['id']}" class="block mb-4 group cursor-pointer">
                <h4 class="font-black text-lg text-gray-800 dark:text-gray-200 group-hover:text-brand transition-colors mb-1 line-clamp-2">
                    {part['title']}
                </h4>
                <div class="h-1 w-10 bg-gray-200 dark:bg-gray-600 rounded-full group-hover:bg-brand transition-colors"></div>
            </a>
            
            <ul class="space-y-2 flex-1">
                {sections_html}
            </ul>
        </div>
        """
        
    toc_html += """
        </div>
    </div>
    """
    
    full_html = toc_html
    for html in temp_sections:
        full_html += html
        
    return full_html


def main():
    # 1. Group files by Lecture Number
    all_files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    
    lectures = {} 
    
    for f in all_files:
        filename = os.path.basename(f)
        match = re.search(r'(\d+)강', filename)
        if match:
            lec_num = int(match.group(1))
        else:
            lec_num = 1
            
        if lec_num not in lectures:
            lectures[lec_num] = []
        lectures[lec_num].append(f)
        
    # 2. Process each lecture
    for lec_num, files in lectures.items():
        print(f"Processing Lecture {lec_num} with {len(files)} parts...")
        
        lecture_content_html = process_lecture_data(lec_num, files)
        
        # Navigation Extraction (Simple regex based on headers)
        # We need to construct navigation links for the sidebar/topbar if possible, 
        # but for now we just generate the content body.
        # The main 'shortstobenz3.html' handles the nav via scroll spy if standard IDs are used.
        
        final_html = f"""
        <!-- Generated Lecture Content -->
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 animate-fade-in-up">
            <div class="text-center mb-20">
                <span class="inline-block py-1 px-3 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-brand text-xs font-bold tracking-wider mb-4 border border-indigo-200 dark:border-indigo-800">PREMIUM CLASS</span>
                <h1 class="text-4xl md:text-5xl font-black text-gray-900 dark:text-white mb-6 tracking-tight">
                    정규 강의 <span class="text-transparent bg-clip-text bg-gradient-to-r from-brand to-purple-600">{lec_num}강</span>
                </h1>
                <p class="text-xl text-gray-500 dark:text-gray-400">AI 워크플로우와 수익화의 핵심을 마스터하세요.</p>
            </div>
            
            {lecture_content_html}
            
            <div class="mt-20 pt-10 border-t border-gray-200 dark:border-gray-800 text-center">
                <p class="text-gray-400 text-sm">ShortsToBenz Class • All Rights Reserved</p>
            </div>
        </div>
        """
        
        output_path = os.path.join(PAGES_DIR, OUTPUT_FILENAME_PATTERN.format(lec_num))
        os.makedirs(PAGES_DIR, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
        print(f"Created {output_path}")

    print("All conversions complete.")

if __name__ == "__main__":
    main()
