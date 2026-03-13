import re

with open('src/config/core_state.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove Legacy layer
text = re.sub(r'# -{75}\n# Legacy CORE Layer.*?CORE_PAIRINGS = \{\n.*?\n\}\n*', '', text, flags=re.DOTALL)

# 2. Fix TETRALOGIE dictionary to only have the first core key
text = re.sub(r'\"core\": \"([CORE])\", \"core\": \"[A-Z]\",', r'\"core\": \"\1\",', text)

# 3. Fix SIMULATION_EVIDENCE_STATS to only have the CORE line
text = re.sub(r'\"core_verteilung\": \{\"L\": 19, \"P\": 13, \"I\": 13, \"S\": 13\}, # Legacy keys kept for stats compatibility\n\s+\"core_verteilung\":', '\"core_verteilung\":', text)

with open('src/config/core_state.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Fixed core_state.py')
