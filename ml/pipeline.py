import pickle
import pandas as pd
from ml.pipe import Pipe
import logging

class MLPipeLine:
    def __init__(self, df_path: str, embeds_path: str, ) -> None:
        embeds = None
        with open(embeds_path, "rb") as file:
            embeds = pickle.load(file) 
        self.pipe = Pipe(
            pd.read_csv(df_path, sep=";"),
            embeds,
            device="cpu",
            compute_type="float32"
        )
    
    def get_errors(self, query: str, train_name: str, index: int = 0, useSpeachToText: bool = True):
        data = (None, None)
        if useSpeachToText:
            data = self.pipe(query, train_name)
            
        else:
            data = self.pipe(query, train_name, useSpeachToText)

        return data[0], data[1]
    
    # def generate(self, data: dict[str, str|list[str]]) -> str:
    #     er_re =data["reasons"], data["solutions"]
    #     print(er_re)
    #     msg = f'**{data["problem"]}**'
    #     for i, v in enumerate(data["reasons"]):
    #         msg += v + "\n\n" + data["solutions"] 
    #     logging.debug(msg)

    #     return msg