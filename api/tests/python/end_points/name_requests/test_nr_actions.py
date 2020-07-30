"""
Integration tests for Name Request state transitions.
"""
import pytest
import json

from tests.python.end_points.common.http import build_test_query, build_request_uri
from tests.python.end_points.common.logging import log_request_path

from tests.python.unit.test_setup_utils import build_nr
from tests.python.end_points.common.http import get_test_headers
# Import token and claims if you need it
from tests.python.end_points.common.configuration import claims, token_header

from .configuration import API_BASE_URI

from namex.models import State, User
from namex.constants import NameRequestActions

"""
Add states
DRAFT	Unexamined name, submitted by a client
INPROGRESS	An examiner is working on this request
CANCELLED	The request is cancelled and cannot be changed
HOLD	A name approval was halted for some reason
APPROVED	Approved request, this is a final state
REJECTED	Rejected request, this is a final state
CONDITIONAL	Approved, but with conditions to be met. This is a final state
HISTORICAL	HISTORICAL
COMPLETED	COMPLETED - LEGACY state for completed NRs from NRO
EXPIRED	EXPIRED - LEGACY state for expired NRs from NRO
NRO_UPDATING	NRO_UPDATING - internal state used when updating records from NRO
COND-RESERVE	Temporary reserved state with consent required
RESERVED	Temporary reserved state between name available and paid.  Once paid it is set to APPROVED or CONDITIONAL approval.
"""

state_data = [
    # ('DRAFT', 'Unexamined name, submitted by a client'),
    # ('INPROGRESS', 'An examiner is working on this request'),
    # ('CANCELLED', 'The request is cancelled and cannot be changed'),
    # ('HOLD', 'A name approval was halted for some reason'),
    # ('APPROVED', 'Approved request, this is a final state'),
    # ('REJECTED', 'Rejected request, this is a final state'),
    # ('CONDITIONAL', 'Approved, but with conditions to be met. This is a final state'),
    # ('HISTORICAL', 'HISTORICAL'),
    # ('COMPLETED', 'COMPLETED - LEGACY state for completed NRs from NRO'),
    # ('EXPIRED', 'EXPIRED - LEGACY state for expired NRs from NRO'),
    # ('NRO_UPDATING', 'NRO_UPDATING - internal state used when updating records from NRO'),
    # TODO: These states are missing in Test DB
    ('COND-RESERVE', 'Temporary reserved state with consent required'),
    ('RESERVED', 'Temporary reserved state between name available and paid.  Once paid it is set to APPROVED or CONDITIONAL approval.')
]


@pytest.mark.skip
def add_states_to_db(states):
    for code, desc in states:
        state = State(cd=code, description=desc)
        state.save_to_db()


@pytest.mark.skip
def add_test_user_to_db():
    user = User(username='name_request_service_account', firstname='Test', lastname='User', sub='idir/name_request_service_account', iss='keycloak')
    user.save_to_db()


@pytest.mark.skip
def create_draft_nr(client, jwt, app):
    """
    Create a draft NR, using the API, to use as the initial state for each test.
    :param client:
    :param jwt:
    :param app:
    :return:
    """
    try:
        # Configure auth
        # token, headers = setup_test_token(jwt, claims, token_header)
        headers = get_test_headers()

        # Set up our test data
        add_states_to_db(state_data)
        add_test_user_to_db()

        nr = build_nr(State.DRAFT)
        # nr.requestTypeCd = 'CR'

        nr_data = nr.json()

        nr_data['names'] = [{
            "name": "BLUE HERON TOURS LTD.",
            "choice": "1",
            "designation": "LTD.",
            "name_type_cd": "CO",
            "consent_words": "",
            "conflict1": "BLUE HERON TOURS LTD.",
            "conflict1_num": "0515211"
        }]

        # New requests need to have these set
        nr_data['additionalInfo'] = ''
        nr_data['corpNum'] = ''
        nr_data['homeJurisNum'] = ''
        nr_data['natureBusinessInfo'] = 'Test'
        nr_data['previousRequestId'] = ''
        nr_data['tradeMark'] = ''
        nr_data['xproJurisdiction'] = ''
        nr_data['priorityCd'] = 'N'
        nr_data['entity_type'] = 'CR'
        nr_data['request_action'] = 'NEW'
        nr_data['stateCd'] = 'DRAFT'
        nr_data['english'] = True
        nr_data['nameFlag'] = False
        nr_data['submit_count'] = 0

        # Create a new DRAFT NR using the NR we just created
        request_uri = API_BASE_URI
        test_params = [{}]

        query = build_test_query(test_params)
        path = build_request_uri(request_uri, query)
        log_request_path(path)

        post_response = client.post(path, data=json.dumps(nr_data), headers=headers)

        if not post_response or post_response.status_code != 201:
            raise Exception('NR POST operation failed, cannot continue with PATCH test')

        return post_response
    except Exception as err:
        print(repr(err))


def test_draft_patch_edit(client, jwt, app):
    """
    Setup:
    Test:
    :param client:
    :param jwt:
    :param app:
    :return:
    """
    post_response = create_draft_nr(client, jwt, app)

    # Assign the payload to new nr var
    draft_nr = json.loads(post_response.data)
    assert draft_nr is not None

    # Take the response and edit it
    request_uri = API_BASE_URI + draft_nr.get('nrNum') + '/' + NameRequestActions.EDIT.value
    test_params = [{}]

    headers = get_test_headers()
    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    patch_response = client.patch(path, data=json.dumps({}), headers=headers)

    if not patch_response or patch_response.status_code != 200:
        raise Exception('NR PATCH operation failed')

    payload = json.loads(patch_response.data)
    assert payload is not None

    # Check state
    print('Assert that stateCd == DRAFT: ' + str(bool(payload.get('stateCd') == 'DRAFT')))
    assert payload.get('stateCd') == 'DRAFT'
    # Check applicant(s)
    # Check names
    # Check actions


