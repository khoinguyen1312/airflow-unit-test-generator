"""
This script is the first version of Airflow Unit Test Generator, it's self present ideas only.
If you are considering using this script for your production, you should use the latest version instead.

See README.md
"""



import subprocess
from subprocess import DEVNULL

import click


@click.command()
@click.option('--dag', help='Dag Name.')
@click.option('--output_file', help='Output file. If empty, output file will be Dag Name.')
def main(dag: str, output_file: str):
  """
  This script help you to run airflow and render tasks's bash operator into text file which can use for comparing.
  This script need airflow have already been installed on your system to be able to run.
  Or you can copy this script to Airflow's Container for running

  How to use:
  Ex:
  `python airflow_test.py --dag=echo_something --output_file=output_file`
  `python airflow_test.py --dag=echo_something.sub_dag_name --output_file=output_file`
  """

  output, msg = subprocess.getstatusoutput('command -v airflow')

  if output != 0:
    print("You have to install Airflow first")
    return

  if not dag:
    print("Please enter Dag name")
    return

  if output_file == None:
    output_file = dag

  test_runner = AirflowBashResultGenerator(dag, output_file, '2019-06-06T19:00:00.000000+00:00')
  test_runner.run_test()


class AirflowBashResultGenerator:
  """Help to generate bash result from airflow's Bash Operator
  """

  def __init__(self,
      dag: str,
      output_file: str,
      time: str
  ):
    """Initialize Airflow Bash Result Generator

    Args:
      dag: DAG's name
      output_file: output file
      time: time in string timezone format
        YYYY-MM-DDTHH:mm:ss.000000+Z
    """
    self.dag=dag
    self.output_file=output_file
    self.time=time

  def run_test(self):
    """Run airflow to get list of tasks for provided DAG name and render these tasks into output file
    """

    with open(self.output_file, 'w') as file:
      tasks = self._get_tasks()
      print(f"{len(tasks)} tasks")
      for i in range(0, len(tasks)):
        task = tasks[i]
        print(f"{i + 1}/{len(tasks)} {task}")

        airflow_render_command=self._build_airflow_render_command(task)

        output = self._run_shell_command(airflow_render_command)

        splitted: [] = output.split("# ----------------------------------------------------------")

        generated_bash_command = splitted[2]

        file.writelines([
          f"------------------------------------------------ \n"
          f"{task} \n"
          f"\n"
          f"{generated_bash_command} \n"
        ])

  def _get_tasks(self) -> []:
    output = self._run_shell_command(['airflow', 'list_tasks', self.dag])

    splitted: [] = output.splitlines()

    i = len(splitted) - 1

    while (i >= 0):
      if (not splitted[i].startswith('[')):
        break
      i = i - 1

    tasks = []

    while (not splitted[i].startswith('[')):
      tasks.append(splitted[i])
      i = i - 1

    tasks.reverse()

    return tasks

  def _build_airflow_render_command(self, task_name: str) -> []:
    return ['airflow', 'render', self.dag, task_name, self.time]

  def _run_shell_command(self,
      commands: []
  ) -> str:
    output: str = subprocess.check_output(commands, stderr=DEVNULL);

    return output.decode("ASCII")


if __name__ == '__main__':
    main()