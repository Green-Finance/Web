from.worker import board_celery
import requests

@board_celery.task
def notify_django_about_post(post_data: dict):
    try:
        # 예: Django 컨테이너 이름이 account일 경우
        response = requests.post("http://account:8000/api/profile/v1/sync/", json=post_data)
        return response.status_code
    except Exception as e:
        return (str(e))

@board_celery.task
def notify_django_about_post_update(post_id:int, post_data: dict):
    try:
        # 예: Django 컨테이너 이름이 account일 경우
        response = requests.put(f"http://account:8000/api/profile/v1/sync/update/{post_id}/", json=post_data)
        return response.status_code
    except Exception as e:
        return str(e)


@board_celery.task
def notify_django_about_post_delete(post_id: int):
    try:
        response = requests.delete(f"http://account:8000/api/profile/v1/sync/delete/{post_id}/")
        return response.status_code
    except Exception as e:
        return str(e)


@board_celery.task
def notify_django_about_board_like(board_id: int, user_id: int, action: str):
    try:
        response = requests.post(
            f"http://account:8000/api/profile/v1/sync/{board_id}/board_like/",
            json={"user_id": user_id, "action": action}
        )
        return response.status_code
    except Exception as e:
        return str(e)

@board_celery.task
def notify_django_about_comment(comment_data: dict):
    """
    FastAPI에서 생성된 댓글 데이터를 Django로 동기화하는 Task.
    comment_data 예시:
    {
        "user_id": 1,
        "board_id": 3,
        "content": "댓글 내용입니다.",
        "created_at": "2025-03-26T06:58:08.775688",
        "updated_at": "2025-03-26T06:58:08.775688"
    }
    """
    try:
        response = requests.post(
            "http://account:8000/api/profile/v1/sync/comment/",
            json=comment_data
        )
        return response.status_code
    except Exception as e:
        return str(e)


@board_celery.task
def notify_django_about_comment_update(comment_id: int, comment_data: dict):
    try:
        response = requests.put(
            f"http://account:8000/api/profile/v1/sync/comment/update/{comment_id}/",  # Django 업데이트 API URL
            json=comment_data
        )
        return response.status_code
    except Exception as e:
        return str(e)

@board_celery.task
def notify_django_about_comment_delete(comment_id: int):
    try:
        response = requests.delete(
            f"http://account:8000/api/profile/v1/sync/comment/delete/{comment_id}/"  # Django 삭제 API URL
        )
        return response.status_code
    except Exception as e:
        return str(e)