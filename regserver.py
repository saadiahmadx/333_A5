"""
Server code for Princeton Registrar Application with GUI
"""
import sys
import os
import socket
import pickle
import argparse
import contextlib
import sqlite3


# Sanitize text input
def sanitize(field):
    """
    input: string field
    output: string with '%' and '_' formatted for SQL
    """
    sanitized = field.replace('%', '\\%')
    sanitized = sanitized.replace('_', '\\_')
    return sanitized

# Generate query based on available user input
def generate_query(dept, num, area, title):
    """
    Generates query body given inputs
    inputs:
    department,
    course #,
    course area,
    course title
    output:
    generated SQL query body,
    generated SQL query args
    """
    query_body=''
    if(dept or num or area or title):
        query_body = "WHERE "
    first = True
    query_args = []
    if dept:
        if not first:
            query_body+= ' AND '
        query_body+= "cross.dept LIKE ?"
        query_args.append("%"+sanitize(dept)+"%")
        first = False
    if area:
        if not first:
            query_body+= ' AND '
        query_body+= "co.area LIKE ?"
        query_args.append("%"+sanitize(area)+"%")
        first = False
    if title:
        if not first:
            query_body+= ' AND '
        query_body+= "co.title LIKE ?"
        query_args.append("%"+sanitize(title.lower())+"%")
        first = False
    if num:
        if not first:
            query_body+= ' AND '
        query_body+= "cross.coursenum LIKE ?"
        query_args.append("%"+sanitize(str(num))+"%")
        first = False
    if(dept or num or area or title):
        query_body += "ESCAPE '\\'"
    return query_body, query_args

#returns all classes with specified attrebutes
def filter_classes(dept=None, num=None, area=None, title=None):
    """
    Inputs:
    -d dept   show only those classes whose department contains dept
    -n num    show only those classes whose course number contains num
    -a area   show only those classes whose distrib area contains area
    -t title  show only those classes whose course title contains title
    Outputs:
    Class descriptions filtered on inputs
    """
    try:
        with sqlite3.connect("reg.sqlite",
            isolation_level = None) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                query_head = """
                    SELECT cl.classid, cross.dept, cross.coursenum,
                    co.area, co.title
                    FROM classes as cl
                        INNER JOIN
                        courses as co
                        ON cl.courseid = co.courseid
                        INNER JOIN
                        crosslistings as cross
                        ON cl.courseid = cross.courseid
                """
                query_body, query_args = generate_query(dept,
                num,area,title)
                query_closing = """
                    ORDER BY cross.dept ASC,
                    cross.coursenum ASC,
                    cl.classid ASC
                """
                cursor.execute(query_head+query_body+query_closing,
                query_args)
                results = cursor.fetchall()

                output = []
                for result in results:
                    class_object = {'id': str(result[0]),
                                    'dept':str(result[1]),
                                    'coursenum':str(result[2]),
                                    'area': str(result[3]),
                                    'title': str(result[4])}
                    output.append(class_object)
                return output

    except Exception as ex:
        print(sys.argv[0] + ": " +str(ex), file=sys.stderr)
        return []

