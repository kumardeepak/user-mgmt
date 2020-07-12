DEBUG                               = True
API_URL_PREFIX                      = "/api"
APP_HOST                            = '0.0.0.0'
APP_PORT                            = 6000
FILE_STORAGE_PATH                   = '/Users/kd/Workspace/python/face/data/input'
ENABLE_CORS                         = True

JWT_SECRET_KEY                      = 'tarento@ai.com$'
JWT_ACCESS_TOKEN_EXPIRY_IN_MINS     = 5
JWT_REFRESH_TOKEN_EXPIRY_IN_DAYS    = 30

DATABASE_SAVE                       = True
DATABASE_URI                        = 'mongodb://localhost:27017'
DATABASE_NAME                       = 'tarento_ai'

REDIS_HOSTNAME                      = 'localhost'
REDIS_PORT                          = 6379

SUPPORTED_UPLOAD_FILETYPES          = ['application/msword',
'application/pdf',
'image/x-ms-bmp',
'image/jpeg',
'image/jpg',
'image/png',
'text/plain',
'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
'video/mp4',
'video/webm']