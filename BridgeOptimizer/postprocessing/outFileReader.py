class Out_file_reader:
    lines = []

    def __init__(self, path_out_file: str) -> None:
        with open(path_out_file) as file:
            for line in file:
                self.lines.append(line)