#returns details for a given class_id
def get_class_details(class_id, out_flo):
    """
    Input:
    class_id

    Output:
    -> Course ID
    -> Days
    -> Start Time
    -> End Time
    -> Building
    -> Room
    -> Dept and Number
    -> Area
    -> Title
    -> Description
    -> Prereqs
    -> Professor
    """
    try:
        with sqlite3.connect("reg.sqlite",
        isolation_level = None) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                class_query = """
                    SELECT *
                    FROM
                    classes as cl,
                    courses as co
                    WHERE cl.courseid = co.courseid
                    AND cl.classid = ?
                """
                cross_query = """
                    SELECT dept,coursenum,prereqs
                    FROM
                    crosslistings as cross,
                    classes as cl,
                    courses as co
                    WHERE cross.courseid = co.courseid
                    AND cl.courseid = co.courseid
                    AND cl.classid = ?
                    ORDER BY dept ASC, coursenum ASC
                """
                prof_query = """
                    SELECT profname
                    FROM classes AS cl
                    INNER JOIN coursesprofs AS cp ON (cl.courseid = cp.courseid)
                    INNER JOIN profs AS p ON (p.profid = cp.profid)
                    WHERE cl.classid =  ?
                    ORDER BY profname ASC
                """
                cursor.execute(class_query, [class_id])
                class_result = cursor.fetchone()

                if not class_result:
                    return print(sys.argv[0] +
                    ": no class with classid "
                    +class_id+" exists",
                    file=sys.stderr)

                out_flo.write("Course Id: "+str(class_result[1])+"\n\n")
                out_flo.write("Days: "+class_result[2]+"\n")
                out_flo.write("Start time: "+class_result[3]+"\n")
                out_flo.write("End time: "+class_result[4]+"\n")
                out_flo.write("Building: "+class_result[5]+"\n")
                out_flo.write("Room: "+class_result[6]+"\n")

                cursor.execute(cross_query, [class_id])
                cross_result = cursor.fetchall()
                for c_result in cross_result:
                    out_flo.write("\nDept and Number: "+c_result[0]
                    +" "+ c_result[1])

                out_flo.write("\n\n"+"Area: "+class_result[8]+"\n")

                out_flo.write("\n" + "Title: "+class_result[9] + "\n")

                out_flo.write("\n" + "Description: "+class_result[10]
                + "\n")

                out_flo.write("\n" + "Prerequisites: "+class_result[11]
                + "\n")

                cursor.execute(prof_query, [class_id])
                prof_result = cursor.fetchall()
                for prof in prof_result:
                    out_flo.write("\n"+"Professor: "+prof[0])

    except Exception as ex:
        print(sys.argv[0] + ": " +str(ex), file=sys.stderr)

# Client handler
def handle_client(sock):
    """
    input:
    client-socket
    output:
    prints-logs
    """
    # Read query from client
    in_flo = sock.makefile(mode="rb", encoding="utf-8")
    query = pickle.load(in_flo)
    in_flo.flush()
    print("Read from client: " + str(query))
    if type(query) is dict:
        # Run SQLite functions and find classes
        classes = filter_classes(query.get('dept'),
                                query.get('num'),
                                query.get('area'),
                                query.get('title'))
        # Write classes back to client
        out_flo = sock.makefile(mode="wb", encoding="utf-8")
        pickle.dump(classes, out_flo)
        out_flo.flush()
        print("Wrote "+str(len(classes))+" classes to client")
    else:
        # Write classes back to client
        out_flo = sock.makefile(mode="w", encoding="utf-8")
        class_details = get_class_details(query,out_flo)
        out_flo.flush()
        print("Wrote class details ("+query+") to client")


# Main server code
def main(args):
    # Check that port is between 10000-60000
    # if args.port < 10000 or args.port > 60000:
    #     print("Usage: python %s host port" % sys.argv[0])
    #     sys.exit(2)

    try:
        port = args.port
        server_sock = socket.socket()
        print("Opened server socket")

        if os.name != "nt":
            server_sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind(("", port))

        print("Bound server socket to port")
        server_sock.listen()

        print("Listening")

        while True:
            try:
                sock, client_addr = server_sock.accept()
                with sock:
                    print("Accepted connection")
                    print("Opened socket")
                    print("Server IP addr and port:",
                    sock.getsockname())
                    print("Client IP addr and port:", client_addr)
                    handle_client(sock)

            except Exception as ex:
                print(ex, file=sys.stderr)

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Server for the registrar application',
        allow_abbrev=False, exit_on_error=True)

    parser.add_argument('port', metavar='port',type=int,
        help='the port at which the server should listen')

    main(parser.parse_args())
