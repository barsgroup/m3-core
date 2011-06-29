#coding:utf-8
from django.conf import settings

import urllib2
from m3.contrib.ssacc_client.exceptions import SSACCException
from m3.contrib.ssacc_client.results import (BaseResult, ErrorResult,
    ProfileRatesResult)

__author__ = 'Excinsky'

##############################################################################
#Обращения к веб-сервисам системы
##############################################################################
#TODO(Excinsky): Превратить в объект

try:
    #Получаем расположение ссакосервера.
    SSACC_SERVER = settings.SSACC_SERVER
except AttributeError:
    SSACC_SERVER = 'http://localhost'

def try_to_connect_to_ssacc_url_and_get_request_result(connect_url):
    """
    Подключается к SSACC серваку, и получает ответ, либо выбрасывает ошибку.

    @param connect_url: добавочный урл на сервере.
    @raise SSACCException
    @return: str
    """
    try:
        request = urllib2.urlopen(SSACC_SERVER + connect_url)
        result_xml = request.read()
    except urllib2.HTTPError, e:
        raise SSACCException(u'Не удалось соединиться с SSACC сервером.')
    return result_xml

def check_if_result_is_ok_and_return_parsed_result(result_xml,
        additional_result_type):
    """
    Превращает пришедшую XML во враппер-объект.

    Возвращает ErrorResult, или результат, необходимый пользователю.

    @param result_xml: XML из которого будут делать враппер.
    @type result_xml: string.
    @param additional_result_type: Тип объекта-враппера, если не XML не сообщает
        об ошибках.
    @type additional_result_type: BaseResult child class.
    @return: BaseResult child instance.
    """
    is_result_ok = BaseResult.is_result_ok(result_xml)
    if is_result_ok:
        result_type = additional_result_type
    else:
        result_type = ErrorResult
    result = BaseResult.parse_xml_to_result(result_xml, result_type)
    return result

def server_ssacc_ping():
    """
    Обращение к системе за пустым запросом.

    @raise: SSACCException.
    @return: OperationResult or ErrorResult
    """
    ping_url = '/ssacc/ping'
    result_xml = try_to_connect_to_ssacc_url_and_get_request_result(ping_url)

    result = check_if_result_is_ok_and_return_parsed_result(result_xml,
        ProfileRatesResult)
    return result

def server_ssacc_profile_rates(account_id):
    """
    Обращение к системе за тарифным планом аккаунта.

    @return: OperationResult or ErrorResult
    """
    profile_url = '/ssacc/profile/rates'
    result_xml = try_to_connect_to_ssacc_url_and_get_request_result(profile_url)

    result = check_if_result_is_ok_and_return_parsed_result(result_xml,
        ProfileRatesResult)
    return result

def server_ssacc_availability(account_id):
    """
    Обращение к системе за возможностью использования.

    @return: AvailabilityResult or ErrorResult
    """
    profile_url = '/ssacc/profile/availability'
    result_xml = try_to_connect_to_ssacc_url_and_get_request_result(profile_url)

    result = check_if_result_is_ok_and_return_parsed_result(result_xml,
        ProfileRatesResult)
    return result
  