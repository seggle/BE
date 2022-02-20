import pandas as pd
class EvaluationMixin(object):

    # solution - problem의 solution 파일
    # submission - 학생의 csv 파일
    # evaluation - problem의 평가 방식
    def evaluate(path, solution_csv, submission_csv, evaluation):
        try:
            solution = pd.read_csv(solution_csv)
            submission = pd.read_csv(submission_csv)

            print("solution", solution)
            print("submission", submission)

            if evaluation == "F1-score":
                path.score = 0

            if evaluation == "RMSE":
                path.score = 0

            if evaluation == "mAP":
                path.score = 0

            if evaluation == "MSE":
                path.score = 0

            if evaluation == "MAE":
                path.score = 0

            if evaluation == "Log loss":
                path.score = 0

            if evaluation == "Accuracy":
                path.score = 0

        except: # 에러 발생
            path.score = None
            path.status = 1 # 문제 있음

        path.save()
