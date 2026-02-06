#!/usr/bin/env python3
"""
Local helper script to update about_me.html from publications.bib
Run this locally to test changes before pushing to GitHub
"""

import re
import subprocess
from pathlib import Path

def update_html():
    """Generate HTML from BibTeX and update about_me.html"""
    
    # Generate new HTML
    result = subprocess.run(
        ['python', 'process_bib.py'], 
        capture_output=True, 
        text=True,
        cwd=Path(__file__).parent
    )
    
    if result.returncode != 0:
        print(f"❌ Error running process_bib.py: {result.stderr}")
        return False
    
    output = result.stdout.strip()
    
    # Extract each section from the output
    publications_match = re.search(r'<!-- PUBLICATIONS_START -->(.*?)<!-- PUBLICATIONS_END -->', output, re.DOTALL)
    presentations_match = re.search(r'<!-- PRESENTATIONS_START -->(.*?)<!-- PRESENTATIONS_END -->', output, re.DOTALL)
    invited_match = re.search(r'<!-- INVITED_START -->(.*?)<!-- INVITED_END -->', output, re.DOTALL)
    sessions_match = re.search(r'<!-- SESSIONS_START -->(.*?)<!-- SESSIONS_END -->', output, re.DOTALL)
    
    if not all([publications_match, presentations_match, invited_match, sessions_match]):
        print("❌ Could not extract all sections from process_bib.py output")
        return False
    
    publications_content = publications_match.group(1).strip()
    presentations_content = presentations_match.group(1).strip()
    invited_content = invited_match.group(1).strip()
    sessions_content = sessions_match.group(1).strip()
    
    # Read current about_me.html
    about_file = Path(__file__).parent.parent / 'about_me.html'
    with open(about_file, 'r') as f:
        html_content = f.read()
    
    # Update Publications section - flexible whitespace matching
    pub_pattern = r'(<!--\s*AUTO-GENERATED:\s*Publications.*?<!--\s*DO NOT EDIT.*?\n\n)(.*?)(<!--\s*END AUTO-GENERATED:\s*Publications\s*-->)'
    if not re.search(pub_pattern, html_content, re.DOTALL | re.IGNORECASE):
        print("❌ Could not find Publications section markers in about_me.html")
        return False
    
    html_content = re.sub(pub_pattern, r'\1' + publications_content + r'\n\n\3', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Update Presentations section
    pres_pattern = r'(<!--\s*AUTO-GENERATED:\s*Presentations.*?<!--\s*DO NOT EDIT.*?\n\n)(.*?)(<!--\s*END AUTO-GENERATED:\s*Presentations\s*-->)'
    if not re.search(pres_pattern, html_content, re.DOTALL | re.IGNORECASE):
        print("❌ Could not find Presentations section markers in about_me.html")
        return False
    
    html_content = re.sub(pres_pattern, r'\1' + presentations_content + r'\n\n\3', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Update Invited Presentations section
    invited_pattern = r'(<!--\s*AUTO-GENERATED:\s*Invited Presentations.*?<!--\s*DO NOT EDIT.*?\n\n)(.*?)(<!--\s*END AUTO-GENERATED:\s*Invited Presentations\s*-->)'
    if not re.search(invited_pattern, html_content, re.DOTALL | re.IGNORECASE):
        print("❌ Could not find Invited Presentations section markers in about_me.html")
        return False
    
    html_content = re.sub(invited_pattern, r'\1' + invited_content + r'\n\n\3', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Update Convened Sessions section
    sessions_pattern = r'(<!--\s*AUTO-GENERATED:\s*Convened Sessions.*?<!--\s*DO NOT EDIT.*?\n\n)(.*?)(<!--\s*END AUTO-GENERATED:\s*Convened Sessions\s*-->)'
    if not re.search(sessions_pattern, html_content, re.DOTALL | re.IGNORECASE):
        print("❌ Could not find Convened Sessions section markers in about_me.html")
        return False
    
    html_content = re.sub(sessions_pattern, r'\1' + sessions_content + r'\n\n\3', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Write back
    with open(about_file, 'w') as f:
        f.write(html_content)
    
    print("✓ Updated about_me.html successfully!")
    print(f"✓ Publications: {len(publications_content)} characters")
    print(f"✓ Presentations: {len(presentations_content)} characters")
    print(f"✓ Invited Presentations: {len(invited_content)} characters")
    print(f"✓ Convened Sessions: {len(sessions_content)} characters")
    return True

if __name__ == '__main__':
    update_html()
