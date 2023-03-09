def check_identical_vtt_files(file1, file2):
    with open(file1, "r", encoding="utf8") as f1:
        file1_contents = f1.read()

    with open(file2, "r", encoding="utf8") as f2:
        file2_contents = f2.read()

    return file1_contents == file2_contents
