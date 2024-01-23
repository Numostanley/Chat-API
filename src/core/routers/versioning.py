"""This module contains utilities for the settings package."""
import logging


logger = logging.getLogger(__name__)


def get_api_version(variable: str, version: str = None):
    """This function returns the API_VERSION to be passed to the url, based on parameters passed."""
    try:
        if not isinstance(variable, str):  # checking the instance of the parameter(variable) passed
            raise Exception(
                'parameter (%s) must be a string alone or separated by commas' % variable
            )
        if not len(version) == 2:
            raise Exception(
                'length of (%s) must be 2 i.e only two strings must be specified '
                'which is v1, v2... or vN; where N is the number of the version'
                % version
            )
        try:
            list_versions = variable.split(',')
            if version and version in list_versions:
                return version
            elif version and version not in list_versions:
                return 'Invalid version parameter passed'
            return list_versions[-1]
        except IndexError as e:
            raise Exception(e, 'Index out of bound.')
    except KeyError as e:
        logger.error('get_api_version@Error')
        logger.error(e)
        return None
