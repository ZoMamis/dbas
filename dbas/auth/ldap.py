import ldap
import os

from dbas.logger import logger
from dbas.strings.keywords import Keywords as _


def verify_ldap_user_data(nickname, password, _tn):
    """
    Tries to authenticate the user with nickname and password

    :param nickname: users nickname for LDAP
    :param password: users password for LDAP
    :param _tn: Translator
    :return: [firstname, lastname, gender, email] on success else None
    """
    logger('ldap', 'verify_ldap_user_data', 'main')
    try:
        server = os.environ.get('DBAS_HHU_LDAP_SERVER', None)
        base = os.environ.get('DBAS_HHU_LDAP_BASE', None)
        scope = os.environ.get('DBAS_HHU_LDAP_ACCOUNT_SCOPE', None)
        filter = os.environ.get('DBAS_HHU_LDAP_ACCOUNT_FILTER', None)
        firstname = os.environ.get('DBAS_HHU_LDAP_ACCOUNT_FIRSTNAME', None)
        lastname = os.environ.get('DBAS_HHU_LDAP_ACCOUNT_LAST', None)
        title = os.environ.get('DBAS_HHU_LDAP_ACCOUNT_TITLE', None)
        email = os.environ.get('DBAS_HHU_LDAP_ACCOUNT_EMAIL', None)
        logger('ldap', 'verify_ldap_user_data', 'parsed data')

        if any([server, base, scope, filter, firstname, lastname, title, email]) is None:
            return {'error': _tn.get(_.internalKeyError) + ' ' + _tn.get(_.pleaseTryAgainLaterOrContactUs)}

        server = server.replace('\'', '')
        base = base.replace('\'', '')
        scope = scope.replace('\'', '')
        filter = filter.replace('\'', '')
        firstname = firstname.replace('\'', '')
        lastname = lastname.replace('\'', '')
        title = title.replace('\'', '')
        email = email.replace('\'', '')

        logger('ldap', 'verify_ldap_user_data', 'ldap.initialize(\'{}\')'.format(server))
        ldaps = ldap.initialize(server)
        ldaps.set_option(ldap.OPT_NETWORK_TIMEOUT, 5.0)
        logger('ldap', 'verify_ldap_user_data', 'ldap.simple_bind_s(\'{}{}\', \'***\')'.format(nickname, scope))
        ldaps.simple_bind_s(nickname + scope, password)
        logger('ldap', 'verify_ldap_user_data',
               'l.search_s({}, ldap.SCOPE_SUBTREE, (\'{}={}\'))[0][1]'.format(base, filter, nickname))
        user = ldaps.search_s(base, ldap.SCOPE_SUBTREE, filter + '=' + nickname)[0][1]

        firstname = user[firstname][0].decode('utf-8')
        lastname = user[lastname][0].decode('utf-8')
        title = user[title][0].decode('utf-8')
        gender = 'm' if 'Herr' in title else 'f' if 'Frau' in title else 'n'
        email = user[email][0].decode('utf-8')
        logger('ldap', 'verify_ldap_user_data', 'success')

        data = {
            'firstname': firstname,
            'lastname': lastname,
            'gender': gender,
            'email': email,
            'error': False
        }
        return data

    except ldap.INVALID_CREDENTIALS as e:
        logger('ldap', 'verify_ldap_user_data', 'ldap credential error: ' + str(e))
        data = {'error': _tn.get(_.userPasswordNotMatch)}
        return data

    except ldap.SERVER_DOWN as e:
        logger('ldap', 'verify_ldap_user_data', 'can\'t reach server within 5s: ' + str(e))
        data = {'error': _tn.get(_.serviceNotAvailable) + '. ' + _tn.get(_.pleaseTryAgainLaterOrContactUs)}
        return data

    except ldap.OPERATIONS_ERROR as e:
        logger('ldap', 'verify_ldap_user_data', 'OPERATIONS_ERROR: ' + str(e))
        data = {'error': _tn.get(_.internalKeyError) + ' ' + _tn.get(_.pleaseTryAgainLaterOrContactUs)}
        return data
