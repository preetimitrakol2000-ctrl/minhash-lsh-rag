from bindings.lsh_bridge import MinHashDeduplicator

def main():
    raw_retrieved_chunks = [
        "Retrieval-Augmented Generation enhances LLMs by pulling ground-truth documents at query time.",
        "Retrieval-Augmented Generation enhances LLMs by pulling relevant external document chunks at query time.",
        "Quantization compresses neural networks by mapping floating point numbers to lower precision integers.",
        "LLMs combined with vector retrieval significantly reduce hallucination rates in enterprise AI.",
        "Quantization compresses deep neural networks by mapping 32-bit floats to reduced precision ints."
    ]

    print("=== Raw Retrieved Context Chunks ===")
    for i, chunk in enumerate(raw_retrieved_chunks, 1):
        print(f"[{i}] {chunk}")

    deduper = MinHashDeduplicator(num_hashes=128, num_bands=16, k_shingle=3)
    unique_chunks = deduper.deduplicate_passages(raw_retrieved_chunks, sim_threshold=0.65)

    print("\n=== Deduplicated Context Window (MinHash LSH Output) ===")
    for i, chunk in enumerate(unique_chunks, 1):
        print(f"[{i}] {chunk}")

if __name__ == "__main__":
    main()
