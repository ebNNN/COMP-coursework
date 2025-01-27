from src.data_store import data_store
from src.error import InputError, AccessError
import re
import string
import random
import smtplib, ssl
from email.mime.text import MIMEText

from src.helper import generate_new_session_id, \
                        encrypt, generate_jwt,  \
                        decode_jwt,             \
                        validation,             \
                        SECRET
from tests.admin_test import GLOBAL_OWNERS, MEMBERS

def auth_login_v2(email, password):

    '''
    <Brief description of what the function does>

    Arguments:
        <email> (<string>)    - <user's email>
        <password> (<string>)    - <user's password>

    Exceptions:
        InputError  - Occurs when email entered does not belong to a user
                            and password is not correct

    Return Value:
        Returns <auth_user_id> on <User has successfully logined>
    '''

    store = data_store.get()

    #Convert email to lower
    new_email = email.lower()

    #Check to determine whether email and password are correct.
    validation(new_email, password)


    for user in store['users']:
        if user['email'] == new_email and user['password'] == encrypt(password):
            session_id = generate_new_session_id()
            user['session_ids'].append(session_id)

            return {
                'auth_user_id'  : user['u_id'],
                'token'         : generate_jwt(user['u_id'], session_id)
            }

    #Email entered does not belong to any user
    raise InputError("New Email")


def auth_register_v2(email, password, name_first, name_last):
    '''
    <Registers the user after checking  to make sure all information given is valid>

    Arguments:
        <email> (<string>)    - <Email given by user>
        <password> (<string>)    - <Password given by user>
        <name_first> (<string>)    - <First name given by user>
        <name_last> (<string>)    - <Last name given by user>

    Exceptions:
        InputError  - Occurs when email entered is not a valid email.
        InputError  - Occurs when email address is already being used by another user.
        InputError  - Occurs when length of password is less than 6 characters.
        InputError  - Occurs when length of name_first is not between 1 and 50 characters inclusive.
        InputError  - Occurs when length of name_last is not between 1 and 50 characters inclusive.

    Return Value:
        Returns <auth_user_id> on <User has correctly registered>
    '''

    store = data_store.get()

    #Convert email to lower
    new_email = email.lower()

    #Check to determine whether password and email are valid.
    validation(new_email, password)

    #Check for duplicated emails.
    for user in store['users']:
        if user['email'] == new_email:
            raise InputError("Email duplicate")

    #Check whether first name is valid.
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("First name is invalid")

    #Check whether last name is valid.
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Last name is invalid")

    #Creates a handle for new user
    handle = name_first + name_last
    handle = handle.lower()
    handle = re.sub(r'[^a-zA-Z0-9]', '', handle)

    if len(handle) > 20:
        handle = handle[:20]
    n = -1
    for user in store['users']:
        if user['handle_str'][:20] == handle:
            n += 1
    if n >= 0:
        handle = handle + str(n)

    session_id = generate_new_session_id()

    # Adds a new user to data_store["users"]
    new_id = len(store['users']) + 1
    permission_id = MEMBERS
    # the first global owner is the first user registered with auth_register_v1()
    if new_id == 1:
        permission_id = GLOBAL_OWNERS
    store['users'].append({
            'u_id'           : new_id,
            'email'          : new_email,
            'name_first'     : name_first,
            'name_last'      : name_last,
            'password'       : encrypt(password),
            'handle_str'     : handle,
            'session_ids'    : [session_id],
            'permission_id'  : permission_id,
            'notifications' : [],
            'profile_img_url': None,
            'reset_code'     : None
        })

    return {
        'auth_user_id'  : new_id,
        'token'         : generate_jwt(new_id, session_id)
    }


def auth_logout_v1(token):
    '''
    <Given an active token, invalidates the token to log the user out.>

    Arguments:
        <token> (<string>)    - <token generated by u_id and session_ids>

    Exceptions:
        N/A

    Return Value:
        Returns <{}>
    '''
    store = data_store.get()
    unwrap = decode_jwt(token)
    for user in store['users']:
        if user['u_id'] == unwrap['u_id']:
            if unwrap['session_ids'] in user['session_ids']:
                user['session_ids'].remove(unwrap['session_ids'])
            else:
                raise AccessError(description = 'already_logged_out')


    return {}


def auth_password_request_v1(email):

    #Gmail used for sending the rest code : Gmail:comp1531streams@gmail.com Password:Someone123
    email = email.lower()

    store = data_store.get()

    #store a reset code so that it can find the account in auth_password_reset_v1
    for user in store['users']:

        if user['email'] == email:

            #make code
            reset_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1,8))

            #send code to email
            sender = 'comp1531streams@gmail.com'
            receivers = email
            body_of_email = "Your passwords reset code is: %s . If you haven't recently requested a password request code, then please ignore this email." % reset_code

            msg = MIMEText(body_of_email, 'html')
            msg['Subject'] = 'Streams password reset'
            msg['From'] = sender
            msg['To'] = ','.join(receivers)

            s = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
            s.login(user = 'comp1531streams@gmail.com', password = 'Someone123')
            s.sendmail(sender, receivers, msg.as_string())
            s.quit()

            user['reset_code'] = reset_code

    return{}

def auth_password_reset_v1(reset_code, new_password):
    validation('temp@gmail.com', new_password)
    store = data_store.get()
    for user in store['users']:
        if user['reset_code'] == reset_code:
            user['password'] = encrypt(new_password)
            user['reset_code'] = None
            return {}

    raise InputError("Invalid reset_code")
