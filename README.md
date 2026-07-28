# MinHash-LSH-RAG

Sub-millisecond near-duplicate document deduplication for context window optimization using probabilistic MinHash Locality-Sensitive Hashing in pure C.

## Compilation & Run Instructions

```bash
# Compile shared dynamic library
gcc -O3 -shared -fPIC -Iinclude src/minhash_lsh.c -o libminhash_lsh.so

# Execute python test driver
python3 app/dedup_rag_app.py
