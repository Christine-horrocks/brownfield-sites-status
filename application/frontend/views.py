import urllib.request, csv, requests
from flask import (
    Blueprint,
    render_template,
    current_app,
    request, url_for,
    session)
from application.frontend.utils import (
    data_standard_headers,
    fetch_results,
    fetch_validation_result,
    summarise_results,
    sort_results
)
from application.forms import URLForm
from io import StringIO
from werkzeug.utils import redirect

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def index():
    return render_template('overview.html', data=summarise_results(current_app.config['STATUS_API']))


@frontend.route('/breakdown')
def breakdown():
    data = sort_results(fetch_results(current_app.config['STATUS_API']))
    return render_template('breakdown.html', data=data)


@frontend.route('/local-authority/<local_authority_id>/change-url', methods=['GET', 'POST'])
def change_url(local_authority_id):
    current_url = _current_url(local_authority_id)
    form = URLForm(current_url=current_url)
    if request.method == 'POST':
        form = URLForm(obj=request.form)
        if form.validate():
            new_url = form.data['register_url']
            api_request_url = 'https://8kx22p2dgg.execute-api.eu-west-2.amazonaws.com/dev/status?url='+new_url
            api_response = requests.get(api_request_url).json()
            print(api_response)
            # TODO change the if statement to equals when finished developing
            if api_response['statusCode'] != 200:
                return redirect(url_for('frontend.what_next', local_authority_id=local_authority_id))
            else:
                session['tested_url'] = new_url
                return redirect(url_for('frontend.url_update_error', local_authority_id=local_authority_id))

    return render_template('change-url.html', local_authority_id=local_authority_id, form=form)


def _current_url(local_authority_id):
    brownfield_register_index_url = 'https://raw.githubusercontent.com/digital-land/alpha-data/master/mhclg-registers/brownfield-register-index.csv'
    data = urllib.request.urlopen(brownfield_register_index_url).read().decode('utf-8')
    data_file = StringIO(data)
    csv_file = csv.reader(data_file)
    for row in csv_file:
        if row[0] == local_authority_id:
            return row[1]


@frontend.route('/local-authority/<local_authority_id>/url-update-error', methods=['GET', 'POST'])
def url_update_error(local_authority_id):
    current_url = _current_url(local_authority_id)
    form = URLForm(current_url=current_url)
    tested_url = session['tested_url']
    return render_template('url-update-error.html', local_authority_id=local_authority_id, form=form, tested_url=tested_url)


@frontend.route('/local-authority/<local_authority_id>/what-next')
def what_next(local_authority_id):
    url = _current_url(local_authority_id)

    return render_template('what-next.html', url=url, local_authority_id=local_authority_id)


@frontend.route('/local-authority/<local_authority_id>/result-details')
def result_details_for_authority(local_authority_id):
    url = current_app.config['STATUS_API'] + '/?organisation=' + local_authority_id
    result_data = fetch_validation_result(url)
    return render_template('validation-result.html', data={'organisation': local_authority_id, 'url': url, 'result': result_data[0]})


def _check(given, expected):
    checked = []
    for field in given:
        if field in expected:
            checked.append((field, True))
        else:
            checked.append((field, False))
    checked_expected = []
    for field in expected:
        if field in given:
            checked_expected.append((field, True))
        else:
            checked_expected.append((field, False))
    return checked, checked_expected


@frontend.route('/local-authority/<local_authority_id>/header-details')
def header_details_for_authority(local_authority_id):
    url = current_app.config['STATUS_API'] + '/?organisation=' + local_authority_id
    result_data = fetch_validation_result(url)
    if bool(result_data):
        # headers_given = result_data.get('headers').get('given', [])
        headers_given = result_data[0].get('validated').get('result').get('columns').get('given', [])
        checked, checked_data_standard_headers = _check(headers_given, data_standard_headers)
        return render_template(
            'header-results.html',
            expected_headers=checked_data_standard_headers,
            checked=checked,
            data={'organisation': local_authority_id, 'url': url, 'result': result_data})
    else:
        return render_template(
            'header-results.html',
            data={'organisation': local_authority_id, 'url': url, 'result': result_data})


@frontend.route('/local-authority/<local_authority_id>')
def local_authority_results(local_authority_id):
    url = f"{current_app.config['STATUS_API']}?organisation={local_authority_id}"
    data = fetch_results(url)
    data.sort(key=lambda x: x['date'], reverse=True)
    return render_template('breakdown-by-authority.html', local_authority_id=local_authority_id, data=data, url=url)

# set the assetPath variable for use in
# jinja templates
@frontend.context_processor
def asset_path_context_processor():
    return {'assetPath': '/static/govuk-frontend/assets'}
