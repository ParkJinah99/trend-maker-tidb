import pymysql
from typing import Dict
import pandas as pd
from sqlalchemy import create_engine


class TiDBHandler:
    def __init__(self, credential: Dict):
        self._datbase = credential["database"]
        self._connection = pymysql.connect(
            host=credential["host"],
            port=credential["port"],
            user=credential["user"],
            password=credential["password"],
            database=credential["database"],
            ssl_verify_cert=True,
            ssl_verify_identity=True,
            ssl_ca=credential["ssl_ca"],
        )
        self.sqlalchemy_engine = (
            create_engine(
                "mysql+pymysql://3tEzqCzo4jQr7L3.root:vgKW3BLAis22k56Y@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true"
            ),
        )

    @property
    def connection(self):
        return self._connection

    def execute_query_as_dict(self, query: str, params: tuple = None) -> list:
        try:
            result_df = pd.read_sql(query, self._connection, params=params)
            if result_df.empty:
                return []
            return result_df.to_dict(orient="records")
        except Exception as e:
            raise Exception(f"Error executing query: {e}")
