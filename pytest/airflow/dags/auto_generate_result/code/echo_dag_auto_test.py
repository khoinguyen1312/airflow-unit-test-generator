
import unittest

from momo.test.tester.bash_operator_test_helper import BaseOperatorTester


class echo_dag(BaseOperatorTester):
  def test_dag_should_exist(self):
    self.should_exists_dag(
        id="echo_dag",
        tasks=
          {
            "echo_something": {
              "content":
                "echo Momo has a weird Data Platform", 

              "upstream": {}
            }, 

            "sql_something": {
              "content":
                "sql \"SELECT 'Momo has a weird Data Platform'\"\"", 

              "upstream": {
                "echo_something"
              }
            }
          }
    )


if __name__ == '__main__':
  unittest.main()

        