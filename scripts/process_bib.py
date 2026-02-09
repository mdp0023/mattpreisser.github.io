#!/usr/bin/env python3
"""
Parse publications.bib and generate HTML for about_me.html
Handles publications, presentations, invited presentations, and convened sessions
"""

import re
import sys
from pathlib import Path

def parse_bibtex(bib_file):
    """Parse BibTeX file and extract entries"""
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    # Match @article{key, ... } patterns
    pattern = r'@(\w+)\{\s*(\w+),\s*(.*?)\n\}'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        entry_type = match.group(1).lower()
        entry_key = match.group(2)
        entry_content = match.group(3)
        
        # Parse fields
        fields = {}
        field_pattern = r'(\w+)\s*=\s*{([^}]+)}'
        for field_match in re.finditer(field_pattern, entry_content):
            field_name = field_match.group(1).lower()
            field_value = field_match.group(2).strip()
            fields[field_name] = field_value
        
        fields['key'] = entry_key
        fields['type'] = entry_type
        entries.append(fields)
    
    return entries

def format_authors(author_string):
    """Format author string for display"""
    # Convert " and " to ", " for standard citation format
    author_string = author_string.replace(' and ', ', ')
    
    # Highlight Preisser's name
    author_string = author_string.replace('Preisser, M.', '<strong>Preisser, M.</strong>')
    author_string = author_string.replace('Preisser, Matthew', '<strong>Preisser, Matthew</strong>')
    return author_string

def month_to_number(month_str):
    """Convert month name to number for sorting"""
    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    return months.get(month_str.lower(), 0)

def generate_publications(entries):
    """Generate HTML for publications only"""
    
    pub_entries = [e for e in entries if e.get('type', 'article').lower() in ('article', 'incollection')]
    
    # Separate by status
    under_review = [e for e in pub_entries if e.get('status', '').lower() == 'under review']
    peer_reviewed = [e for e in pub_entries if e.get('status', '').lower() != 'under review']
    
    # Sort by year (newest first)
    under_review = sorted(under_review, key=lambda x: x.get('year', '0'), reverse=True)
    peer_reviewed = sorted(peer_reviewed, key=lambda x: x.get('year', '0'), reverse=True)
    
    html = []
    
    # Under Review / In Preparation
    if under_review:
        html.append('\t\t\t\t\t\t<h3>Under Review / In Preparation</h3>')
        start_num = len(under_review) + len(peer_reviewed)
        html.append(f'\t\t\t\t\t\t<ol reversed start="{start_num}">')
        
        for entry in under_review:
            formatted = format_publication(entry)
            html.append(f'\t\t\t\t\t\t\t<li>{formatted}</li>')
        
        html.append('\t\t\t\t\t\t</ol>')
        html.append('')
    
    # Peer-Reviewed Articles
    if peer_reviewed:
        html.append('\t\t\t\t\t\t<h3>Peer-Reviewed Journal Articles</h3>')
        start_num = len(peer_reviewed)
        html.append(f'\t\t\t\t\t\t<ol reversed start="{start_num}">')
        
        for entry in peer_reviewed:
            formatted = format_publication(entry)
            html.append(f'\t\t\t\t\t\t\t<li>{formatted}</li>')
        
        html.append('\t\t\t\t\t\t</ol>')
    
    return '\n'.join(html)

def generate_presentations(entries):
    """Generate HTML for conference presentations"""
    
    presentations = [e for e in entries if e.get('type', '').lower() == 'presentations']
    presentations = sorted(presentations, key=lambda x: (x.get('year', '0'), month_to_number(x.get('month', ''))), reverse=True)
    
    html = []
    
    if presentations:
        html.append('\t\t\t\t\t\t<h3>Conference Presentations</h3>')
        start_num = len(presentations)
        html.append(f'\t\t\t\t\t\t<ol reversed start="{start_num}">')
        
        for entry in presentations:
            formatted = format_presentation(entry)
            html.append(f'\t\t\t\t\t\t\t<li>{formatted}</li>')
        
        html.append('\t\t\t\t\t\t</ol>')
    
    return '\n'.join(html)

def generate_invited_presentations(entries):
    """Generate HTML for invited presentations"""
    
    invited = [e for e in entries if e.get('type', '').lower() == 'invited_presentation']
    invited = sorted(invited, key=lambda x: (x.get('year', '0'), month_to_number(x.get('month', ''))), reverse=True)
    
    html = []
    
    if invited:
        html.append('\t\t\t\t\t\t<h3>Invited Presentations</h3>')
        start_num = len(invited)
        html.append(f'\t\t\t\t\t\t<ol reversed start="{start_num}">')
        
        for entry in invited:
            formatted = format_invited_presentation(entry)
            html.append(f'\t\t\t\t\t\t\t<li>{formatted}</li>')
        
        html.append('\t\t\t\t\t\t</ol>')
    
    return '\n'.join(html)

