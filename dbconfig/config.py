import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "Fitness-pro1")
    MYSQL_HOST = "fitness-pro.cdga22ekaxjl.us-east-2.rds.amazonaws.com"
    MYSQL_PORT = 3306
    MYSQL_USER = "admin"
    MYSQL_PASSWORD = "Fitness-pro1"
    MYSQL_DB = "fitness_pro"
