from fastapi import FastAPI
from routes.Users import users_root
from routes.login import login_root
from routes.logout import logout_root
from routes.signup import signupRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://192.168.29.147:3000",  # replace with your own ipv4 address:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_root)
app.include_router(users_root)
app.include_router(logout_root)
app.include_router(signupRouter)
