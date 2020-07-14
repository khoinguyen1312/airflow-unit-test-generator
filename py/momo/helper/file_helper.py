class FileHelper:
  @staticmethod
  def read_file(path):
    return open(path, "r").read()
