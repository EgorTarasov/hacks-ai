import pandas as pd
import pickle
from ml.pipe import Pipe
from ml.audio.wer import wer


def accuracy(train_df, test_df, embeds):
    valid = pd.read_csv(test_df)
    df = pd.read_csv(train_df, sep=";")
    embeds = pickle.load(open(embeds, mode="rb"))

    pipe = Pipe(df, embeds)

    corr = 0
    for i, q in enumerate(valid[["question", "train_name", "problem"]].itertuples()):
        idx = pipe.predict_top_k(q.question, q.train_name.split(",")[0], False)[0][
            "uniq_id"
        ]
        if df.loc[idx, "problem"] == q.problem:
            corr += 1

    return corr / len(valid)


if __name__ == "__main__":
    acc_metric = accuracy("ml/train.csv", "ml/val.csv", "ml/embeds.pkl")
    wer_metric = wer("ml/audio/t3.csv", "ml/audio/t3_clean_for_stt/", "cuda")

    print(f"Accuracy: {acc_metric}\nWER: {wer_metric}")
