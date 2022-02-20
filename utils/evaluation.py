import pandas as pd
class EvaluationMixin(object):

    # path - socre, status
    # solution_csv - problem의 solution 파일
    # submission_csv - 학생의 csv 파일
    # evaluation - problem의 평가 방식
    def evaluate(self, path, solution_csv, submission_csv, evaluation):
        try:
            solution = pd.read_csv(solution_csv)
            submission = pd.read_csv(submission_csv)

            print("solution", solution)
            print("submission", submission)

            if evaluation == "F1-score":
                path.score = 1

            if evaluation == "RMSE":
                path.score = 1

            if evaluation == "mAP":
                path.score = 1

            if evaluation == "MSE":
                path.score = 1

            if evaluation == "MAE":
                path.score = 1

            if evaluation == "Log loss":
                path.score = 1

            if evaluation == "Accuracy":
                path.score = 1

        except: # 에러 발생
            path.score = None
            path.status = 1 # 문제 있음

        path.save()