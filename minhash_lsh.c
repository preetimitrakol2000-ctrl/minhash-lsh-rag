#include "../include/minhash_lsh.h"
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define PRIME 4294967291U // Large prime for universal hashing

LSHIndex* lsh_init(size_t num_hashes, size_t num_bands) {
    if (num_hashes % num_bands != 0) return NULL;
    
    LSHIndex *index = (LSHIndex*)malloc(sizeof(LSHIndex));
    index->num_hashes = num_hashes;
    index->num_bands = num_bands;
    index->rows_per_band = num_hashes / num_bands;
    
    index->hash_funcs = (HashFunc*)malloc(sizeof(HashFunc) * num_hashes);
    
    // Seed reproducible pseudorandom coefficients
    srand(42);
    for (size_t i = 0; i < num_hashes; i++) {
        index->hash_funcs[i].a = (uint32_t)(rand() % (PRIME - 1)) + 1;
        index->hash_funcs[i].b = (uint32_t)(rand() % PRIME);
    }
    
    return index;
}

void lsh_free(LSHIndex *index) {
    if (!index) return;
    if (index->hash_funcs) free(index->hash_funcs);
    free(index);
}

uint32_t* compute_minhash(LSHIndex *index, const uint64_t *shingle_hashes, size_t shingle_count) {
    if (!index || !shingle_hashes || shingle_count == 0) return NULL;
    
    uint32_t *sig = (uint32_t*)malloc(sizeof(uint32_t) * index->num_hashes);
    for (size_t i = 0; i < index->num_hashes; i++) {
        sig[i] = UINT32_MAX;
    }
    
    for (size_t h = 0; h < index->num_hashes; h++) {
        uint64_t a = index->hash_funcs[h].a;
        uint64_t b = index->hash_funcs[h].b;
        
        for (size_t s = 0; s < shingle_count; s++) {
            uint32_t val = (uint32_t)((a * shingle_hashes[s] + b) % PRIME);
            if (val < sig[h]) {
                sig[h] = val;
            }
        }
    }
    
    return sig;
}

float estimate_jaccard_similarity(LSHIndex *index, const uint32_t *sig_a, const uint32_t *sig_b) {
    if (!index || !sig_a || !sig_b) return 0.0f;
    
    size_t matches = 0;
    for (size_t i = 0; i < index->num_hashes; i++) {
        if (sig_a[i] == sig_b[i]) {
            matches++;
        }
    }
    return (float)matches / (float)index->num_hashes;
}

bool is_near_duplicate(LSHIndex *index, const uint32_t *sig_a, const uint32_t *sig_b, float threshold) {
    float sim = estimate_jaccard_similarity(index, sig_a, sig_b);
    return sim >= threshold;
}
