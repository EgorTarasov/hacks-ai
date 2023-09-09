from cherche import retrieve
from cherche.index import Faiss
from sentence_transformers import SentenceTransformer


class Search:
    def __init__(
        self,
        on: list[str],
        model_name: str = None,
        k: int = 3,
        key: str = "id",
        df=None,
    ) -> None:
        if model_name is None:
            model_name = (
                "sentence-transformers/distilbert-multilingual-nli-stsb-quora-ranking"
            )
        self.model = retrieve.Encoder(
            key=key,
            on=on,
            encoder=SentenceTransformer(model_name).encode,
            k=k,
        )
        self.key = key

        if df is not None:
            self.init_index(df)

    def init_index(self, df):
        self.model.index = Faiss(key=self.key)

        documents = df.to_dict(orient="records")
        self.model.add(documents=documents)

        return self.model.index

    def get_new_index(self, df):
        return self.init_index(df)

    def load_index(self, index):
        self.model.index = index

    def __call__(self, query: list[str] | str, k: int | None = None) -> dict:
        if isinstance(k, int):
            self.model.k = k

        return self.model(query)
