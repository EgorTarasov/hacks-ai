import pandas as pd
import string
import faster_whisper as whisper
import os
import torch

prompt = "УОИ, ТЭД, ТП, БВ, ГВ, АЗВ, БОДД, ПВДД, АБ, КЗ, ЭДТ, БСК, ПВСК, МВ, ОМ, ВВК, КМ, МПСУ, QF, ПТО, ЭПК, SA, СУ, ПС, БЦВ, RS, РУ, БУК, ПУ, QS, ВПР, РВ, QF, ИПЦУ, ВИП, ВУ, ПСН, ТНВД, QF, ВЦУ, QS, БВС, КДК, SF, МСУД, БПСН, САУ"


def wer(df_path, path_to_audio, device):
    data = pd.read_csv(df_path)

    def segments_to_text(segments):
        return " ".join([segment.text for segment in segments])

    def calculate_wer(test, predict):
        test_list = (
            test.translate(str.maketrans("", "", string.punctuation)).lower().split()
        )
        predict_list = (
            predict.translate(str.maketrans("", "", string.punctuation)).lower().split()
        )

        substitutions = sum(
            1 for ref, hyp in zip(test_list, predict_list) if ref != hyp
        )
        deletions = len(test_list) - len(predict_list)
        insertions = len(predict_list) - len(test_list)

        total = len(predict_list)

        wer = (substitutions + deletions + insertions) / total

        return wer

    def get_avg_wer(model, path_to_audio):
        wers = []

        for audio_file in os.listdir(path_to_audio):
            result, _ = model.transcribe(
                path_to_audio + audio_file,
                language="ru",
                initial_prompt=prompt,
            )

            pred_text = segments_to_text(result)
            true_text = data.iloc[int(audio_file[3:5])]["Неисправность"]

            wers.append(calculate_wer(true_text, pred_text))

        return sum(wers) / len(wers)

    model = whisper.WhisperModel("medium", device=device)

    return get_avg_wer(model, path_to_audio)
