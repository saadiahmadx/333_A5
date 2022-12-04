import html
import flask
import templates
import database
#-----------------------------------------------------------------------

app = flask.Flask(__name__)

#-----------------------------------------------------------------------

def error(string):
    html_code = templates.ERROR_PAGE_TEMPLATE.replace('{{error}}',
        string)
    response = flask.make_response(html_code)
    return response

def format_form(form, dept, num, area, title):
    if dept:
        form = form.replace('{{dept}}', dept)
    else:
        form = form.replace('{{dept}}', '')
    if num:
        form = form.replace('{{coursenum}}', num)
    else:
        form = form.replace('{{coursenum}}', '')
    if area:
        form = form.replace('{{area}}', area)
    else:
        form = form.replace('{{area}}', '')
    if title:
        form = form.replace('{{title}}', title)
    else:
        form = form.replace('{{title}}', '')

    return form

def format_classes(classes):
    results = ''
    for clas in classes:
        results += "<tr>"
        if clas.get('id'):
            results += """<td><a href='/regdetails?classid=
            """+clas.get('id')+"'>"+clas.get('id')+"</td>"
        else:
            results += "<td></td>"
        if clas.get('dept'):
            results += "<td>"+clas.get('dept')+"</td>"
        else:
            results += "<td></td>"
        if clas.get('coursenum'):
            results += "<td>"+clas.get('coursenum')+"</td>"
        else:
            results += "<td></td>"
        if clas.get('area'):
            results += "<td>"+clas.get('area')+"</td>"
        else:
            results += "<td></td>"
        if clas.get('title'):
            results += "<td>"+clas.get('title')+"</td>"
        else:
            results += "<td></td>"
        results += "</tr>"
    return templates.SEARCH_RESULTS_TEMPLATE.replace('{{results}}',
                                                        results)

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])

def index():
    dept = flask.request.args.get("dept")
    if dept:
        dept = html.escape(str(dept))
    num = flask.request.args.get("num")
    if num:
        num = html.escape(str(num))
    area = flask.request.args.get("area")
    if area:
        area = html.escape(str(area))
    title = flask.request.args.get("title")
    if title:
        title = html.escape(str(title))

    header = templates.HEADER_TEMPLATE
    footer = templates.FOOTER_TEMPLATE

    form = templates.FORM_TEMPLATE
    form = format_form(form, dept, num, area, title)
    classes = database.filter_classes(dept, num, area, title)


    if classes == 0:
        error_page = templates.ERROR_PAGE_TEMPLATE.replace(
            '{{header}}', header)
        error_page = error_page.replace('{{footer}}', footer)
        error_page = error_page.replace('{{error}}',
            """A server error occured.
            Please contact the system administrator.""")
        return flask.make_response(error_page)


    search_results = format_classes(classes)

    html_code = templates.INDEX_TEMPLATE.replace('{{header}}',
                                                    header)
    html_code = html_code.replace('{{form}}', form)
    html_code = html_code.replace('{{search_results}}',
                                                    search_results)
    html_code = html_code.replace('{{footer}}', footer)

    response = flask.make_response(html_code)

    return response

#-----------------------------------------------------------------------
@app.route('/searchresults', methods=['GET'])
def search_results():
    dept = flask.request.args.get("dept")
    num = flask.request.args.get("num")
    area = flask.request.args.get("area")
    title = flask.request.args.get("title")

    classes = database.filter_classes(dept, num, area, title)
    search_results = format_classes(classes)

    response = flask.make_response(search_results)
    return response
 

#-----------------------------------------------------------------------
@app.route('/regdetails', methods=['GET'])

def reg_details():
    header = templates.HEADER_TEMPLATE
    footer = templates.FOOTER_TEMPLATE

    html_code = templates.REG_DETAILS_TEMPLATE.replace('{{header}}',
                                                            header)
    html_code = html_code.replace('{{footer}}', footer)

    class_id = flask.request.args.get('classid')

    error_page = templates.ERROR_PAGE_TEMPLATE.replace('{{header}}',
                                                            header)
    error_page = error_page.replace('{{footer}}', footer)

    if not class_id:
        error_page = error_page.replace('{{error}}',
        "Missing class id.")
        return flask.make_response(error_page)

    try:
        class_id = int(class_id)
        class_id = str(class_id)
    except:
        return flask.make_response(error_page.replace('{{error}}',
        "Class id must be an integer."))


    class_details = database.get_class_details(class_id)
    if class_details == 0:
        error_page = error_page.replace('{{error}}',
            """A server error occured.
            Please contact the system administrator.""")
        return flask.make_response(error_page)

    if not class_details:
        error_page = error_page.replace('{{error}}',
        "Class details could not be fetched for this class id.")
        return flask.make_response(error_page)

    html_code = html_code.replace('{{class_id}}',
                        class_id)
    html_code = html_code.replace('{{course_id}}',
                        class_details.get('course_id'))
    html_code = html_code.replace('{{days}}',
                        class_details.get('days'))
    html_code = html_code.replace('{{start_time}}',
                        class_details.get('start_time'))
    html_code = html_code.replace('{{end_time}}',
                        class_details.get('end_time'))
    html_code = html_code.replace('{{building}}',
                        class_details.get('building'))
    html_code = html_code.replace('{{room}}',
                        class_details.get('room'))

    html_code = html_code.replace('{{area}}',
                        class_details.get('area'))
    html_code = html_code.replace('{{title}}',
                        class_details.get('title'))
    html_code = html_code.replace('{{description}}',
                        class_details.get('description'))
    html_code = html_code.replace('{{prerequisites}}',
                        class_details.get('prerequisites'))

    profs = ""
    if class_details.get('profs'):
        for prof in class_details.get('profs'):
            profs += "<strong>Professor: </strong>" + prof +"<br>"
        html_code = html_code.replace('{{professors}}', profs)

    dept_and_num = ""
    if class_details.get('dept_and_num'):
        index_class = 0
        for deptnum in class_details.get('dept_and_num'):
            index_class += 1
            if index_class == len(class_details.get('dept_and_num')):
                dept_and_num += """<strong>
                Dept and Number: </strong>""" + deptnum
            else:
                dept_and_num += """<strong>
                Dept and Number: </strong>""" + deptnum +"<br>"
        html_code = html_code.replace('{{dept_and_num}}', dept_and_num)


    response = flask.make_response(html_code)

    return response