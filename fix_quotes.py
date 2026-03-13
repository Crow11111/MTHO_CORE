with open('src/config/core_state.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\\"core\\": \\"M\\"', '"core": "M"')
text = text.replace('\\"core\\": \\"O\\"', '"core": "O"')
text = text.replace('\\"core\\": \\"T\\"', '"core": "T"')
text = text.replace('\\"core\\": \\"H\\"', '"core": "H"')

with open('src/config/core_state.py', 'w', encoding='utf-8') as f:
    f.write(text)
