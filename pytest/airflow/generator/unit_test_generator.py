
import json
import os
import pathlib

import click
from airflow import DAG
from airflow.models import DagBag, BaseOperator
from airflow.operators.bash_operator import BashOperator

import textwrap

@click.command()
@click.option('--dag_folder', help='Location of DAG folder')
@click.option('--output_folder', help='Location of output file')

def main(dag_folder: str, output_folder: str):
  """
  """
  UnitTestGenerator(
      dag_folder=dag_folder,
      output_folder=output_folder
  ).run()

class UnitTestGenerator:
  """Help to generate bash result from airflow's Bash Operator

  """
  def __init__(self,
      dag_folder: str,
      output_folder: str
  ):
    """
    """
    self.dag_bag: DagBag = DagBag(dag_folder=dag_folder, include_examples=False)
    self.output_folder = output_folder

  def run(self):
    dag_bash_results = self._generate_expected_result()

    for dag_id, dag_result in dag_bash_results.items():
      dag_file_location = dag_result["file_path"]
      dag_task_dict = dag_result["task_dict"]

      pretty_class_name = dag_id.replace(".", "_").replace("-", "_")

      pretty_result = json.dumps(dag_task_dict, indent=2, sort_keys=True, separators=(", \n", ": "))

      result_content_space_indent = " " * 6

      pretty_result = pretty_result.replace("\\n", f"\\n\"\n{result_content_space_indent}\"")
      pretty_result = pretty_result.replace("\": \"", f"\":\n{result_content_space_indent}\"")
      pretty_result = pretty_result.replace(": 0", "")

      pretty_result = textwrap.indent(pretty_result, " " * 10)

      pytest_file_result= f"""
import unittest

from momo.test.tester.bash_operator_test_helper import BaseOperatorTester


class {pretty_class_name}(BaseOperatorTester):
  def test_dag_should_exist(self):
    self.should_exists_dag(
        id="{dag_id}",
        tasks=
{pretty_result}
    )


if __name__ == '__main__':
  unittest.main()

        """

      task_contain_folder = f"{self.output_folder}/{pathlib.Path(dag_file_location).parent}"
      file_location = f'{task_contain_folder}/{pretty_class_name}_auto_test.py'

      try:
        os.makedirs(task_contain_folder)
      except FileExistsError:
        pass

      with open(file_location, 'wt') as file:
        file.writelines([pytest_file_result])


  def _generate_expected_result(self):
    """Generate bash result for Airflow's DAG into dict

    Args:
      id: DAG's id

    Returns:
      dict of tasks with key is task's name and value is:
       - BashOperator'scommand if task is BashOperator
       - otherwise operator's class name
    """
    dag_bash_result = {}

    for dag_id, dag in self.dag_bag.dags.items():
      task_dict = {}

      for task_name, operator in dag.task_dict.items():
        baseOperator: BaseOperator = operator
        task_dict[task_name] = {}
        task_dict[task_name]["upstream"] = dict.fromkeys(baseOperator.upstream_task_ids, 0)
        if (isinstance(operator, BashOperator)):
          bashOperator: BashOperator = operator
          task_dict[task_name]["content"] = bashOperator.bash_command
        else:
          task_dict[task_name]["content"] = operator.__class__.__name__

      dag_bash_result[dag_id] = {
        "file_path": dag.filepath,
        "task_dict": task_dict
      }

    return dag_bash_result



if __name__ == '__main__':
  main()