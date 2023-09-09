from transformers import MBartTokenizer, MBartForConditionalGeneration


class QA:
    def __init__(self) -> None:
        model_name = "IlyaGusev/mbart_ru_sum_gazeta"
        self.tokenizer = MBartTokenizer.from_pretrained(model_name,)
        self.model = MBartForConditionalGeneration.from_pretrained(model_name)

    def __call__(self, text, smart=True) -> str:
        if not smart:
            return text
        input_ids = self.tokenizer(
            [text],
            max_length=600,
            padding="longest",
            truncation=True,
            return_tensors="pt",
        )["input_ids"]

        output_ids = self.model.generate(input_ids=input_ids, no_repeat_ngram_size=4)[0]

        summary = self.tokenizer.decode(output_ids, skip_special_tokens=True)

        return summary
    