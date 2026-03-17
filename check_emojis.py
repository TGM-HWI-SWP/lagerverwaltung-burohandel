"""Check if all emojis have been removed"""
import os
import re

emoji_pattern = re.compile("[\U0001F300-\U0001F9FF]+")
files_with_emojis = []

# File extensions to check
extensions = ['.py', '.html']

for root, dirs, files in os.walk('.'):
    # Skip hidden and cache directories
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
    
    for file in files:
        if any(file.endswith(ext) for ext in extensions):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if emoji_pattern.search(content):
                        files_with_emojis.append(filepath)
            except:
                pass

if files_with_emojis:
    print("Dateien mit Emojis gefunden:")
    for f in files_with_emojis:
        print(f"  - {f}")
else:
    print("✓ Erfolg: Keine Emojis gefunden! Die Anwendung wirkt jetzt professioneller.")
