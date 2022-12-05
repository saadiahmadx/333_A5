"""
Client code for Princeton Registrar Application with GUI (via PyQt5)
"""

import sys
import argparse
import socket
import pickle
import threading
import queue as queuemod
import PyQt5.QtCore as core
import PyQt5.QtWidgets as wid
import PyQt5.QtGui as gui


class WorkerThread (threading.Thread):

    def __init__(self, host, port, input, queue):
        threading.Thread.__init__(self)
        self._host = host
        self._port = port
        self._dept = input.get("dept")
        self._coursenum = input.get("coursenum")
        self._area = input.get("area")
        self._title = input.get("title")
        self._queue = queue
        self._should_stop = False

    def stop(self):
        self._should_stop = True

    def run(self):
        print("RUNNING WORKER THREAD")
        try:
            with socket.socket() as sock:

                sock.connect((self._host, self._port))
                print("WORKER THREAD CONNECTED")

                out_flo = sock.makefile(mode="wb", encoding="utf-8")
                pickle.dump({'dept': self._dept,
                             'num': self._coursenum,
                             'area': self._area,
                             'title': self._title}, out_flo)
                out_flo.flush()
                print("OUTFLOW")

                in_flo = sock.makefile(mode="rb", encoding="utf-8")
                courses = pickle.load(in_flo)
                print("INFLOW")

                self._queue.put((True, courses))
                print("QUEUE INSERSION")

            if courses == "":
                print("The reg server crashed", file=sys.stderr)
                raise Exception("The reg server crashed")
            sock.close()

        except Exception as ex:
            self._queue.put((False, ex))


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
        query_server_regdetails(
            self._args, self._window, item.data(core.Qt.UserRole))

# Query the server for class details


def query_server_regdetails(args, window, classid):
    """
    inputs: command arguments, class id of clicked class
    outputs: (GUI) show additional class details
    """
    try:
        with socket.socket() as sock:
            sock.connect((args.host, args.port))

            out_flo = sock.makefile(mode="wb", encoding="utf-8")
            pickle.dump(classid, out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode="r", encoding="utf-8")
            coursedetails = ""
            for line in in_flo.readlines():
                coursedetails += line
            wid.QMessageBox.information(
                window, "Course Details", coursedetails)
            in_flo.flush()
            sock.close()
        if coursedetails == "":
            print("The reg server crashed", file=sys.stderr)

    except Exception:
        print("""A server error occurred.
        Please contact the system administrator.""")

# Query reg server


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
                                    + course.get('dept').rjust(4)
                                    + course.get('coursenum').rjust(5)
                                    + course.get('area').rjust(4)+" "
                                    + course.get('title').ljust(100))
                course_item.setData(core.Qt.UserRole, course.get('id'))
                list.insertItem(index, course_item)
                index += 1
        sock.close()
    except Exception:
        print("""A server error occurred.
        Please contact the system administrator.""")


def create_widgets(args):
    dept_label = wid.QLabel(
        " Department: ", alignment=core.Qt.AlignRight)
    coursenum_label = wid.QLabel(
        " Number: ", alignment=core.Qt.AlignRight)
    area_label = wid.QLabel(" Area: ", alignment=core.Qt.AlignRight)
    title_label = wid.QLabel(" Title: ", alignment=core.Qt.AlignRight)

    dept_input = wid.QLineEdit("")
    coursenum_input = wid.QLineEdit("")
    area_input = wid.QLineEdit("")
    title_input = wid.QLineEdit("")

    return_list = ListWidget()
    return_list._args = args

    layout = wid.QGridLayout()

    layout.setSpacing(5)
    layout.setContentsMargins(0, 0, 0, 0)

    layout.addWidget(dept_label, 0, 1)
    layout.addWidget(coursenum_label, 1, 1)
    layout.addWidget(area_label, 2, 1)
    layout.addWidget(title_label, 3, 1)

    layout.addWidget(dept_input, 0, 2)
    layout.addWidget(coursenum_input, 1, 2)
    layout.addWidget(area_input, 2, 2)
    layout.addWidget(title_input, 3, 2)

    layout.addWidget(return_list, 4, 0, 1, 5)

    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(4, 1)
    layout.setColumnStretch(1, 1)
    layout.setColumnStretch(2, 100)
    layout.setColumnStretch(3, 1)

    frame = wid.QFrame()
    frame.setLayout(layout)
    window = wid.QMainWindow()
    window.setWindowTitle("Reg")
    window.setCentralWidget(frame)
    screen_size = wid.QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)

    return_list._window = window
    return_list.itemClicked.connect(return_list.clicked)

    return (window, dept_input,
            coursenum_input,
            area_input,
            title_input, return_list)


def reg_slot_helper(queue, return_list):
    while True:
        try:
            item = queue.get(block=False)
        except queuemod.Empty:
            break

        return_list.clear()
        successful, data = item
        if successful:
            courses = data
            index = 0
            for course in courses:
                course_item = wid.QListWidgetItem()
                course_item.setText(course.get('id').rjust(5)
                                    + course.get('dept').rjust(4)
                                    + course.get('coursenum').rjust(5)
                                    + course.get('area').rjust(4)+" "
                                    + course.get('title').ljust(100))
                course_item.setData(
                    core.Qt.UserRole, course.get('id'))
                return_list.insertItem(index, course_item)
                index += 1
        else:
            ex = data
            print('not successfull')
        return_list.repaint()

# Runs Application


def main(args):
    """
    input: host, port arguments

    output: GUI Registrar window
    """
    app = wid.QApplication(sys.argv)

    window, dept_input, coursenum_input, area_input, title_input, return_list = create_widgets(
        args)

    queue = queuemod.Queue()

    def reg_queue():
        reg_slot_helper(queue, return_list)

    timer = core.QTimer()
    timer.timeout.connect(reg_queue)
    timer.setInterval(100)  # milliseconds
    timer.start()

    worker_thread = None

    def reg_slot():
        nonlocal worker_thread

        dept = dept_input.text()
        coursenum = coursenum_input.text()
        area = area_input.text()
        title = title_input.text()

        if worker_thread is not None:
            worker_thread.stop()

        worker_thread = WorkerThread(
            args.host,
            args.port,
            {"dept":dept,
                "coursenum":coursenum,
                "area":area,
                "title":title},
            queue)
        worker_thread.start()

    dept_input.textChanged.connect(reg_slot)
    area_input.textChanged.connect(reg_slot)
    title_input.textChanged.connect(reg_slot)
    coursenum_input.textChanged.connect(reg_slot)

    window.show()
    reg_slot()
    sys.exit(app.exec_())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                description='Server for the registrar application',
                allow_abbrev=False)
    parser.add_argument('host',
                type=str,
                help='the host on which the server is running')
    parser.add_argument('port',
                type=int,
                help='the port at which the server is listening')
    args = parser.parse_args()
    main(args)
