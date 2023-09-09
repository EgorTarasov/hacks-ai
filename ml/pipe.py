import ast
from faster_whisper import WhisperModel

from ml.search import Search
from ml.qa import QA
import uuid
import re
from num2words import num2words


appendix_map = {
    "2М62,2М62У": 1,
    "2ТЭ10М,2ТЭ10МК,2ТЭ10У,2ТЭ10УК": 2,
    "2ТЭ25А": 3,
    "2ТЭ25КМ": 4,
    "2ТЭ70": 5,
    "2ТЭ116": 6,
    "2ТЭ116УД": 7,
    "2ЭС4К": 8,
    "2ЭС5К,3ЭС5К": 9,
    "2ЭС6": 10,
    "2ЭС7": 11,
    "2ЭС10": 12,
    "ВЛ10,ВЛ10У": 13,
    "ВЛ10К": 14,
    "ВЛ11,ВЛ11М": 15,
    "ВЛ11М": 16,
    "ВЛ15": 17,
    "ВЛ65": 18,
    "ВЛ80Р": 19,
    "ВЛ80С": 20,
    "ВЛ80Т": 21,
    "ВЛ85": 22,
    "ТЭМ2": 23,
    "ТЭМ7А": 24,
    "ТЭМ14": 25,
    "ТЭМ18Д,ТЭМ18ДМ": 26,
    "ТЭП70": 27,
    "ТЭП70БС": 28,
    "ЧМЭ3": 29,
    "ЧС2": 30,
    "ЧС2К": 31,
    "ЧС2Т": 32,
    "ЧС4Т": 33,
    "ЧС6,ЧС200": 34,
    "ЧС7": 35,
    "ЧС8": 36,
    "ЭП1,ЭП1М": 37,
    "ЭП2К": 38,
    "ЭП10": 39,
    "ЭП20": 40,
}




class Pipe:
    def __init__(self, data, embeds, device="cuda", compute_type="float16") -> None:
        self.speech2text = WhisperModel(
            "medium", device=device, compute_type=compute_type
        )
        self.ranker = Search(key='uniq_id', on = ['category', 'problem'])
        # self.qa = QA()

        self.data = data
        self.embeds = embeds

    def __call__(self, query, train_name, use_speech2text=True):
        if use_speech2text:
            segments, info = self.speech2text.transcribe(query, beam_size=3)
            query = "".join([segment.text for segment in segments])

        self.ranker.load_index(self.embeds[train_name])
        top_k = self.ranker(query)

        # answer = self.qa(text)
        return Output(top_k, self.data), query


class Output:
    def __init__(self, top_k, data) -> None:
        self.top_k = top_k
        self.data = data

    def __getitem__(self, idx):
        if idx > len(self.top_k):
            raise IndexError
        
        idx = self.top_k[idx]["uniq_id"]
        problem = self.data.loc[idx, "problem"]
        problem_id = self.data.loc[idx, "problem_id"]
        appendix = appendix_map[self.data.loc[idx, "train_name"]]
        reason = ast.literal_eval(self.data.loc[idx, "reason"])
        solution = ast.literal_eval(self.data.loc[idx, "solution"])
        
        text = self._generate_prompt(problem, reason, solution, problem_id, appendix)
        return text

    def _generate_prompt(self, problem: str, reason: list[str], solution: list[str], problem_id: int, appendix: int):
        
        reason = "\n".join([f"{i+1}. {v}" for i, v in enumerate(reason)])
        solution = "\n".join([f"{i+1}. {v}" for i, v in enumerate(solution)])
        text = f"Приложение №{appendix}, неисправность №{problem_id}: {problem}\n\nВероятные причины:\n{reason}.\n\nМетоды устранения:\n{solution}."

        return text

class Text2Speech:
    def __init__(self):
        from RUTTS import TTS
        from num2words import num2words
        import re

        self.tts = TTS("TeraTTS/natasha-g2p-vits")

        from ruaccent import RUAccent
        self.accentizer = RUAccent(workdir="./model")
        self.accentizer.load(omograph_model_size='medium', dict_load_startup=False)
        
    def __call__(self, example_text):
        out = self.replace_numbers_with_words(example_text)
        # out = self.accentizer.process_all(out)
        print(out)
        audio = self.tts(out)
        file_name = f"data/out-{str(uuid.uuid4())}.wav"
        self.tts.save_wav(audio, file_name)
        return file_name
    
    def replace_numbers_with_words(self, text):
        # Regular expression pattern to match numbers
        pattern = r'\d+'
        
        # Find all the numbers in the text using the pattern
        numbers = re.findall(pattern, text)
        
        # Replace each number with its word representation
        for number in numbers:
            word = num2words(int(number), lang='ru')
            text = text.replace(number, word)
        
        return text