def generate_convened_sessions(entries):
    """Generate HTML for convened sessions"""
    
    sessions = [e for e in entries if e.get('type', '').lower() == 'conference_session']
    sessions = sorted(sessions, key=lambda x: x.get('year', '0'), reverse=True)
    
    html = []
    
    if sessions:
        html.append('\t\t\t\t\t\t<h3>Convened Sessions</h3>')
        html.append('\t\t\t\t\t\t<ul>')
        
        for entry in sessions:
            formatted = format_convened_session(entry)
            html.append(f'\t\t\t\t\t\t\t<li>{formatted}</li>')
        
        html.append('\t\t\t\t\t\t</ul>')
    
    return '\n'.join(html)

def format_publication(entry):
    """Format a single publication entry as HTML"""
    
    entry_type = entry.get('type', 'article').lower()
    author = format_authors(entry.get('author', 'Author list'))
    year = entry.get('year', 'Year')
    title = entry.get('title', 'Title')
    doi = entry.get('doi', '')
    status = entry.get('status', '')
    
    # Format depends on entry type
    if entry_type == 'incollection':
        # For book chapters
        booktitle = entry.get('booktitle', '')
        pages = entry.get('pages', '')
        publisher = entry.get('publisher', '')
        
        citation = f"{author} ({year}). {title}. In <em>{booktitle}</em>"
        if pages:
            citation += f" (pp. {pages})"
        if publisher:
            citation += f". {publisher}"
        if doi:
            citation += f'. <a href="https://doi.org/{doi}" target="_blank">DOI: {doi}</a>'
        else:
            citation += "."
    else:
        # For journal articles (default)
        journal = entry.get('journal', 'Journal Name')
        volume = entry.get('volume', '')
        number = entry.get('number', '')
        pages = entry.get('pages', '')
        
        citation = f"{author} ({year}). {title}. <em>{journal}</em>"
        
        if volume:
            citation += f", {volume}"
            if number:
                citation += f"({number})"
            if pages:
                citation += f", {pages}"
        
        if doi:
            citation += f'. <a href="https://doi.org/{doi}" target="_blank">DOI: {doi}</a>'
        elif status:
            citation += f". ({status})"
        else:
            citation += "."
    
    return citation

def format_presentation(entry):
    """Format a conference presentation"""
    
    author = format_authors(entry.get('author', 'Author list'))
    year = entry.get('year', 'Year')
    title = entry.get('title', 'Title')
    conference = entry.get('conference', 'Conference Name')
    address = entry.get('address', 'Location')
    pres_type = entry.get('presentation_type', 'Presentation')
    month = entry.get('month', '')
    
    citation = f'{author} "{title}" – {conference}'
    if address:
        citation += f', {address}'
    if month:
        citation += f', {month} {year}'
    else:
        citation += f', {year}'
    citation += f'. ({pres_type})'
    
    return citation

def format_invited_presentation(entry):
    """Format an invited presentation"""
    
    author = format_authors(entry.get('author', 'Author list'))
    year = entry.get('year', 'Year')
    title = entry.get('title', 'Title')
    conference = entry.get('conference', 'Conference Name')
    address = entry.get('address', 'Location')
    pres_type = entry.get('presentation_type', 'Presentation')
    month = entry.get('month', '')

    citation = f'{author} "{title}" – {conference}'
    if address:
        citation += f', {address}'
    if month:
        citation += f', {month} {year}'
    else:
        citation += f', {year}'
    citation += f'. ({pres_type})'
    
    return citation

def format_convened_session(entry):
    """Format a convened session"""
    
    title = entry.get('title', 'Session Title')
    conference = entry.get('conference', 'Conference Name')
    address = entry.get('address', 'Location')
    year = entry.get('year', 'Year')
    conveners = entry.get('conveners', '')
    
    citation = f'<strong>{title}</strong> – {conference}, {address}, {year}'
    if conveners:
        conveners_formatted = format_authors(conveners)
        citation += f'<ul style="margin-top: 0.5em;"><li>Co-Conveners: {conveners_formatted}</li></ul>'
    
    return citation

def main():
    bib_file = Path(__file__).parent.parent / 'publications.bib'
    
    if not bib_file.exists():
        print(f"Error: {bib_file} not found")
        sys.exit(1)
    
    # Parse BibTeX
    entries = parse_bibtex(bib_file)
    
    if not entries:
        print("Warning: No entries found in BibTeX file")
        return
    
    # Generate HTML for each section and print as JSON-like output
    publications_html = generate_publications(entries)
    presentations_html = generate_presentations(entries)
    invited_html = generate_invited_presentations(entries)
    sessions_html = generate_convened_sessions(entries)
    
    # Output as structured sections separated by markers
    print("<!-- PUBLICATIONS_START -->")
    print(publications_html)
    print("<!-- PUBLICATIONS_END -->")
    print()
    print("<!-- PRESENTATIONS_START -->")
    print(presentations_html)
    print("<!-- PRESENTATIONS_END -->")
    print()
    print("<!-- INVITED_START -->")
    print(invited_html)
    print("<!-- INVITED_END -->")
    print()
    print("<!-- SESSIONS_START -->")
    print(sessions_html)
    print("<!-- SESSIONS_END -->")

if __name__ == '__main__':
    main()

