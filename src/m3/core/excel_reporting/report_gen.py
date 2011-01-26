# -*- coding: utf-8 -*-

import subprocess as sub
from django.conf import settings
from django.utils import importlib, simplejson
import sys
import os
from django.template import loader
from django.template.context import Context
import datetime
import decimal

__all__ = ['BaseReport', 'ReportGeneratorError', 'ReportGeneratorNotResponse']

#============================== ПАРАМЕТРЫ ================================

def __get_template_path():
    ''' Ищем корневую папку проекта '''
    mod = importlib.import_module(settings.SETTINGS_MODULE)
    settings_abs_path = os.path.dirname(mod.__file__)
    return settings_abs_path
    
JAR_FULL_PATH = os.path.join(os.path.dirname(__file__), 'report.jar')
DEFAULT_REPORT_TEMPLATE_PATH = __get_template_path()

#============================= ИСКЛЮЧЕНИЯ ================================

class ReportGeneratorNotResponse(Exception):
    pass

class ReportGeneratorError(Exception):
    pass

#============================== ЛОГИКА ===================================


def __check_process(encoding_name, process, result_err):
    # Если не завершился сам, то поможем
    if process.poll() is None:
        process.terminate()
        raise ReportGeneratorNotResponse(JAR_FULL_PATH + ' ' + encoding_name)
    # Если процесс навернулся, надо вежливо вернуть ошибку
    if process.returncode != 0:
        raise ReportGeneratorError(result_err)
    

class ReportJSONEncoder(simplejson.JSONEncoder):
    """
    Сырой словарь с данными может содержать типы данных не поддерживаемых JSON.
    Для этого определяем свои правила сериализации типов (по аналогии с джанговским)
    """
    # Немецкий формат (не менять! я жестко прописал java генераторе)
    DATE_FORMAT = "%d.%m.%Y"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return "#m3dt#" + o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            return "#m3dd#" + o.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return "#m3tt#" + o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(ReportJSONEncoder, self).default(o)


def make_report_from_object(obj, dump_to_file = None):
    '''
    Вызывает генератор отчета и передает ему объект с исходными данными
    @param obj: Объект с данными
    @param dump_to_file: Файл в который записывается результат сериализации (для отладки)
    '''
    assert isinstance(obj, dict)
    
    indent = 4 if dump_to_file != None else 0;
    result = simplejson.dumps(obj, skipkeys = True, ensure_ascii = False, cls = ReportJSONEncoder, indent = indent)
        
    # Для отладки пишем результат в файл
    if dump_to_file is not None:
        assert isinstance(dump_to_file, str)
        with open(dump_to_file, "w") as f:
            f.write(result.encode("utf-8"))
    
    make_report_from_json_string(result)
    

def make_report_from_json_string(json_str):
    '''
    Вызавает генератор отчета и передает ему в качестве исходных данных JSON строку.
    @param json_str: Строка JSON
    '''
    # При передаче данных через стандартные потоки ввода/вывода
    # важно кодировать/декодировать в кодировку консоли
    if hasattr(sys.stdout, 'encoding'):
        encoding_name = sys.stdout.encoding
    else:
        # Под нормальным сервером перекодировка не нужна
        encoding_name = 'utf-8'
    process = sub.Popen(['java', '-jar', JAR_FULL_PATH, encoding_name], 
                        stdin = sub.PIPE, stdout = sub.PIPE, stderr = sub.PIPE)
    result_out, result_err = process.communicate(input = json_str.encode(encoding_name))
    __check_process(encoding_name, process, result_err)
    
    
def make_html_report_from_object(obj):
    pass
 
 
class BaseReport:
    ''' Базовый класс для создания отчетов '''
    
    # Определяет путь к файлу шаблона относительно папки шаблонов
    template_name = ''
    html_template_name = ''
    
    # Определяет путь к файлу результата относительно папки результатов
    result_name = ''
    # Строка в которую отрендерился html шаблон
    html_result_string = ''
    
    def _norm_path(self, path):
        if sys.platform.find('linux') > -1:
            # os.path.normpath - нормализует неправильно
            path = path.replace('\\', '/')
        return path
    
    def make_report(self, *args, **kwargs):
        ''' Запускает формирование отчета '''
        obj = self.collect(*args, **kwargs)
        if not isinstance(obj, dict):
            raise ReportGeneratorError("Collected data must be packed in the dictionary")
        
        # С версии 2.0 политика партии поменялась
        # Теперь отчеты могут генериться в несколько форматов, соответственно некоторые из них нам
        # нужны не всегда. Поэтому если имя до одного из шаблонов не задано, это не вызывает ошибку,
        # а отключает генерацию по данному шаблону
        if len(self.template_name) > 0:
            if len(self.result_name) == 0:
                raise ReportGeneratorError("Field result_name must be overrided")
            # Создаем абсолютные пути
            tfp = os.path.join(DEFAULT_REPORT_TEMPLATE_PATH, self.template_name)
            ofp = os.path.join(DEFAULT_REPORT_TEMPLATE_PATH, self.result_name)
            tfp = self._norm_path(tfp)
            ofp = self._norm_path(ofp)
            obj["TEMPLATE_FILE_PATH"] = tfp
            obj["OUTPUT_FILE_PATH"]   = ofp

            #Если пытаемся сохранить файл в несуществующую директорию, то попробуем ее предварительно создать
            if os.path.exists(ofp) == False:
                try:
                    cat = os.path.split(ofp)[0]
                    os.makedirs(cat)
                except :
                    raise ReportGeneratorError("Can't access to specified result file path ")

            # Тут генерится экселька
            make_report_from_object(obj)
        
        if len(self.html_template_name) > 0:
            tfp = os.path.join(DEFAULT_REPORT_TEMPLATE_PATH, self.html_template_name)
            tfp = self._norm_path(tfp)
            # Загружаем шаблон из файла
            self._temp = loader.get_template(tfp)
            self._cont = Context(obj)
            
    def get_html_result(self, params):
        '''
        Рендерит HTML отчет на основе контекста собраннаго в make_report и дополнительных
        параметров **params. Возвращает HTML строку.
        '''
        assert isinstance(params, dict)
        self._cont.update(params)
        return self._temp.render(self._cont)
    
    def collect(self):
        ''' Функция отвечающая за формирование данных '''
        raise NotImplemented("The function of data collection should be overrided in child classes")
    

