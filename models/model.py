import contextlib
from db.config import Database
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
        if len(sql_injections) > 0:
            print("SQL injections detected:")
            for statement in sql_injections:
                print(statement)
            return 1, sql_injections  # Return both flag and list of SQL injection payloads
        else:
            print("No SQL injections detected.")
            return 0, []  # No SQL injections detected, return 0 and empty list




