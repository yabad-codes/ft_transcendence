import logging
import sys

bind = "0.0.0.0:8000"
workers = 4

# Paths to log files
accesslog = "/app/logs/access.log"
errorlog = "/app/logs/error.log"

# Logging level
loglevel = "info"

logging.basicConfig(
	level=loglevel.upper(),
	format="%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
 	handlers=[
		logging.FileHandler(errorlog),
		logging.StreamHandler(sys.stdout)
	]
)