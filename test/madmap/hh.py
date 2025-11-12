import os
import re
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLabel, QWidget, QFileDialog,
                             QMessageBox, QCheckBox, QGroupBox, QScrollArea, QRadioButton,
                             QButtonGroup)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont


class CodeProcessorThread(QThread):
    """处理代码操作的线程"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, operation_type, root_dir=None, markdown_file=None, old_code="", new_code="", use_regex=False):
        super().__init__()
        self.operation_type = operation_type
        self.root_dir = root_dir
        self.markdown_file = markdown_file
        self.old_code = old_code
        self.new_code = new_code
        self.use_regex = use_regex

    def run(self):
        try:
            if self.operation_type == "merge":
                self.merge_py_to_markdown()
            elif self.operation_type == "rollback":
                self.rollback_from_markdown()
            elif self.operation_type == "replace":
                self.replace_code_in_files()
        except Exception as e:
            self.log_signal.emit(f"❌ 错误: {str(e)}")

    def merge_py_to_markdown(self):
        """合并 Python 文件到 Markdown"""
        if self.root_dir is None:
            self.root_dir = os.getcwd()

        output_file = os.path.join(self.root_dir, "all_code.md")

        with open(output_file, "w", encoding="utf-8") as out:
            out.write("# 合并的 Python 代码文件\n\n")

            for dirpath, dirnames, filenames in os.walk(self.root_dir):
                # 过滤掉 test 目录
                if "test111" in dirpath.split(os.sep):
                    continue

                for file in filenames:
                    if file.endswith(".py"):
                        filepath = os.path.join(dirpath, file)
                        rel_path = os.path.relpath(filepath, self.root_dir)

                        # 跳过输出文件自身
                        if os.path.abspath(filepath) == os.path.abspath(output_file):
                            continue

                        self.log_signal.emit(f"处理文件: {rel_path}")
                        out.write(f"# 文件路径: {rel_path}\n")
                        out.write("```python\n")
                        try:
                            with open(filepath, "r", encoding="utf-8") as f:
                                out.write(f.read())
                        except Exception as e:
                            out.write(f"# 无法读取文件: {e}\n")
                        out.write("\n```\n\n---\n\n")

        self.finished_signal.emit(f"✅ 所有 .py 文件内容已合并到: {output_file}")

    def rollback_from_markdown(self):
        """从 Markdown 文件回滚到原始 Python 文件"""
        if not os.path.exists(self.markdown_file):
            self.finished_signal.emit(f"❌ Markdown 文件不存在: {self.markdown_file}")
            return

        try:
            with open(self.markdown_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.finished_signal.emit(f"❌ 读取 Markdown 文件失败: {e}")
            return

        pattern = r'# 文件路径: (.+?)\n```python\n(.*?)\n```\n\n---\n\n'
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            self.finished_signal.emit("❌ 未找到有效的文件内容")
            return

        restored_count = 0
        for file_path, file_content in matches:
            full_path = os.path.join(self.root_dir, file_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            try:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file_content.rstrip())
                self.log_signal.emit(f"✅ 已恢复: {file_path}")
                restored_count += 1
            except Exception as e:
                self.log_signal.emit(f"❌ 恢复文件失败 {file_path}: {e}")

        self.finished_signal.emit(f"🎉 回滚完成! 共恢复了 {restored_count} 个文件")

    def replace_code_in_files(self):
        """在文件中替换代码"""
        if not self.old_code.strip():
            self.finished_signal.emit("❌ 请先输入要替换的旧代码")
            return

        replaced_count = 0
        file_count = 0

        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            for file in filenames:
                if file.endswith(".py"):
                    filepath = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(filepath, self.root_dir)

                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()

                        # 替换代码
                        if self.use_regex:
                            # 使用正则表达式替换
                            try:
                                new_content, count = re.subn(self.old_code, self.new_code, content,
                                                             flags=re.MULTILINE | re.DOTALL)
                                if count > 0:
                                    with open(filepath, "w", encoding="utf-8") as f:
                                        f.write(new_content)
                                    self.log_signal.emit(f"✅ 已正则替换 ({count} 处): {rel_path}")
                                    replaced_count += 1
                            except re.error as e:
                                self.log_signal.emit(f"❌ 正则表达式错误 {rel_path}: {e}")
                                continue
                        else:
                            # 普通文本替换
                            if self.old_code in content:
                                new_content = content.replace(self.old_code, self.new_code)
                                with open(filepath, "w", encoding="utf-8") as f:
                                    f.write(new_content)
                                self.log_signal.emit(f"✅ 已替换: {rel_path}")
                                replaced_count += 1

                        file_count += 1

                    except Exception as e:
                        self.log_signal.emit(f"❌ 处理文件失败 {rel_path}: {e}")

        if self.use_regex:
            self.finished_signal.emit(
                f"🎉 正则替换完成! 处理了 {file_count} 个文件，在 {replaced_count} 个文件中进行了替换")
        else:
            self.finished_signal.emit(f"🎉 代码替换完成! 处理了 {file_count} 个文件，替换了 {replaced_count} 个文件")


class CodeProcessorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("代码处理工具")
        self.setGeometry(100, 100, 1000, 800)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("代码处理工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)

        # 文件操作区域
        file_group = QGroupBox("文件操作")
        file_layout = QVBoxLayout(file_group)

        # 目录选择
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("当前目录: " + os.getcwd())
        self.select_dir_btn = QPushButton("选择目录")
        self.select_dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.select_dir_btn)
        file_layout.addLayout(dir_layout)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.merge_btn = QPushButton("合并到Markdown")
        self.rollback_btn = QPushButton("从Markdown回滚")
        self.merge_btn.clicked.connect(self.merge_files)
        self.rollback_btn.clicked.connect(self.rollback_files)
        btn_layout.addWidget(self.merge_btn)
        btn_layout.addWidget(self.rollback_btn)
        file_layout.addLayout(btn_layout)

        main_layout.addWidget(file_group)

        # 代码替换区域
        replace_group = QGroupBox("代码替换")
        replace_layout = QVBoxLayout(replace_group)

        # 替换模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("替换模式:"))
        self.normal_radio = QRadioButton("普通替换")
        self.regex_radio = QRadioButton("正则表达式替换")
        self.normal_radio.setChecked(True)
        self.replace_mode_group = QButtonGroup()
        self.replace_mode_group.addButton(self.normal_radio)
        self.replace_mode_group.addButton(self.regex_radio)
        mode_layout.addWidget(self.normal_radio)
        mode_layout.addWidget(self.regex_radio)
        mode_layout.addStretch()
        replace_layout.addLayout(mode_layout)

        # 旧代码区域
        old_code_layout = QVBoxLayout()
        old_code_layout.addWidget(QLabel("旧代码:"))
        self.old_code_edit = QTextEdit()
        self.old_code_edit.setPlaceholderText("粘贴要替换的旧代码到这里...\n使用正则表达式时，请确保表达式正确")
        self.old_code_edit.setMaximumHeight(150)
        old_code_layout.addWidget(self.old_code_edit)
        replace_layout.addLayout(old_code_layout)

        # 新代码区域
        new_code_layout = QVBoxLayout()
        new_code_layout.addWidget(QLabel("新代码:"))
        self.new_code_edit = QTextEdit()
        self.new_code_edit.setPlaceholderText("粘贴新代码到这里...\n使用正则表达式时，可以使用分组引用如 \\1、\\2 等")
        self.new_code_edit.setMaximumHeight(150)
        new_code_layout.addWidget(self.new_code_edit)
        replace_layout.addLayout(new_code_layout)

        # 替换按钮
        replace_btn_layout = QHBoxLayout()
        self.detect_clipboard_btn = QPushButton("检测剪贴板")
        self.replace_btn = QPushButton("执行替换")
        self.preview_btn = QPushButton("预览替换")
        self.detect_clipboard_btn.clicked.connect(self.detect_clipboard)
        self.replace_btn.clicked.connect(self.replace_code)
        self.preview_btn.clicked.connect(self.preview_replace)
        replace_btn_layout.addWidget(self.detect_clipboard_btn)
        replace_btn_layout.addWidget(self.preview_btn)
        replace_btn_layout.addWidget(self.replace_btn)
        replace_layout.addLayout(replace_btn_layout)

        main_layout.addWidget(replace_group)

        # 日志区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        log_layout.addWidget(self.log_edit)

        main_layout.addWidget(log_group)

        # 状态栏
        self.statusBar().showMessage("就绪")

        # 当前工作目录
        self.current_dir = os.getcwd()

    def select_directory(self):
        """选择工作目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择目录", self.current_dir)
        if directory:
            self.current_dir = directory
            self.dir_label.setText("当前目录: " + directory)
            self.log("已选择目录: " + directory)

    def merge_files(self):
        """合并文件操作"""
        self.log("开始合并 Python 文件到 Markdown...")
        self.set_buttons_enabled(False)

        self.worker_thread = CodeProcessorThread("merge", self.current_dir)
        self.worker_thread.log_signal.connect(self.log)
        self.worker_thread.finished_signal.connect(self.operation_finished)
        self.worker_thread.start()

    def rollback_files(self):
        """回滚文件操作"""
        markdown_file = os.path.join(self.current_dir, "all_code.md")
        if not os.path.exists(markdown_file):
            QMessageBox.warning(self, "警告", f"未找到 Markdown 文件: {markdown_file}")
            return

        reply = QMessageBox.question(self, "确认回滚",
                                     "是否要从 Markdown 文件回滚到原始 Python 文件？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.log("开始从 Markdown 回滚文件...")
            self.set_buttons_enabled(False)

            self.worker_thread = CodeProcessorThread("rollback", self.current_dir, markdown_file)
            self.worker_thread.log_signal.connect(self.log)
            self.worker_thread.finished_signal.connect(self.operation_finished)
            self.worker_thread.start()

    def replace_code(self):
        """替换代码操作"""
        old_code = self.old_code_edit.toPlainText().strip()
        new_code = self.new_code_edit.toPlainText().strip()
        use_regex = self.regex_radio.isChecked()

        if not old_code:
            QMessageBox.warning(self, "警告", "请输入要替换的旧代码")
            return

        if use_regex:
            # 验证正则表达式
            try:
                re.compile(old_code)
            except re.error as e:
                QMessageBox.warning(self, "正则表达式错误", f"正则表达式格式错误:\n{e}")
                return

        reply = QMessageBox.question(self, "确认替换",
                                     "确定要执行代码替换操作吗？此操作不可逆！",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.log("开始替换代码..." + ("(使用正则表达式)" if use_regex else ""))
            self.set_buttons_enabled(False)

            self.worker_thread = CodeProcessorThread("replace", self.current_dir,
                                                     old_code=old_code, new_code=new_code, use_regex=use_regex)
            self.worker_thread.log_signal.connect(self.log)
            self.worker_thread.finished_signal.connect(self.operation_finished)
            self.worker_thread.start()

    def preview_replace(self):
        """预览替换结果"""
        old_code = self.old_code_edit.toPlainText().strip()
        new_code = self.new_code_edit.toPlainText().strip()
        use_regex = self.regex_radio.isChecked()

        if not old_code:
            QMessageBox.warning(self, "警告", "请输入要替换的旧代码")
            return

        if use_regex:
            try:
                re.compile(old_code)
            except re.error as e:
                QMessageBox.warning(self, "正则表达式错误", f"正则表达式格式错误:\n{e}")
                return

        # 查找第一个匹配的文件进行预览
        preview_content = ""
        preview_file = ""

        for dirpath, dirnames, filenames in os.walk(self.current_dir):
            for file in filenames:
                if file.endswith(".py"):
                    filepath = os.path.join(dirpath, file)

                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()

                        if use_regex:
                            if re.search(old_code, content, re.MULTILINE | re.DOTALL):
                                preview_content = content
                                preview_file = os.path.relpath(filepath, self.current_dir)
                                break
                        else:
                            if old_code in content:
                                preview_content = content
                                preview_file = os.path.relpath(filepath, self.current_dir)
                                break
                    except:
                        continue

            if preview_content:
                break

        if not preview_content:
            QMessageBox.information(self, "预览", "未找到包含匹配代码的文件")
            return

        # 显示预览
        if use_regex:
            new_content = re.sub(old_code, new_code, preview_content, flags=re.MULTILINE | re.DOTALL)
        else:
            new_content = preview_content.replace(old_code, new_code)

        preview_dialog = QMessageBox(self)
        preview_dialog.setWindowTitle("替换预览")
        preview_dialog.setText(f"文件: {preview_file}\n\n原内容:\n{preview_content}\n\n替换后:\n{new_content}")
        preview_dialog.setDetailedText(f"原内容:\n{preview_content}\n\n替换后:\n{new_content}")
        preview_dialog.exec()

    def detect_clipboard(self):
        """检测剪贴板内容"""
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text().strip()

        if clipboard_text:
            # 检查当前哪个文本框有焦点，或者都没有内容
            if not self.old_code_edit.toPlainText().strip():
                self.old_code_edit.setPlainText(clipboard_text)
                self.log("已从剪贴板填充旧代码")
            elif not self.new_code_edit.toPlainText().strip():
                self.new_code_edit.setPlainText(clipboard_text)
                self.log("已从剪贴板填充新代码")
            else:
                # 如果两个都有内容，询问用户
                reply = QMessageBox.question(self, "选择",
                                             "要将剪贴板内容放入哪个区域？",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.Yes)
                if reply == QMessageBox.StandardButton.Yes:
                    self.old_code_edit.setPlainText(clipboard_text)
                    self.log("已从剪贴板替换旧代码")
                else:
                    self.new_code_edit.setPlainText(clipboard_text)
                    self.log("已从剪贴板替换新代码")
        else:
            QMessageBox.information(self, "提示", "剪贴板为空或不是文本内容")

    def operation_finished(self, message):
        """操作完成回调"""
        self.log(message)
        self.set_buttons_enabled(True)
        self.statusBar().showMessage("操作完成")

    def set_buttons_enabled(self, enabled):
        """设置按钮启用状态"""
        self.merge_btn.setEnabled(enabled)
        self.rollback_btn.setEnabled(enabled)
        self.replace_btn.setEnabled(enabled)
        self.preview_btn.setEnabled(enabled)
        self.detect_clipboard_btn.setEnabled(enabled)
        self.select_dir_btn.setEnabled(enabled)

    def log(self, message):
        """添加日志"""
        self.log_edit.append(message)
        self.log_edit.moveCursor(QTextCursor.MoveOperation.End)
        self.statusBar().showMessage(message)


def main():
    app = QApplication(sys.argv)
    window = CodeProcessorUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()