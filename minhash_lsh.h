#ifndef MINHASH_LSH_H
#define MINHASH_LSH_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define MAX_TOKEN_LEN 64

typedef struct {
    uint32_t a;
    uint32_t b;
} HashFunc;

typedef struct {
    size_t num_hashes;
    size_t num_bands;
    size_t rows_per_band;
    HashFunc *hash_funcs;
} LSHIndex;

typedef struct {
    uint32_t doc_id;
    uint32_t *signature;
} MinHashSig;

#ifdef __cplusplus
extern "C" {
#endif

LSHIndex* lsh_init(size_t num_hashes, size_t num_bands);
void lsh_free(LSHIndex *index);

uint32_t* compute_minhash(LSHIndex *index, const uint64_t *shingle_hashes, size_t shingle_count);
float estimate_jaccard_similarity(LSHIndex *index, const uint32_t *sig_a, const uint32_t *sig_b);
bool is_near_duplicate(LSHIndex *index, const uint32_t *sig_a, const uint32_t *sig_b, float threshold);

#ifdef __cplusplus
}
#endif

#endif // MINHASH_LSH_H
