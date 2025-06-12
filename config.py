import os
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'default-secret-key-for-dev'
    MONGO_URI = f"mongodb://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@mongodb:27017/"
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    # Production specific settings
    pass

class TestingConfig(Config):
    TESTING = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}