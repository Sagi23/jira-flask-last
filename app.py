import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import json
from datetime import timedelta


app = Flask(__name__)
CORS(app)

ITEMS_PER_PAGE = 10
BASE_URL = "https://jira-soft.ngsoft.com/rest/api/2"
NO_RESULT_SEARCH = "startAt=0&maxResults=0"

app.secret_key = 'hello'
app.permanent_session_lifetime = timedelta(days=350)

def get_total_issues(jql, headers, BASE_URL, NO_RESULT_SEARCH):
    response = requests.get(f'{BASE_URL}/search/?jql={jql}&{NO_RESULT_SEARCH}', headers=headers)
    response_json = json.loads(response.text)
    return response_json['total']

@app.route('/')
def hello():
    print('///////')
    return jsonify({"messeage": "hello"})


@app.route('/login', methods=['POST', 'GET'])
def login():

    data = request.get_json()
    auth = data['auth']
    print(auth)
    # auth = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
    app.auth = auth

    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json',
        "Content-Encoding": "gzip",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
    response = requests.get(f'https://jira-soft.ngsoft.com/rest/api/2/project', headers=headers)

    if response.status_code == 200:
        return jsonify({'success': True})


    else:
        return jsonify({'success': False})



@app.route('/jira/project/<auth>', methods=['POST', 'GET'])
def get_all_projects(auth):
    # Extract the page parameters from the query string
    page = request.args.get('page', default=1, type=int)
  
    # Base64 encode the credentials
    # auth = base64.b64encode(b'sagi.twig:St123369').decode('utf-8')

    # Set the Authorization header
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json',
        "Content-Encoding": "gzip",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    # Send the API request with the startAt and maxResults parameters
    response = requests.get(f'https://jira-soft.ngsoft.com/rest/api/2/project?startAt={(page - 1) * ITEMS_PER_PAGE}&maxResults={ITEMS_PER_PAGE}', headers=headers)

    string_data = response.content.decode("utf-8")

    # Return the response
    return make_response(string_data, 200)



@app.route('/jira/search/<project_id>/<severity>/<auth>', methods=['POST', 'GET'])
def jira_jql_severity(project_id, severity, auth):
   
    # Base64 encode the credentials
    # auth = base64.b64encode(b'sagi.twig:St123369').decode('utf-8')
    page = request.args.get('page', default=1, type=int)



    # Set the Authorization header
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json',
        "Content-Encoding": "gzip",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }


    # Send the API request
    response = requests.get(f'{BASE_URL}/search/?jql=project={project_id}&startAt={(page - 1) * ITEMS_PER_PAGE}&maxResults={ITEMS_PER_PAGE}', headers=headers)
    string_data = response.content.decode("utf-8")

    total_issues = get_total_issues(f'project={project_id}', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_blocker = get_total_issues(f'project={project_id} AND severity="blocker"', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_critical = get_total_issues(f'project={project_id} AND severity="critical"', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_major = get_total_issues(f'project={project_id} AND severity="major"', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_minor = get_total_issues(f'project={project_id} AND severity="minor"', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_cosmetic = get_total_issues(f'project={project_id} AND severity="cosmetic"', headers, BASE_URL, NO_RESULT_SEARCH)



    total_issues_open = get_total_issues(f'project={project_id} {(f"AND severity={severity}" if severity != "All" else "")} AND status="open"', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_closed = get_total_issues(f'project={project_id} {(f"AND severity={severity}" if severity != "All" else "")}  AND status="closed"', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_reopened = get_total_issues(f'project={project_id} {(f"AND severity={severity}" if severity != "All" else "")}  AND status="reopened"', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_in_progress = get_total_issues(f'project={project_id} {(f"AND severity={severity}" if severity != "All" else "")}  AND status="in progress"', headers, BASE_URL, NO_RESULT_SEARCH)
    total_issues_customer_approval = get_total_issues(f'project={project_id} {(f"AND severity={severity}" if severity != "All" else "")}  AND status="customer approval"', headers, BASE_URL, NO_RESULT_SEARCH)


    json_data = json.loads(string_data)
    project_name = 'Error No Issues Found'
    
    if json_data['issues']:
        project_name = json_data['issues'][0]['fields']['project']['name']


    res = {
        "data": string_data,
        "total_issues" : total_issues,
        "total_blocker" : total_issues_blocker,
        "total_critical" : total_issues_critical,
        "total_major" : total_issues_major,
        "total_minor" : total_issues_minor,
        "total_cosmetic" : total_issues_cosmetic,
        "total_open" : total_issues_open,
        "total_closed" : total_issues_closed,
        "total_reopened" : total_issues_reopened,
        "total_in_progress" : total_issues_in_progress,
        "total_customer_approval" : total_issues_customer_approval,
        "project_name" : project_name,
    }


    # Return the response
    return make_response(res, 200)




# @app.route('/jira/issue/<issue_id>', methods=['GET'])
# def jira_issue(issue_id):
#     # Base64 encode the credentials
#     auth = base64.b64encode(b'sagi.twig:St123369').decode('utf-8')

#     # Set the Authorization header
#     headers = {
#         'Authorization': f'Basic {auth}',
#         'Content-Type': 'application/json',
#         "Content-Encoding": "gzip",
#         "Access-Control-Allow-Origin": "*",
#         "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
#         "Access-Control-Allow-Headers": "Content-Type, Authorization"
#     }

#     # Send the API request
#     response = requests.get(f'{BASE_URL}/issue/{issue_id}', headers=headers)
#     string_data = response.content.decode("utf-8")

#     # Return the response
#     return make_response(jsonify(string_data), 200)
    
if __name__ == '__main__':
    app.run()