def test_draft_patch_upgrade(client, jwt, app):
    """
    Setup:
    Test:
    :param client:
    :param jwt:
    :param app:
    :return:
    """
    post_response = create_draft_nr(client, jwt, app)

    # Assign the payload to new nr var
    draft_nr = json.loads(post_response.data)
    assert draft_nr is not None

    # Take the response and edit it
    request_uri = API_BASE_URI + draft_nr.get('nrNum') + '/' + NameRequestActions.UPGRADE.value
    test_params = [{}]

    headers = get_test_headers()
    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    patch_response = client.patch(path, data=json.dumps({}), headers=headers)

    if not patch_response or patch_response.status_code != 200:
        raise Exception('NR PATCH operation failed')

    payload = json.loads(patch_response.data)
    assert payload is not None

    # Check state
    print('Assert that stateCd == DRAFT: ' + str(bool(payload.get('stateCd') == 'DRAFT')))
    assert payload.get('stateCd') == State.DRAFT
    # Check applicant(s)
    # Check names
    # Check actions


def test_draft_patch_cancel(client, jwt, app):
    """
    Setup:
    Test:
    :param client:
    :param jwt:
    :param app:
    :return:
    """
    post_response = create_draft_nr(client, jwt, app)

    # Assign the payload to new nr var
    draft_nr = json.loads(post_response.data)
    assert draft_nr is not None

    # Take the response and edit it
    request_uri = API_BASE_URI + draft_nr.get('nrNum') + '/' + NameRequestActions.CANCEL.value
    test_params = [{}]

    headers = get_test_headers()
    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    patch_response = client.patch(path, data=json.dumps({}), headers=headers)

    if not patch_response or patch_response.status_code != 200:
        raise Exception('NR PATCH operation failed')

    payload = json.loads(patch_response.data)
    assert payload is not None

    # Check state
    print('Assert that stateCd == CANCELLED: ' + str(bool(payload.get('stateCd') == 'CANCELLED')))
    assert payload.get('stateCd') == State.CANCELLED
    # Check applicant(s)
    # Check names
    # Check actions


def test_draft_patch_refund(client, jwt, app):
    """
    Setup:
    Test:
    :param client:
    :param jwt:
    :param app:
    :return:
    """
    post_response = create_draft_nr(client, jwt, app)

    # Assign the payload to new nr var
    draft_nr = json.loads(post_response.data)
    assert draft_nr is not None

    # Take the response and edit it
    request_uri = API_BASE_URI + draft_nr.get('nrNum') + '/' + NameRequestActions.REFUND.value
    test_params = [{}]

    headers = get_test_headers()
    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    patch_response = client.patch(path, data=json.dumps({}), headers=headers)

    if not patch_response or patch_response.status_code != 200:
        raise Exception('NR PATCH operation failed')

    payload = json.loads(patch_response.data)
    assert payload is not None

    # Check state
    print('Assert that stateCd == DRAFT: ' + str(bool(payload.get('stateCd') == 'DRAFT')))
    assert payload.get('stateCd') == State.DRAFT
    # Check applicant(s)
    # Check names
    # Check actions


def test_draft_patch_reapply(client, jwt, app):
    """
    Setup:
    Test:
    :param client:
    :param jwt:
    :param app:
    :return:
    """
    post_response = create_draft_nr(client, jwt, app)

    # Assign the payload to new nr var
    draft_nr = json.loads(post_response.data)
    assert draft_nr is not None

    # Take the response and edit it
    request_uri = API_BASE_URI + draft_nr.get('nrNum') + '/' + NameRequestActions.REAPPLY.value
    test_params = [{}]

    headers = get_test_headers()
    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    patch_response = client.patch(path, data=json.dumps({}), headers=headers)

    if not patch_response or patch_response.status_code != 200:
        raise Exception('NR PATCH operation failed')

    payload = json.loads(patch_response.data)
    assert payload is not None

    # Check state
    print('Assert that stateCd == DRAFT: ' + str(bool(payload.get('stateCd') == 'DRAFT')))
    assert payload.get('stateCd') == State.DRAFT
    # Check applicant(s)
    # Check names
    # Check actions


def test_draft_patch_resend(client, jwt, app):
    """
    Setup:
    Test:
    :param client:
    :param jwt:
    :param app:
    :return:
    """
    post_response = create_draft_nr(client, jwt, app)

    # Assign the payload to new nr var
    draft_nr = json.loads(post_response.data)
    assert draft_nr is not None

    # Take the response and edit it
    request_uri = API_BASE_URI + draft_nr.get('nrNum') + '/' + NameRequestActions.RESEND.value
    test_params = [{}]

    headers = get_test_headers()
    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    patch_response = client.patch(path, data=json.dumps({}), headers=headers)

    if not patch_response or patch_response.status_code != 200:
        raise Exception('NR PATCH operation failed')

    payload = json.loads(patch_response.data)
    assert payload is not None

    # Check state
    print('Assert that stateCd == DRAFT: ' + str(bool(payload.get('stateCd') == 'DRAFT')))
    assert payload.get('stateCd') == State.DRAFT
    # Check applicant(s)
    # Check names
    # Check actions
