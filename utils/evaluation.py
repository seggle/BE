import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, log_loss, f1_score, mean_absolute_error,
    mean_squared_error, average_precision_score,
    mean_squared_log_error
)
import traceback

class EvaluationMixin(object):
    def evaluate(self, submission, problem):
        """
        submission:
        problem:
        evaluation: ["CategorizationAccuracy", "RMSE", "MAE", "MSE", "F1-score", "Log-loss", "RMSLE", "mAP"]
        """
        try:
            # 낮은 순 리스트: ["CategorizationAccuracy", "F1-score", "mAP"]
            solution_csv_path = problem.solution
            submission_csv_path = submission.csv
            evaluation = problem.evaluation

            solution_csv = pd.read_csv(solution_csv_path)
            submission_csv = pd.read_csv(submission_csv_path)

            score = None
            y_true = solution_csv.iloc[:, -1].values.tolist()
            y_pred = submission_csv.iloc[:, -1].values.tolist()
            if evaluation == "CategorizationAccuracy":
                """ Categorization Accuracy
                높을수록 1등
                expected: double, string
                checked
                """
                score = accuracy_score(y_true, y_pred)
            elif evaluation == "RMSE":
                """ Root Mean Squared Error
                낮을수록 1등
                expected: double
                checked
                """
                score = mean_squared_error(y_true, y_pred, squared=False)
            elif evaluation == "MAE":
                """ Mean Absolute Error
                낮을수록 1등
                expected: double
                checked
                """
                score = mean_absolute_error(y_true, y_pred)
            elif evaluation == "MSE":
                """ Mean Squared Error
                낮을수록 1등
                expected: double
                checked
                """
                score = mean_squared_error(y_true, y_pred)
            elif evaluation == "F1-score":
                """ 높을수록 1등
                expected: binary
                checked
                """
                score = f1_score(y_true, y_pred, pos_label=1)
            elif evaluation == "Log-loss":
                """ Log Loss
                낮을수록 1등
                expected: double
                checked
                """
                score = log_loss(y_true, y_pred)
            elif evaluation == "RMSLE":
                """ Root Mean Squared Logarithmic Error
                낮을수록 1등
                expected: double
                checked
                """
                score = mean_squared_log_error(y_true, y_pred)
            elif evaluation == "mAP":
                """ MAP
                높을수록 1등
                expected: string
                checked
                """
                score = average_precision_score(y_true, y_pred)
            else:
                submission.score = None
                submission.status = 1 # 문제 있음
                submission.save()
                print(f'evaluation: {evaluation}')
                return
            submission.score = score

        except: # 에러 발생
            print(traceback.format_exc())
            print(f'evaluation: {evaluation}')
            submission.score = None
            submission.status = 1 # 문제 있음

        submission.save()
        return