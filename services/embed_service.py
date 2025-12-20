import numpy as np
from sentence_transformers import SentenceTransformer
from utils.tags import tags

class EmbedService:
    _model = None
    _tag_embeddings = None

    @classmethod
    def init(cls):
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
            cls._tag_embeddings = cls._model.encode(
                tags, convert_to_numpy=True
            )

    @classmethod
    def user_vector_from_indices(cls, indices: list[int]) -> np.ndarray:
        if cls._tag_embeddings is None:
            cls.init()

        if not indices:
            return np.zeros(cls._tag_embeddings.shape[1], dtype=float)

        vecs = cls._tag_embeddings[indices]
        mean_vec = vecs.mean(axis=0)

        norm = np.linalg.norm(mean_vec)
        if norm > 0:
            mean_vec = mean_vec / norm

        return mean_vec
