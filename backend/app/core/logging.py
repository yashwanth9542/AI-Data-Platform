import logging
import sys
from app.core.config import settings


logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), stream=sys.stdout, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("ai_data_platform")
