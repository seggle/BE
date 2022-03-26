import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, log_loss, f1_score, mean_absolute_error,
    mean_squared_error, average_precision_score
)
import traceback

class EvaluationMixin(object):
    def evaluate(self, submission, problem):
        """
        submission: 
        problem: 
        evaluation: 평가 방식
        """
        try:
            solution_csv_path = problem.solution
            submission_csv_path = submission.csv
            evaluation = problem.evaluation

            solution_csv = pd.read_csv(solution_csv_path)
            submission_csv = pd.read_csv(submission_csv_path)

            score = None
            y_true = solution_csv.iloc[:, -1].values.tolist()
            y_pred = submission_csv.iloc[:, -1].values.tolist()

            if evaluation == "F1-score":
                """ 높을수록 1등
                expected: binary
                """
                score = f1_score(y_true, y_pred, pos_label=1)

            if evaluation == "RMSE":
                """ 낮을수록 1등
                expected: double
                """
                score = mean_squared_error(y_true, y_pred, squared=False) # squared=False: RMSE

            if evaluation == "mAP":
                score = average_precision_score(y_true, y_pred)

            if evaluation == "MSE":
                """ 낮을수록 1등
                expected: double
                """
                score = mean_squared_error(y_true, y_pred)

            if evaluation == "MAE":
                """ 낮을수록 1등
                expected: double
                """
                score = mean_absolute_error(y_true, y_pred)

            if evaluation == "Log loss":
                """ 낮을수록 1등
                expected: 
                """
                score = log_loss(y_true, y_pred)

            if evaluation == "Accuracy":
                """ 높을수록 1등
                expected: double, string
                """
                score = accuracy_score(y_true, y_pred)

            submission.score = score

        except: # 에러 발생
            print(traceback.format_exc())
            submission.score = None
            submission.status = 1 # 문제 있음

        submission.save()
        return