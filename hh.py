import os

def merge_py_to_markdown(root_dir=None, output_filename="all_code.md"):
    """
    合并指定目录及其子目录下的所有 .py 文件为一个 Markdown 文件。
    忽略 test 文件夹及其子目录。
    每个文件会带有路径标识，并以 Markdown 代码块格式包裹。
    """

    if root_dir is None:
        root_dir = os.getcwd()

    output_file = os.path.join(root_dir, output_filename)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# 合并的 Python 代码文件\n\n")

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # 过滤掉 test 目录
            if "test" in dirpath.split(os.sep):
                continue

            for file in filenames:
                if file.endswith(".py"):
                    filepath = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(filepath, root_dir)

                    # 跳过输出文件自身
                    if os.path.abspath(filepath) == os.path.abspath(output_file):
                        continue

                    out.write(f"# 文件路径: {rel_path}\n")
                    out.write("```python\n")
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"# 无法读取文件: {e}\n")
                    out.write("\n```\n\n---\n\n")

    print(f"✅ 所有 .py 文件内容已合并到: {output_file}")


if __name__ == "__main__":
    merge_py_to_markdown()
