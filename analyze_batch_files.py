import json

files = [
    '/workspace/data/overviews/medications_batch_3/medications_overview_batch_3_comprehensive.json',
    '/workspace/data/overviews/medications_batch_4/medications_overview_batch_4_real.json',
    '/workspace/data/overviews/medications_batch_5/medications_overview_batch_5_extracted.json',
    '/workspace/data/overviews/medications_batch_6/consolidated_all_medications.json',
    '/workspace/data/overviews/medications_batch_7/medications_overview_batch_7.json',
]

for file_path in files:
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f"\n{file_path.split('/')[-1]}:")
        print(f"  Top-level keys: {list(data.keys())[:5]}")
        
        # Find the products array
        for key in data.keys():
            if isinstance(data[key], list) and len(data[key]) > 0:
                print(f"  Array key '{key}': {len(data[key])} items")
                if isinstance(data[key][0], dict):
                    print(f"    First item keys: {list(data[key][0].keys())[:8]}")
                break
    except Exception as e:
        print(f"\n{file_path.split('/')[-1]}: Error - {str(e)[:100]}")
