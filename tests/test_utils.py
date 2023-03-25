def check_identical_contents(file1, file2):
    with open(file1, "r", encoding="utf8") as f1:
        f1_contents = f1.read()

    with open(file2, "r", encoding="utf8") as f2:
        f2_contents = f2.read()

    return f1_contents == f2_contents
