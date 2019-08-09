import os
import json
import random
import unittest
import subprocess

from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase

from dffml_source_mysql.source import MysqlSourceConfig, MysqlSource

DROP_TABLE_QUERY = "DROP TABLE IF EXISTS `repo_data`;"
CREATE_TABLE_QUERY = """
CREATE TABLE `repo_data` (
  `src_url` varchar(100) NOT NULL,
  `feature_PetalLength` float DEFAULT NULL,
  `feature_PetalWidth` float DEFAULT NULL,
  `feature_SepalLength` float DEFAULT NULL,
  `feature_SepalWidth` float DEFAULT NULL,
  `prediction_confidence` float DEFAULT NULL,
  `prediction_value` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`src_url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


class TestMySQLSource(SourceTest, AsyncTestCase):
    async def setUp(self):
        self.container_name = str(random.random()).replace('.', '')
        subprocess.check_output(["docker", "run", "--rm", "-d", "--name",
            self.container_name,
            "-e", "MYSQL_RANDOM_ROOT_PASSWORD=yes",
            "-e", "MYSQL_USER=user",
            "-e", "MYSQL_PASSWORD=pass",
            "-e", "MYSQL_DATABASE=db",
            "mariadb"])
        info = json.loads(subprocess.check_output(["docker", "inspect",
            self.container_name]))[0]
        container_ip = info["NetworkSettings"]["IPAddress"]
        self.source_config = MysqlSourceConfig(
            host=container_ip,
            port=3306,
            user="user",
            password="pass",
            db="db",
            repo_query="select * from repo_data where src_url=%s",
            update_query="""insert into repo_data (`src_url`, `feature_PetalLength`, `feature_PetalWidth`, `feature_SepalLength`, `feature_SepalWidth`, `prediction_confidence`, `prediction_value`) values (%s,%s,%s,%s,%s,%s,%s) on duplicate key update src_url=%s, feature_PetalLength=%s, feature_PetalWidth=%s, feature_SepalLength=%s, feature_SepalWidth=%s, prediction_confidence=%s, prediction_value=%s""",
            repos_query="select * from repo_data",
            model_columns="src_url feature_PetalLength feature_PetalWidth feature_SepalLength feature_SepalWidth prediction_confidence prediction_value",
        )
        async with (await self.setUpSource()) as source:
            async with source() as sctx:
                await sctx.conn.execute(DROP_TABLE_QUERY)
                await sctx.conn.execute(CREATE_TABLE_QUERY)

    async def tearDown(self):
        subprocess.check_output(["docker", "stop", self.container_name])

    async def setUpSource(self):
        return MysqlSource(self.source_config)

    @unittest.skip("Labels not implemented")
    async def test_label(self):
        """
        Labels not implemented
        """
