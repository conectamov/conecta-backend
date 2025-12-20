import numpy as np
from typing import Sequence


class SimilarityService:
    @staticmethod
    def cosine_similarity(
        vec_a: Sequence[float],
        vec_b: Sequence[float]
    ) -> float:

        a = np.array(vec_a, dtype=float)
        b = np.array(vec_b, dtype=float)

        if a.shape != b.shape:
            raise ValueError("Os vetores precisam ter a mesma dimensão")

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))
