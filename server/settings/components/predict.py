from decouple import config as c

 
# Replicate service setup
INCORRECT_ARTICLE_LENGTH = c("INCORRECT_ARTICLE_LENGTH", cast=int, default=150)