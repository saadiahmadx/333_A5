"""
Client code for Princeton Registrar Application
with GUI (via PyQt5)

"""

import sys
import argparse
import socket
import pickle
#importing each creates no-name-in-module
#warning, instead import via wildcard
#pylint: disable=W0401
import PyQt5.QtCore as core
import PyQt5.QtWidgets as wid
import PyQt5.QtGui as gui
# undefined-varible warning diabled due to wildcard imports
# pylint: disable=E0602

# pylint: disable=W0212
class ListWidget(wid.QListWidget):
    """
    List to show classes and handle click event
    """
    _args = None
    _window = None

    def clicked(self, item):
        """
        inputs:
        outputs:
        """
        print(self._args, item.data(core.Qt.UserRole))
        query_server_regdetails(self._args, self._window,
            item.data(core.Qt.UserRole))

#Query the server for class details
def query_server_regdetails(args, window, classid):
    """
    inputs: command arguments, class id of clicked class
    outputs: (GUI) show additional class details
    """
    try:
        with socket.socket() as sock:
            sock.connect((args.host, args.port))

            out_flo = sock.makefile(mode="wb", encoding="utf-8")
            pickle.dump(classid,out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode="r", encoding="utf-8")
            coursedetails = ""
            for line in in_flo.readlines():
                coursedetails.join(line)
            wid.QMessageBox.information(window, "Course Details" ,
                coursedetails)
            in_flo.flush()

        if coursedetails == "":
            print("The reg server crashed", file=sys.stderr)

    except Exception:
        print("""A server error occurred.
        Please contact the system administrator.""")

#Query reg server
def query_server_reg(args, query, list):
    """
    inputs: command arguments

    outputs: (GUI) shows class details
    """

    try:
        with socket.socket() as sock:
            sock.connect((args.host, args.port))

            out_flo = sock.makefile(mode="wb", encoding="utf-8")
            pickle.dump(query, out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode="rb", encoding="utf-8")
            courses = pickle.load(in_flo)
            in_flo.flush()

        if courses == "":
            print("The reg server crashed", file=sys.stderr)
        else:
            list.clear()
            index = 0
            for course in courses:
                course_item = wid.QListWidgetItem()
                course_item.setText(course.get('id').rjust(5)
                                    +course.get('dept').rjust(4)
                                    +course.get('coursenum').rjust(5)
                                    +course.get('area').rjust(4)+" "
                                    +course.get('title').ljust(100))
                course_item.setData(core.Qt.UserRole, course.get('id'))
                list.insertItem(index, course_item)
                index += 1

    except Exception:
        print("""A server error occurred.
        Please contact the system administrator.""")

# Runs Application
def main(argsp):
    """
    input: host, port arguments

    output: GUI Registrar window
    """
    app = wid.QApplication(sys.argv)

    dept_label = wid.QLabel(" Department: ", alignment=core.Qt.AlignRight)
    coursenum_label = wid.QLabel(" Number: ", alignment=core.Qt.AlignRight)
    area_label = wid.QLabel(" Area: ", alignment=core.Qt.AlignRight)
    title_label = wid.QLabel(" Title: ", alignment=core.Qt.AlignRight)

    dept_input = wid.QLineEdit("")
    coursenum_input = wid.QLineEdit("")
    area_input = wid.QLineEdit("")
    title_input = wid.QLineEdit("")

    return_list = ListWidget()
    return_list._args = argsp

    search_button = wid.QPushButton("Search")

    layout = wid.QGridLayout()

    layout.setSpacing(5)
    layout.setContentsMargins(0, 0, 0, 0)

    layout.addWidget(dept_label, 0, 1)
    layout.addWidget(coursenum_label, 1,1)
    layout.addWidget(area_label, 2, 1)
    layout.addWidget(title_label,3, 1)

    layout.addWidget(dept_input, 0, 2)
    layout.addWidget(coursenum_input, 1,2)
    layout.addWidget(area_input, 2, 2)
    layout.addWidget(title_input ,3, 2)

    layout.addWidget(search_button,0,3,4,1)
    layout.addWidget(return_list,4,0,1,5)

    layout.setColumnStretch(0,1)
    layout.setColumnStretch(4,1)
    layout.setColumnStretch(1,1)
    layout.setColumnStretch(2,100)
    layout.setColumnStretch(3,1)

    frame = wid.QFrame()
    frame.setLayout(layout)
    window = wid.QMainWindow()
    window.setWindowTitle("Reg")
    window.setCentralWidget(frame)
    screen_size = wid.QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)

    return_list._window = window
    return_list.itemClicked.connect(return_list.clicked)

    search_button.clicked.connect(lambda: query_server_reg(argsp,
        {'dept':dept_input.text(),
        'num':coursenum_input.text(),
        'area':area_input.text(),
        'title':title_input.text()},return_list))


    query_server_reg(argsp,
        {'dept':dept_input.text(),
        'num':coursenum_input.text(),
        'area':area_input.text(),
        'title':title_input.text()},return_list)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Server for the registrar application',
        allow_abbrev=False, exit_on_error=True)
    parser.add_argument('host',type=str,
        help='the host on which the server is running')
    parser.add_argument('port',type=int,
        help='the port at which the server is listening')

    main(parser.parse_args())
