import ctypes
import os
import zlib
from typing import List, Tuple

# Locate and load the compiled dynamic library
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../libminhash_lsh.so"))

class LSHIndexStruct(ctypes.Structure):
    pass

lsh_lib = ctypes.CDLL(lib_path)

lsh_lib.lsh_init.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
lsh_lib.lsh_init.restype = ctypes.POINTER(LSHIndexStruct)

lsh_lib.lsh_free.argtypes = [ctypes.POINTER(LSHIndexStruct)]
lsh_lib.lsh_free.restype = None

lsh_lib.compute_minhash.argtypes = [
    ctypes.POINTER(LSHIndexStruct),
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_size_t
]
lsh_lib.compute_minhash.restype = ctypes.POINTER(ctypes.c_uint32)

lsh_lib.estimate_jaccard_similarity.argtypes = [
    ctypes.POINTER(LSHIndexStruct),
    ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32)
]
lsh_lib.estimate_jaccard_similarity.restype = ctypes.c_float

class MinHashDeduplicator:
    def __init__(self, num_hashes: int = 128, num_bands: int = 16, k_shingle: int = 3):
        self.num_hashes = num_hashes
        self.num_bands = num_bands
        self.k_shingle = k_shingle
        self.index = lsh_lib.lsh_init(num_hashes, num_bands)
        if not self.index:
            raise RuntimeError("Failed to initialize C MinHash LSH Index")

    def __del__(self):
        if hasattr(self, 'index') and self.index:
            lsh_lib.lsh_free(self.index)

    def _shingle_document(self, text: str) -> List[int]:
        tokens = text.lower().split()
        if len(tokens) < self.k_shingle:
            shingles = [" ".join(tokens)]
        else:
            shingles = [" ".join(tokens[i:i+self.k_shingle]) for i in range(len(tokens) - self.k_shingle + 1)]
        return [zlib.crc32(s.encode('utf-8')) for s in shingles]

    def compute_signature(self, text: str):
        shingles = self._shingle_document(text)
        shingle_arr = (ctypes.c_uint64 * len(shingles))(*shingles)
        sig_ptr = lsh_lib.compute_minhash(self.index, shingle_arr, len(shingles))
        return sig_ptr

    def get_jaccard_similarity(self, sig_a, sig_b) -> float:
        return float(lsh_lib.estimate_jaccard_similarity(self.index, sig_a, sig_b))

    def deduplicate_passages(self, passages: List[str], sim_threshold: float = 0.75) -> List[str]:
        signatures = [self.compute_signature(p) for p in passages]
        retained = []
        retained_sigs = []

        for i, (passage, sig) in enumerate(zip(passages, signatures)):
            is_dup = False
            for prev_sig in retained_sigs:
                sim = lsh_lib.estimate_jaccard_similarity(self.index, sig, prev_sig)
                if sim >= sim_threshold:
                    is_dup = True
                    break
            if not is_dup:
                retained.append(passage)
                retained_sigs.append(sig)

        return retained
