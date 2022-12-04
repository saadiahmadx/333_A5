FOOTER_TEMPLATE = ('''

<center class="footer"> Created by Nickolas Casalinuovo and Saadi Ahmad. </center>

''')

HEADER_TEMPLATE = ('''
<center><h1 style="background-color:#E77500; color:white" >Registrar's Office: Class Search</h1></center>
''')

FORM_TEMPLATE = ('''

<form action="" method="get">
    <div class='search' style="">
            <input id="DEPT" type="text" style="color:white" name="dept" placeholder="Department" value="{{dept}}" autoFocus>
            <input id="NUM" type="text" name="coursenum" placeholder="Number" value="{{coursenum}}">
            <input id="AREA" type="text" name="area" placeholder="Area" value="{{area}}">
            <input id="TITLE" type="text" name="title" placeholder="Title" value="{{title}}">
    </div>
</form>
<br>
''')


SEARCH_RESULTS_TEMPLATE = ('''
    <table>
        <tbody>
            <tr>
                <th><strong>ClassId</strong></th>
                <th><strong>Dept</strong></th>
                <th><strong>Num</strong></th>
                <th><strong>Area</strong></th>
                <th><strong>Title</strong></th>
            </tr>
            {{results}}
        </tbody>
    </table>
''')

INDEX_TEMPLATE = ('''
    <!DOCTYPE html>
        <html>
        <head>
            <title>Registrar's Office Class Search</title>
            
            <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Lato">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                h1 {
                margin-bottom: 10px;
                padding-top: 10px;
                font-family: "Lato";
                font-size:calc(2vw + 20px);
                
                }
                body {
                font-family: "Lato";
                
                }
                input         {
                font-size:20px;
                margin: 5px;
                padding:10px 10px 10px 15px;

                border:1px solid #FFFFFF;
                border-radius: 25px;
                background-color:#E77500;
                color:#FFFFFF;
                min-width: 420px;

                }
                table {
                width: 100%;
                }
                th {
                color:#000000;;
                background:#ffdfbf;
                //border-bottom:4px solid #9ea7af;
                font-size:16px;
                font-weight: 100;
                padding:10px;
                text-align:left;
                text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
                vertical-align:middle;
                }

                th:first-child {
                border-top-left-radius:20px;
                }

                th:last-child {
                border-top-right-radius:20px;
                border-right:none;
                }

                tr {
                color:#666B85;
                font-size:16px;
                font-weight:normal;
                text-shadow: 0 1px 1px rgba(256, 256, 256, 0.05);
                }

                tr:hover td {
                background:#4E5066;
                color:#FFFFFF;
                }

                tr:first-child {
                border-top:none;
                }

                tr:last-child {
                border-bottom:none;
                }

                tr:nth-child(odd) td {
                background:#EBEBEB;
                }

                tr:nth-child(odd):hover td {
                background:#4E5066;
                }

                tr:last-child td:first-child {
                border-bottom-left-radius:3px;
                }

                tr:last-child td:last-child {
                border-bottom-right-radius:3px;
                }

                td {
                background:#FFFFFF;
                padding:8px;
                text-align:left;
                vertical-align:middle;
                font-weight:300;
                font-size:16px;
                }

                td:last-child {
                border-right: 0px;
                }
                .search {
                display: flex;
                flex-wrap: wrap;
                flex-direction: row;
                justify-content:center;
                }
                ::placeholder {
                color: #FFFFFF;
                opacity: 0.6;
                font-style: italic; 
                }

                .footer {
                background-color:#E77500; 
                color:white;
                padding: 10px;
                border-radius: 25px;
                border-top-left-radius:0px;
                border-top-right-radius:0px;
                }
            
            </style>
        </head>
        <body>
        <div style="background-color:#E77500;border-radius: 15px;">
            {{header}}

            {{form}}

            
        </div>
        <div id="RESULTS"> 
            {{search_results}}
        </div>
            
            {{footer}}

        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
        <script>
            'use strict';
            function handleResponse(response){
                $('#RESULTS').html(response);
            }
            let request = null;
            function getResults(){
                let dept = $('#DEPT').val();
                let num = $('#NUM').val();
                let area = $('#AREA').val();
                let title = $('#TITLE').val();
                dept = encodeURIComponent(dept);
                num = encodeURIComponent(num);
                area = encodeURIComponent(area);
                title = encodeURIComponent(title);
                url = '/searchresults?dept=' + dept + '&num=' + num + '&area=' + area + '&title=' + title;
             

                if (request != null){
                    request.abort();
                }
                request = $.ajax(
                    {
                        type: 'GET',
                        url: url,
                        success: handleResponse
                    }
                );
                
            }

            function setup(){
                $('#DEPT').on('input', getResults);
                $('#NUM').on('input', getResults);
                $('#AREA').on('input', getResults);
                $('#TITLE').on('input', getResults);
                getResults();
            }

            $('document').ready(setup);
        </script>
        </body>
    </html>
''')

REG_DETAILS_TEMPLATE = ('''
    <!DOCTYPE html>
        <html>
        <head>
            <title>Registrar's Office: Class Details</title>
            <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Lato:bold,normal">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                h1 {
                    font-family: "Lato";
                    font-size:calc(2vw + 20px);

                }
                body {
                    font-family: "Lato";
                    line-height: 1.5rem;

                }
                .footer {
                    background-color:#E77500; 
                    color:white;
                    padding: 10px;
                    border-radius: 25px;
                    border-top-left-radius:0px;
                    border-top-right-radius:0px;
                }
                strong {
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
        <div style="background-color:#E77500;">
            <center><h1 style="background-color:#E77500; color:white; padding:40px;" >Registrar's Office: Class Details</h1></center>
        </div>
        <div style="padding:0px 10px;">
            <h2>Class Details (class id {{class_id}})</h2>
            <strong>Course Id: </strong>{{course_id}} <br/>
            <strong>Days: </strong>{{days}} <br/>
            <strong>Start time: </strong>{{start_time}} <br/>
            <strong>End time: </strong>{{end_time}} <br/>
            <strong>Building: </strong>{{building}} <br/>
            <strong>Room: </strong>{{room}} <br/> <br/>

            <hr>
            <h2>Course Details (course id {{course_id}})</h2>

            {{dept_and_num}} <br/>
            <strong>Area: </strong>{{area}} <br/>
            <strong>Title: </strong>{{title}} <br/>
            <strong>Description: </strong>{{description}} <br/>
            <strong>Prerequisites: </strong>{{prerequisites}} <br/>
            {{professors}} <br/>
        </div>
            {{footer}}
        </body>
    </html>
''')

ERROR_PAGE_TEMPLATE = ('''
    <!DOCTYPE html>
        <html>
        <head>
            <title>Registrar's Office Class Search</title>
            <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Lato">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                h1 {
                    font-family: "Lato";
                    font-size:calc(2vw + 20px);

                }
                body {
                    font-family: "Lato";
                    line-height: 1.5rem;

                }
                .footer {
                    background-color:#E77500; 
                    color:white;
                    padding: 10px;
                    border-radius: 25px;
                    border-top-left-radius:0px;
                    border-top-right-radius:0px;
                }
                strong {
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div style="background-color:#E77500;">
                <center><h1 style="background-color:#E77500; color:white; padding:40px;" >Registrar's Office: Class Search</h1></center>
            </div>

            <p><strong>{{error}}</strong></p>

            {{footer}}
        </body>
    </html>
''')
