from src.database.tidb_handler import TiDBHandler
from src.config import TIDB_CREDENTIAL


def init_tidb() -> TiDBHandler:
    return TiDBHandler(TIDB_CREDENTIAL)
