import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, log_loss, f1_score, mean_absolute_error,
    mean_squared_error
)
class EvaluationMixin(object):

    # path - socre, status
    # solution_csv - problem의 solution 파일
    # submission_csv - 학생의 csv 파일
    # evaluation - problem의 평가 방식
    def evaluate(self, path, solution_csv, submission_csv, evaluation):
        try:
            solution = pd.read_csv(solution_csv)
            submission = pd.read_csv(submission_csv)

            score = None
            y_true = solution.iloc[:, -1].values.tolist()
            y_pred = submission.iloc[:, -1].values.tolist()

            if evaluation == "F1-score":
                score = f1_score(y_true, y_pred, pos_label=1) # 높을수록 1등

            if evaluation == "RMSE": # 낮을수록 1등
                score = np.sqrt(mean_squared_error(y_true, y_pred))

            if evaluation == "mAP":
                path.score = 1

            if evaluation == "MSE":
                score = mean_squared_error(y_true, y_pred) # 낮을수록 1등

            if evaluation == "MAE":
                score = mean_absolute_error(y_true, y_pred) # 낮을수록 1등

            if evaluation == "Log loss":
                score = log_loss(y_true, y_pred) # 낮을수록 1등

            if evaluation == "Accuracy":
                score = accuracy_score(y_true, y_pred) # 높을수록 1등

            path.score = score

        except: # 에러 발생
            path.score = None
            path.status = 1 # 문제 있음

        path.save()