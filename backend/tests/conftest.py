import sys
import types

# Stub requests if not installed
if 'requests' not in sys.modules:
    requests_stub = types.ModuleType('requests')

    class MockResponse:
        def __init__(self):
            self.content = b''
            self.status_code = 200
        def raise_for_status(self):
            pass
        def json(self):
            return {}

    def get(*args, **kwargs):
        return MockResponse()

    requests_stub.get = get
    requests_stub.exceptions = types.SimpleNamespace(RequestException=Exception)
    sys.modules['requests'] = requests_stub

# Stub BeautifulSoup if bs4 is missing
if 'bs4' not in sys.modules:
    bs4_stub = types.ModuleType('bs4')
    import re

    class Element:
        def __init__(self, html: str):
            self.html = html

        def get_text(self, strip: bool = False):
            text = re.sub(r'<[^>]+>', '', self.html)
            return text.strip() if strip else text

        def get(self, attr: str):
            match = re.search(fr'{attr}="([^"]*)"', self.html)
            return match.group(1) if match else None

    class BeautifulSoup(Element):
        def __init__(self, html: str, parser: str = "html.parser"):
            super().__init__(html)

        def select(self, selector: str, limit: int | None = None):
            if selector == "div.news-release-item":
                pattern = re.compile(
                    r'<div class="news-release-item">(.*?)</div>\s*</div>',
                    re.DOTALL,
                )
                matches = [m.group(0) for m in pattern.finditer(self.html)]
                if not matches:
                    pattern = re.compile(
                        r'<div class="news-release-item">(.*?</div>)', re.DOTALL
                    )
                    matches = [m.group(0) for m in pattern.finditer(self.html)]
                if limit:
                    matches = matches[:limit]
                return [BeautifulSoup(m) for m in matches]
            return []

        def find(self, tag: str, class_: str | None = None):
            if tag == "div" and class_ == "news-release-date":
                m = re.search(r'<div class="news-release-date">(.*?)</div>', self.html, re.DOTALL)
                return BeautifulSoup(m.group(0)) if m else None
            return None

        def select_one(self, selector: str):
            if selector == "h4 > a":
                m = re.search(r'<h4><a href="([^"]+)">(.*?)</a></h4>', self.html, re.DOTALL)
                return BeautifulSoup(m.group(0)) if m else None
            return None

    bs4_stub.BeautifulSoup = BeautifulSoup
    sys.modules['bs4'] = bs4_stub

# Stub feedparser if not installed
if 'feedparser' not in sys.modules:
    feedparser_stub = types.ModuleType('feedparser')

    def parse(*args, **kwargs):
        return types.SimpleNamespace(bozo=False, feed={}, entries=[])

    feedparser_stub.parse = parse
    sys.modules['feedparser'] = feedparser_stub

# Stub dotenv if not installed
if 'dotenv' not in sys.modules:
    dotenv_stub = types.ModuleType('dotenv')
    def load_dotenv(*args, **kwargs):
        pass
    dotenv_stub.load_dotenv = load_dotenv
    sys.modules['dotenv'] = dotenv_stub

# Stub schedule if not installed
if 'schedule' not in sys.modules:
    schedule_stub = types.ModuleType('schedule')
    class Every:
        def __getattr__(self, name):
            return self
        def at(self, *args, **kwargs):
            return self
        def do(self, *args, **kwargs):
            return self
    schedule_stub.every = lambda: Every()
    schedule_stub.clear = lambda: None
    schedule_stub.run_pending = lambda: None
    schedule_stub.jobs = []
    sys.modules['schedule'] = schedule_stub

# Stub fastapi if not installed to allow importing main module
if 'fastapi' not in sys.modules:
    fastapi_stub = types.ModuleType('fastapi')

    class HTTPException(Exception):
        def __init__(self, status_code: int = 500, detail: str | None = None):
            self.status_code = status_code
            self.detail = detail

    class BackgroundTasks:
        def add_task(self, func, *args, **kwargs):
            pass

    class Request:
        def __init__(self):
            self.headers = {}

    class FastAPI:
        def __init__(self, *args, **kwargs):
            pass

        def add_middleware(self, *args, **kwargs):
            pass

        def middleware(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

        def on_event(self, event):
            def decorator(func):
                return func
            return decorator

    def Depends(x):
        return x

    fastapi_stub.FastAPI = FastAPI
    fastapi_stub.HTTPException = HTTPException
    fastapi_stub.BackgroundTasks = BackgroundTasks
    fastapi_stub.Request = Request
    fastapi_stub.Depends = Depends

    responses = types.ModuleType('fastapi.responses')
    responses.JSONResponse = object
    fastapi_stub.responses = responses
    sys.modules['fastapi.responses'] = responses

    middleware = types.ModuleType('fastapi.middleware')
    cors = types.ModuleType('fastapi.middleware.cors')
    cors.CORSMiddleware = object
    middleware.cors = cors
    fastapi_stub.middleware = middleware
    sys.modules['fastapi.middleware'] = middleware
    sys.modules['fastapi.middleware.cors'] = cors

    security = types.ModuleType('fastapi.security')
    security.OAuth2PasswordBearer = lambda *args, **kwargs: None
    class OAuth2PasswordRequestForm:
        pass
    security.OAuth2PasswordRequestForm = OAuth2PasswordRequestForm
    fastapi_stub.security = security
    sys.modules['fastapi.security'] = security

    sys.modules['fastapi'] = fastapi_stub

# Stub pydantic_settings if not installed
if 'pydantic_settings' not in sys.modules:
    ps_stub = types.ModuleType('pydantic_settings')

    class BaseSettings:
        model_config: dict | None = None

    SettingsConfigDict = dict

    ps_stub.BaseSettings = BaseSettings
    ps_stub.SettingsConfigDict = SettingsConfigDict
    sys.modules['pydantic_settings'] = ps_stub

# Stub openai if not installed
if 'openai' not in sys.modules:
    openai_stub = types.ModuleType('openai')

    class OpenAI:
        def __getattr__(self, name):
            return None

    openai_stub.OpenAI = OpenAI
    sys.modules['openai'] = openai_stub

# Stub bcrypt if not installed
if 'bcrypt' not in sys.modules:
    bcrypt_stub = types.ModuleType('bcrypt')
    bcrypt_stub.hashpw = lambda p, s: b''
    bcrypt_stub.gensalt = lambda *args, **kwargs: b''
    bcrypt_stub.checkpw = lambda p, h: True
    sys.modules['bcrypt'] = bcrypt_stub

# Stub jwt if not installed
if 'jwt' not in sys.modules:
    jwt_stub = types.ModuleType('jwt')
    jwt_stub.encode = lambda *args, **kwargs: ''
    jwt_stub.decode = lambda *args, **kwargs: {}
    class PyJWTError(Exception):
        pass
    jwt_stub.PyJWTError = PyJWTError
    sys.modules['jwt'] = jwt_stub

# Stub passlib if not installed
if 'passlib.context' not in sys.modules:
    passlib_context_stub = types.ModuleType('passlib.context')
    class CryptContext:
        def __init__(self, *args, **kwargs):
            pass
        def verify(self, password, hashed):
            return True
        def hash(self, password):
            return 'hash'
    passlib_context_stub.CryptContext = CryptContext
    sys.modules['passlib.context'] = passlib_context_stub
