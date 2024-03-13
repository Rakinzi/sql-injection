import contextlib

from joblib import load



class Model:
    def __init__(self):
        self.model = load(filename='models/sqli_injection-logistic-reg-v-1-0-0.joblib')
        self.vectorizer = load(filename='models/sqli_injection-vectorizer-v-1-0-0.joblib')

    def make_predictions(self, inputs):
        sql_injections = []
        model = self.model
        vectorizer = self.vectorizer
        for input in inputs:
            vectorized_inputs = vectorizer.transform([input])
            if model.predict(vectorized_inputs) == '1':
                sql_injections.append(input)
                if len(sql_injections) == 0:
                    print("No sql injections detected")
                    return 0
                else:
                    print("Sql injections detected")
                    print(sql_injections)
                    return 1
