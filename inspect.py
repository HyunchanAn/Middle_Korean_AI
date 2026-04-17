import json
from huggingface_hub import hf_hub_download

pry = hf_hub_download(repo_id='seyoungsong/Open-Korean-Historical-Corpus', filename='aks_kyu_nhm.jsonl', repo_type='dataset', cache_dir='data/raw/okhc/cache')
with open(pry, 'r', encoding='utf-8') as f:
    for i in range(2):
        print(f.readline())
