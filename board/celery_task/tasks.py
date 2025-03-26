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

