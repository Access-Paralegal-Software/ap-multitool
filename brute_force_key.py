import urllib.request
import json
import itertools

base_key = "AlzaSyBVog5QeCaEkafa0pzdJm1maLlhjs-31Yw"

key_list = list(base_key)
key_list[1] = 'I' # Standard prefix AIzaSy guaranteed

# Broaden the ambiguity search:
# Index 20: '0' (could be 'O', 'o')
# Index 26: '1' (could be 'I', 'l')
# Index 29: 'L' (could be 'I', '1', 'l')
# Index 30: 'l' (could be 'I', '1', 'L')
# Index 36: '3' (could be 'B', '8'?) -> less likely
# Index 37: '1' (could be 'I', 'l')

ambig_indices = [20, 26, 29, 30, 37]
options = {
    20: ['0', 'O', 'o'],
    26: ['1', 'I', 'l'],
    29: ['L', 'I', '1', 'l'],
    30: ['l', 'I', '1', 'L'],
    37: ['1', 'I', 'l']
}

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
payload = {"contents":[{"parts":[{"text":"hi"}]}]}
data_bytes = json.dumps(payload).encode('utf-8')

found = False
combinations = list(itertools.product(*[options[i] for i in ambig_indices]))
print(f"Testing {len(combinations)} broader key permutations...")

tested = 0
for comb in combinations:
    test_key = list(key_list)
    for idx, char in zip(ambig_indices, comb):
        test_key[idx] = char
    
    full_key = "".join(test_key)
    
    req_url = f"{url}?key={full_key}"
    req = urllib.request.Request(req_url, data=data_bytes, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.getcode() == 200:
                print(f"\n[SUCCESS] Valid API Key found: {full_key}")
                with open('/tmp/gemini_valid_key.txt', 'w') as f:
                    f.write(full_key)
                found = True
                break
    except Exception as e:
        pass
    tested += 1
    if tested % 50 == 0:
        print(f"Tested {tested} permutations...")

if not found:
    print("\n[FAILED] None of the broader permutations worked.")
