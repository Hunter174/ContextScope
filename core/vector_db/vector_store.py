import faiss
from sklearn.feature_extraction.text import TfidfVectorizer


class FaissVectorStore:
    def __init__(self, debug=True, preview_chars=120):
        self.vectorizer = TfidfVectorizer(
            max_features=512,
            token_pattern=r"(?u)\b\w+\b"
        )

        self.texts = []
        self.index = None
        self.dim = None

        self.debug = debug
        self.preview_chars = preview_chars

    # ---------- logging ----------
    def _log(self, *args):
        if self.debug:
            print("[VectorStore]", *args)

    def _preview(self, text):
        text = text.replace("\n", " ")
        return text[:self.preview_chars] + ("..." if len(text) > self.preview_chars else "")

    # ---------- add ----------
    def add(self, text: str):
        if not text or not text.strip():
            return

        self._log("\nSTORE:", self._preview(text))
        self._log("Length:", len(text))

        self.texts.append(text)

        # ---- recompute embeddings ----
        X = self.vectorizer.fit_transform(self.texts).toarray().astype("float32")

        # normalize for cosine similarity
        faiss.normalize_L2(X)

        self.index = faiss.IndexFlatIP(X.shape[1])
        self.dim = X.shape[1]
        self.index.add(X)

        self._log("Index size:", len(self.texts))

    # ---------- search ----------
    def search(self, query: str, k=5):
        if not self.texts:
            self._log("SEARCH skipped: no data")
            return []

        self._log("\n=== SEARCH ===")
        self._log("Query:", self._preview(query))

        q = self.vectorizer.transform([query]).toarray().astype("float32")

        if q.shape[1] != self.dim:
            self._log("Dimension mismatch")
            return []

        faiss.normalize_L2(q)

        scores, indices = self.index.search(q, k)

        results = []
        self._log("Top results:")

        for rank, (idx, score) in enumerate(zip(indices[0], scores[0])):
            if 0 <= idx < len(self.texts):
                text = self.texts[idx]
                results.append(text)

                self._log(
                    f"#{rank+1} | score={score:.3f}",
                    "|",
                    self._preview(text)
                )

        self._log("=== END SEARCH ===\n")

        return results