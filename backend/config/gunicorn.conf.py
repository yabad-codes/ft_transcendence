bind = "0.0.0.0:8000"
workers = 4

# Paths to log files
accesslog = "/app/logs/access.log"
errorlog = "/app/logs/error.log"
debuglog = "/app/logs/debug.log"

# Logging level
loglevel = "info"

# Additional logging configuration
import logging
import sys

logging.basicConfig(
	level=loglevel.upper(),
	format="%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
	handlers=[
		logging.FileHandler(debuglog),
		logging.StreamHandler(sys.stdout),
	]
)