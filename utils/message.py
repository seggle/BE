# msg_view이름_함수_s or _e
# ex) msg_ListUsers_get_s = {"success":"성공했습니다"}
# ex) msg_ListUsers_get_e = {"error":"처리에 실패했습니다"}

msg_success = {"success":"성공했습니다"}
msg_success_create = {"code": 201, "message": "성공했습니다"}
msg_success_delete = {"code": 204, "message": "성공했습니다"}
msg_error = {"error": "실패"}
msg_error_id = {"error": "올바르지 않은 URL 입니다."}
msg_error_diff_user = {"error": "작성자만 수정/삭제 가능합니다."}
msg_time_error = {'error': '제한된 시간입니다.'}
msg_user_model_username_unique = {'unique': '중복된 ID 입니다.'}
msg_user_model_email_unique = {'unique': '중복된 email 입니다.'}
msg_problem_model_title_unique = {'unique': '중복된 제목 입니다.'}
msg_error_no_selection = {"code": 400, "message": "대상을 선택해 주세요."}
msg_error_url = {"code": 400, "message": "잘못된 URL 입니다."}
msg_notfound = {"code": 404, "message": "콘텐츠를 찾을 수 없습니다."}

# account

# announcement

# classes



# competition

# contest

# exam
msg_ExamParticipateView_get_e_1 = {"error": "해당 class의 교수 또는 TA가 아닙니다."}
msg_ExamParticipateView_get_e_2 = {"error": "해당 class에 속하지 않습니다."}

# faq

# leaderboard

# password

# problem
msg_ProblemDetailView_delete_e_1 = {"success": "문제가 제거되었습니다."}
msg_ProblemDetailView_delete_e_2 = {"code": 204, "message": "이미 삭제된 문제입니다."}
msg_ProblemView_post_e_1 = {"code": 400, "message": "파일을 업로드 해주세요."}
msg_ProblemView_post_e_2 = {"code": 400, "message": "올바른 데이터 파일을 업로드 해주세요."}
msg_ProblemView_post_e_3 = {"code": 400, "message": "올바른 정답 파일을 업로드 해주세요."}

# proposal

# seggle

# submission
msg_SubmissionCheckView_patch_e_1 = {"error": "username"}
msg_SubmissionClassView_post_e_1 = {"error": "올바른 csv 파일을 업로드 해주세요."}
msg_SubmissionClassView_post_e_2 = {"error": "올바른 ipynb 파일을 업로드 해주세요."}
msg_SubmissionClassView_post_e_3 = {"error": "ip가 중복입니다"}
msg_SubmissionCompetitionView_post_e_1 = {'error': "대회에 참가하지 않았습니다."}

msg_error_no_download_option = {"code": 400, "message": "다운로드 옵션을 명시해 주세요."}
# uploads

