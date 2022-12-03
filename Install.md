# Configuration

## 개발 환경
* Python 3.11
* Django 4.1.3
* (테스트용) MariaDB 10.6.x
* Mozilla Firefox / Google Chrome
* Postman / Httpie

## 세팅

### secrets.json
settings.py 파일에 담기 어려운 키 등을 담는 파일로 SECRET_KEY 저장을 위해 필요

secret key는 그냥 파이썬 shell을 켜서 명령어로 얻을 수 있다.
```python3
import secrets
print(secrets.token_urlsafe())
```
출처: [TLDR: Generate Django Secret Key](https://humberto.io/blog/tldr-generate-django-secret-key/)

그런 다음 secrets.json을 루트에 만들고 다음과 같이 적어 준다.
```json
{
  "SECRET_KEY": "[생성한 secret key]",
  "EMAIL_HOST_USER": "asdf@asdf.com",
  "EMAIL_HOST_PASSWORD": "asdf"
}
```

### Database
실제 서버에서는 PostgreDB를 사용하나 소스 코드 상에서는 SQLite3를 사용하는 것으로 되어 있는데,
여기서는 [MariaDB](https://mariadb.org)를 사용했다.

루트에 dbconnetions.cnf를 추가하고 MariaDB에서 사용자와 데이터베이스를 생성한 다음 적어준다.

```ini
[client]
database = [설정한 데이터베이스]
user = [설정한 사용자명]
password = [설정한 비밀번호]
default-character-set = utf8
host = 127.0.0.1
port = 3306
```
그런 다음 settings.py에서 다음과 같은 내용으로 DB 설정을 바꿔준다. 주의할 점은 이 부분은 **절대** 커밋하면 안 된다.
```python3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': './dbconnection.cnf',
            'init_command': 'SET default_storage_engine=INNODB',
        }
    }
}
```

### Migration

마이그레이션을 해줘야 한다.

일단 venv가 적용된 콘솔에서 다음과 같은 명령어를 쳐서 migration 항목을 생성한다.
```shell
(venv) $ python manage.py makemigrations
```

이후 마이그레이션을 한다.
```shell
(venv) $ python manage.py migrate
```

### Superuser 계정 만들기

```shell
(venv) $ python manage.py createsuperuser
```

이후 나오는 설정을 잘 해주면 된다.