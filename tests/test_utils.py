from xmldiff import main


def check_identical_contents(file1, file2):
    with open(file1, "r", encoding="utf8") as f1:
        f1_contents = f1.read()

    with open(file2, "r", encoding="utf8") as f2:
        f2_contents = f2.read()

    # Just parse the files to avoid any issues with inconsistent whitespace
    if file1.suffix in (".ttml", ".dfxp"):
        return len(main.diff_files(file1, file2)) == 0

    return f1_contents == f2_contents
