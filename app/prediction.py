import joblib

pipe_lr = joblib.load(open("./models/emotion_classifier_pipe_lr.pkl", "rb"))
#pipe_lr = joblib.load(open("../models/emotion_classifier_pipe_lr.pkl", "rb"))


def predict_emotions(text):
    return pipe_lr.predict([text])[0]

def get_prediction_proba(text):
    prob_values = pipe_lr.predict_proba([text]).tolist()
    print('prob values', prob_values)
    labels = [
        "anger",
        "disgust",
        "fear",
        "joy",
        "natural",
        "sadness",
        "shame",
        "surprise"
    ]
    prob_dict = {
        label: prob for label,
        prob in zip(labels, prob_values[0])
    }
    print(prob_dict)
    return prob_dict