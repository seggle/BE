# msg_view이름_함수_s or _e
# ex) msg_ListUsers_get_s = {"success":"성공했습니다"}
# ex) msg_ListUsers_get_e = {"error":"처리에 실패했습니다"}

msg_success = {"code": 200, "success": "성공했습니다"}
msg_success_create = {"code": 201, "message": "성공했습니다"}
msg_success_delete = {"code": 200, "message": "성공적으로 삭제했습니다."}
msg_error = {"error": "실패"}
msg_error_id = {"error": "올바르지 않은 URL 입니다."}
msg_error_diff_user = {"code": 403, "error": "작성자만 수정/삭제 가능합니다."}
msg_time_error = {'code': 400, 'message': '제한된 시간입니다.'}
msg_user_model_username_unique = {'unique': '중복된 ID 입니다.'}
msg_user_model_email_unique = {'unique': '중복된 email 입니다.'}
msg_problem_model_title_unique = {'unique': '중복된 제목 입니다.'}
msg_error_no_selection = {"code": 400, "message": "대상을 선택해 주세요."}
msg_error_url = {"code": 400, "message": "잘못된 URL 입니다."}
msg_notfound = {"code": 404, "message": "콘텐츠를 찾을 수 없습니다."}
msg_error_no_permission = {'code': 400, 'message': '권한이 없습니다.'}
msg_error_no_request = {'code': 400, 'message': '바꿀 항목을 입력해 주세요.'}

msg_success_check_public = {'code': 200, 'message': '성공적으로 공개로 바꾸었습니다.'}
msg_success_check_private = {'code': 200, 'message': '성공적으로 비공개로 바꾸었습니다.'}

# account
msg_password_is_not_match = {'code': 400, 'message': '비밀번호가 일치하지 않습니다.'}
msg_success_delete_user = {'code': 200, 'message': '회원 탈퇴 성공'}
msg_error_delete_user = {'code': 400, 'message': '이미 탈퇴 되었습니다.'}
msg_error_new_password_is_not_match = {'code': 400, 'message': '새로운 비밀번호가 일치하지 않습니다.'}
msg_error_current_password_is_not_correct = {'code': 400, 'message': '현재 비밀번호가 일치하지 않습니다.'}
msg_error_no_permission_user = {"code": 403, "message": "접근 권한이 없습니다."}
msg_error_not_in_class = {"code": 400, "message": "해당 수업에 속해있지 않습니다."}
# announcement

# classes

msg_error_invalid_contest = {'code': 400, 'message': '잘못된 contest입니다.'}

# competition

msg_error_invalid_user = {'code': 400, 'message': '잘못된 사용자입니다.'}
msg_success_participation = {'code': 201, 'message': '대회에 참여 처리되었습니다.'}
msg_error_participation = {'code': 400, 'message': '참여 처리 중 오류가 발생했습니다.'}
msg_error_already_participated = {'code': 400, 'message': '이미 참가한 대회입니다.'}
msg_success_delete_competition = {'code': 200, 'message': "대회가 정상적으로 삭제되었습니다."}
msg_error_already_deleted = {'code': 404, 'message': '이미 삭제된 대회입니다.'}

msg_error_invalid_id = {'code': 400, 'message': 'id가 없거나 유효한 id가 아닙니다.'}
msg_error_invalid_order = {'code': 400, 'message': 'order가 없거나 유효한 order가 아닙니다.'}
msg_error_invalid_url = {'code': 400, 'message': '유효한 URL이 아닙니다.'}
msg_success_patch_order = {'code': 200, 'message': 'order를 성공적으로 바꿨습니다.'}

msg_error_invalid_problem = {'code': 400, 'message': '잘못된 메시지 요청입니다.'}
msg_error_wrong_problem = {'code': 500, 'message': '잘못된 문제 유형입니다.'}
msg_error_problem_not_found = {'code': 404, 'message': '없는 문제입니다.'}
msg_error_user_not_found = {"code": 404, "message": "없는 사용자입니다."}

# contest

# exam
msg_ExamParticipateView_get_e_1 = {"error": "해당 class의 교수 또는 TA가 아닙니다."}
msg_ExamParticipateView_get_e_2 = {"error": "해당 class에 속하지 않습니다."}

# faq

# leaderboard
msg_error_no_on_leaderboard_submission = {'code': 400, "message": "리더보드에 공개된 제출이 없습니다."}

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
msg_SubmissionCheckView_patch_e_1 = {'code': 400, 'error': '타인의 제출물입니다.'}
msg_SubmissionClassView_post_e_1 = {'code': 400, "message": "올바른 csv 파일을 업로드 해주세요."}
msg_SubmissionClassView_post_e_2 = {'code': 400, "message": "올바른 ipynb 파일을 업로드 해주세요."}
msg_SubmissionClassView_post_e_3 = {'code': 400, "message": "ip가 중복입니다"}
msg_SubmissionCompetitionView_post_e_1 = {'code': 403, 'message': "대회에 참가하지 않았습니다."}

msg_error_no_download_option = {"code": 400, "message": "다운로드 옵션을 명시해 주세요."}
# uploads

