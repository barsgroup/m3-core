#coding:utf-8

import uno
import os
import datetime
import decimal
from django.conf import settings
from django.utils import importlib
from com.sun.star.beans import PropertyValue
from com.sun.star.connection import NoConnectException


def __get_template_path():
    ''' Ищем корневую папку проекта '''
    mod = importlib.import_module(settings.SETTINGS_MODULE)
    settings_abs_path = os.path.dirname(mod.__file__)
    return settings_abs_path
    
DEFAULT_REPORT_TEMPLATE_PATH = __get_template_path()

IMAGE_REGEX = '<img .*>'

VARIABLE_REGEX  = '#[:alpha:]+((_)*[:digit:]*[:alpha:]*)*#'

TEMPORARY_SHEET_NAME = 'template_zw'

class ReportGeneratorException(Exception):
    pass

class OOParserException(Exception):
    pass
    
class OORunner(object):
    '''
    Запускает, останавливает и соединяется с сервером OpenOffice
    '''
    # Порт, на котором будет запущен сервер
    PORT = 8010
    
    CONTEXT = None
    
    # Количество попыток соединения с сервером 
    CONNECTION_RETRY_COUNT = 5            

    @staticmethod
    def get_desktop(start=False):
        '''
        Запускает сервер (если start = True), и возвращает объект Desktop
        '''        
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext)
        if start:
            OORunner.start_server()   
        
        # Пытаемся соединиться с сервером
        for i in range(OORunner.CONNECTION_RETRY_COUNT):
            try:
                OORunner.CONTEXT = resolver.resolve("uno:socket,host=localhost,port=%d;urp;StarOffice.ComponentContext" % OORunner.PORT)
            except NoConnectException:
                raise ReportGeneratorException, "Не удалось соединиться с сервером openoffice на порту %d" % OORunner.PORT    
        
        desktop = OORunner.CONTEXT.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", OORunner.CONTEXT)
        if not desktop:
            raise ReportGeneratorException, "Не удалось создать объект рабочей области Desktop на порту %d" % OORunner.PORT
        
        return desktop    
                              

class OOParser(object):
    '''
    Этот класс преобразовывает текст в соответствии с языком шаблонов.
    '''        
                
    def find_image_tags(self, document):
        '''
        Находит, и возвращает в списке все теги изображений. 
        ''' 
        return self.find_regex(document, IMAGE_TAG)        
               
    def find_and_replace(self, document, regex, replace):
        '''
        Находит все строки, соответствующие регулярному выражению(задается строкой,
        по правилам опенофиса), и заменяет их на replace. 
        Если в document передана область ячеек таблицы, замена будет происходить 
        только в ней. 
        '''
        replace_descriptor = document.createReplaceDescriptor()
        replace_descriptor.SearchRegularExpression = True
        replace_descriptor.SearchString = regex
        replace_descriptor.ReplaceString = replace
        document.replaceAll(replace_descriptor)
    
    def find_regex(self, document, regex):
        '''
        Находит все строки, соответствующие регулярному выражению(задается строкой,
        по правилам опенофиса). 
        Возвращает список удовлетворяющих регулярному выражению строк.
        '''
        result = []
        search_descriptor = document.createSearchDescriptor()
        search_descriptor.SearchRegularExpression = True
        search_descriptor.SearchString = regex
        found = document.findFirst(search_descriptor)
        while found:
            result.append(found.String)
            found = document.findNext(found.End, search_descriptor)
        return result
    
    def create_sections(self, document, report_object):
        '''
        Находит в листе Excel'я аннотации и составляет список секций. Считается, 
        что начало секции в шаблоне обозначается знаком '+' (напр., '+Шапка'), конец
        секции - знаком '-' ('-Шапка')
        '''   
        all_sections = {}
        annotations = document.getAnnotations()
        annotations_iter = annotations.createEnumeration()
        while annotations_iter.hasMoreElements():
            annotation = annotations_iter.nextElement()
            value = annotation.String
            position = annotation.Position
            section_names = value.split()
            for section_name in section_names:
                section_name = section_name.strip()
                if section_name[0] in ['+', '-']:
                    if all_sections.has_key(section_name[1:]):
                        all_sections[section_name[1:]].add_new_cell(position)
                    else:
                        new_section = Section()
                        new_section.name = section_name[1:]
                        new_section.report_object = report_object
                        new_section.add_new_cell(position)
                        all_sections[section_name[1:]] = new_section    
                else:
                    raise OOParserException, "Секции в ячейке (%s, %s) \
                    должны начинаться со знака '+' или '-'" %(position.Row+1, position.Column+1)            
        for section in all_sections.values():
            if not section.is_valid():
                raise OOParserException, "Неверно задана секция %s. \
                Определена одна из двух ячеек" %section.name    
        return all_sections  
    
    def convert_value(self, value):
        '''
        Преобразовывает значение в тип, подходящий для отображения в openoffice
        '''       
        if (isinstance(value, (datetime.date, datetime.datetime, datetime.time))):
            return str(value)  
        elif isinstance(value, basestring):
            return value    
        elif isinstance(value, (int, float, decimal.Decimal, long)):
            return str(value).replace('.', ',')        
        else:
            return repr(value)           


class Section(object):
    '''
    Класс, описывающий секции в шаблоне Excel
    '''
    
    def __init__(self, name=None, left_cell_addr=None, right_cell_addr=None, 
                 report_object=None):
        #Название секции
        self.name = name
        #Верхняя левая ячейка - объект com.sun.star.table.CellAddress
        self.left_cell_addr = left_cell_addr
        #Нижняя правая ячейка - объект com.sun.star.table.CellAddress
        self.right_cell_addr = right_cell_addr
        #Объект отчета, в контексте которого будет выводиться секция
        self.report_object = report_object
        
    def add_new_cell(self, cell):
        '''
        Добавляет новую ячейку. Если одна из ячеек не определена, добавляет 
        ячейку как левую. Если добавляется вторая, определяется, какая из них левая
        '''
        #Если это первая добавляемая ячейка
        if not self.left_cell_addr and not self.right_cell_addr:
            self.left_cell_addr = cell
        #Если пытаются добавить третью ячейку, ругаемся    
        elif self.left_cell_addr and self.right_cell_addr:
            raise OOParserException, "Секция %s задается двумя ячейками, невозможно добавить третью." %self.name    
        #Если левая ячейка уже задана, определяем, действительно ли она левая    
        elif self.left_cell_addr:
            if (cell.Row >= self.left_cell_addr.Row) and (cell.Column >= self.left_cell_addr.Column):
                self.right_cell_addr = cell
            elif (cell.Row < self.left_cell_addr.Row) and (cell.Column < self.left_cell_addr.Column):   
                self.right_cell_addr = self.left_cell_addr
                self.left_cell_addr = cell     
            # Секция задана неверно, не записываем такую ерунду
            else:    
                raise OOParserException, "Неверно задана секция %s. \
                Определите верхнюю левую и нижнюю правую ячейки" %self.name
        # И то же самое, если задана правая ячейка
        elif self.right_cell_addr:
            if (cell.Row >= self.right_cell_addr.Row) and (cell.Column >= self.right_cell_addr.Column):
                self.left_cell_addr = self.right_cell_addr
                self.right_cell_addr = cell
            elif (cell.Row < self.left_cell_addr.Row) and (cell.Column < self.left_cell_addr.Column):
                self.left_cell_addr = cell     
            # Секция задана неверно, не записываем такую ерунду
            else:    
                raise OOParserException, "Неверно задана секция %s. \
                Определите верхнюю левую и нижнюю правую ячейки" %self.name                 
            
    def is_valid(self):
        '''
        Определяет, обе ли ячейки заданы
        '''        
        return self.left_cell_addr and self.right_cell_addr
    
    def copy(self, context, document, src_sheet, cell):
        '''
        Копирует секцию в документе из листа src_sheet начиная с ячейки cell
        Ячейку можно получить из листа так: cell = sheet.getCellByPosition(2,5)     
        '''
    
        dispatcher = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.DispatchHelper", context) 
        section_range = src_sheet.getCellRangeByPosition(self.left_cell_addr.Column,
                                                      self.left_cell_addr.Row,
                                                      self.right_cell_addr.Column,
                                                      self.right_cell_addr.Row)
        document.CurrentController.select(section_range)
        prop = PropertyValue()
        prop.Name = "Flags"
        #Так задаются флаги: A - all or S - string V - value D - date, time F - formulas  
        #N - notes T - formats
        # Не копируем комментарии 
        prop.Value = "SVDFT"
        # Копируем выделенную секцию
        dispatcher.executeDispatch(document.getCurrentController().getFrame(), ".uno:Copy", "", 0, ())
        # Выделяем ячейку, в которую будет вставляться секция
        document.CurrentController.select(cell)
        # Вставляем секцию
        dispatcher.executeDispatch(document.getCurrentController().getFrame(), ".uno:InsertContents", "", 0,(prop,))
        
    def flush(self, params, vertical=True):
        '''
        Выводит секцию в отчет
        '''
        section_width = abs(self.left_cell_addr.Column - self.right_cell_addr.Column)+1
        section_height = abs(self.left_cell_addr.Row - self.right_cell_addr.Row)+1
        x, y = self.report_object.find_section_position(vertical, section_width, section_height)
        context = self.report_object.context
        document = self.report_object.document
        #Лист с результатом - второй по счету
        dest_sheet = document.getSheets().getByIndex(1)
        dest_cell = dest_sheet.getCellByPosition(x,y)
        if document.getSheets().hasByName(TEMPORARY_SHEET_NAME):
            src_sheet = document.getSheets().getByName(TEMPORARY_SHEET_NAME)
        else:
            raise ReportGeneratorException, "Невозможно вывести секцию в отчет, \
            лист-шаблон отсутствует. Возможно, отчет уже был отображен."    
        self.copy(context, document, src_sheet, dest_cell)
        section_range = dest_sheet.getCellRangeByPosition(x,y,x+section_width-1,y+section_height-1)
        parser = OOParser()
        for key, value in params.items():
            if not isinstance(key, str):
                raise ReportGeneratorException, "Значение ключа для подстановки в шаблоне должно быть строковым"
            value = parser.convert_value(value)
            parser.find_and_replace(section_range, u'#'+key+u'#', value)    
        #Если не все переменные в шаблоне были заменены, стираем оставшиеся
        parser.find_and_replace(section_range, VARIABLE_REGEX, '')
        #Задаем размеры строк и столбцов
        self.set_columns_width(x, src_sheet, dest_sheet)
        self.set_rows_height(y, src_sheet, dest_sheet)
        
    def set_rows_height(self, y, src_sheet, dest_sheet):
        '''
        Выставляет высоту строк в листе отчета в соответствиии с высотой строк 
        в секции
        '''    
        dest_row_index = y
        for src_row_index in range(self.left_cell_addr.Row,self.right_cell_addr.Row+1):
            #Если у ряда уже устанавливали высоту, перезаписывать не будем
            if dest_row_index in self.report_object.defined_height_rows:
                return
            else:
                #Если у ряда выставлена автовысота, устанавливать высоту не нужно 
                if src_sheet.getRows().getByIndex(src_row_index).OptimalHeight:
                    dest_sheet.getRows().getByIndex(dest_row_index).OptimalHeight = True
                else:
                    dest_sheet.getRows().getByIndex(dest_row_index).Height = \
                    src_sheet.getRows().getByIndex(src_row_index).Height
                self.report_object.defined_height_rows.append(dest_row_index)
            dest_row_index+=1    
    
    def set_columns_width(self, x, src_sheet, dest_sheet):
        '''
        Выставляет ширину колонок в листе отчета в соответствиии с шириной колонок 
        в секции
        '''
        dest_column_index = x
        for src_column_index in range(self.left_cell_addr.Column,self.right_cell_addr.Column+1):
            #Если у колонки уже устанавливали ширину, перезаписывать не будем
            if not(dest_column_index in self.report_object.defined_width_columns):
                dest_sheet.getColumns().getByIndex(dest_column_index).Width = \
                src_sheet.getColumns().getByIndex(src_column_index).Width
                self.report_object.defined_width_columns.append(dest_column_index)
            dest_column_index+=1                     
                        
                    
class OOImage(object):
    '''
    Класс для удобной работы с изображениями. 
    '''    
    
    def __init__(self, path, document):
        '''
        Создает объект com.sun.star.drawing.GraphicObjectShape, который может
        быть встроен в документ(а не просто выставлен линк на изображение).
        Нужно для того, чтобы не быть "привязанным" к тому компьютеру, где документ 
        был изначально создан.
        '''  
        image_url = path_to_file_url(path)        
        image = document.createInstance("com.sun.star.drawing.GraphicObjectShape") 
        bitmap = document.createInstance( "com.sun.star.drawing.BitmapTable" )
        #Просто рандомное имя image; это такой хитрый трюк получить само изображение,
        #а не ссылку на него
        if not bitmap.hasByName('image'):
            bitmap.insertByName('image', image_url)
        image_url = bitmap.getByName( 'image' )
        image.GraphicURL = image_url
        self.image = image
                
    def set_image_size(self, width, height):
        '''
        Задает свойства ширина и высота для изображения в единицах 1/100 миллиметра
        '''                
        size = uno.createUnoStruct('com.sun.star.awt.Size')
        size.Width = width
        size.Height = height
        self.image.Size = size
        
    def set_image_location(self, x, y):
        '''
        Задает положение изображения как позицию верхнего левого угла в единицах
        1/100 миллиметра
        '''
        point = uno.createUnoStruct('com.sun.star.awt.Point')
        point.X = x
        point.Y = y
        self.image.Position = point 
        
    def insert_into_text_document(self, document):
        '''
        Вставляет в документ изображение.В случае вставки в электронную таблицу
        нужно передавать лист         
        '''       
        document.getDrawPage().add(image)  
        
                                 
def create_document(desktop, path):
    '''
    Создает объект документа рабочей области из файла path.
    '''
    if path:
        #В windows, несмотря на режим запуска OO с опцией headless, новые 
        # документы открываются в обычном режиме. Это свойство делает документ
        # скрытым 
        prop = PropertyValue()
        prop.Name = "Hidden"
        prop.Value = True
        file_url = path_to_file_url(path)
        return desktop.loadComponentFromURL(file_url, "_blank", 0, (prop,))
    else:
        return desktop.getCurrentComponent()
             
             
def save_document_as(document, path, properties):
    '''
    Сохраняет документ по указанному пути со свойствами property. property - 
    объект com.sun.star.beans.PropertyValue
    '''           
    file_url = path_to_file_url(path)
    document.storeToURL(file_url, properties)
        

def path_to_file_url(path):
    '''
    Преобразует путь в url, понятный для uno.
    '''
    abs_path = os.path.abspath(path)
    file_url = uno.systemPathToFileUrl(abs_path)
    return file_url 


class DocumentReport(object):
    '''
    Класс для создания отчетов-текстовых документов.
    '''
    def __init__(self, template_name):
        if not template_name:
            raise ReportGeneratorException, "Не указан путь до шаблона"   
        self.desktop = OORunner.get_desktop()         
        template_path = os.path.join(DEFAULT_REPORT_TEMPLATE_PATH, template_name)
        self.document = create_document(self.desktop, template_path)
        
    def show(self, result_name, params, filter=None):    
        '''
        Подставляет в документе шаблона на место строк-ключей словаря params 
        значения, соответствующие ключам. 
        
        Допустимые популярные значения фильтра (по умолчанию используется .odt): 
        "writer_pdf_Export" - pdf
        "MS Word 97" - doc
        "Rich Text Format" - rtf
        "HTML" - html
        "Text" - txt
        "writer8" - odt
        '''
        assert isinstance(params, dict) 
        if not result_name:
            raise ReportGeneratorException, "Не указан путь до файла с отчетом"
        properties = []
        if filter:
            filter_property = PropertyValue()
            filter_property.Name = "FilterName"
            filter_property.Value = filter
            properties.append(filter_property)
        parser = OOParser()
        for key, value in params.items():
            if not isinstance(key, str):
                raise ReportGeneratorException, "Значение ключа для подстановки в шаблоне должно быть строковым"
            value = parser.convert_value(value)
            parser.find_and_replace(self.document, '#'+key+'#', value)    
        #Если не все переменные в шаблоне были заменены, стираем оставшиеся
        parser.find_and_replace(self.document, VARIABLE_REGEX, '')
        result_path = os.path.join(DEFAULT_REPORT_TEMPLATE_PATH, result_name)
        save_document_as(self.document, result_path, tuple(properties))
        
        
class SpreadsheetReport(object): 
    '''
    Класс для создания отчетов-электронных таблиц.
    '''       
    def __init__(self, template_name):
        
        #Задаем начальное состояние конечного автомата, описывающего порядок
        #размещения секций
        #Выводится ли секция вертикально (вниз)
        self.vertical = True
        
        #Ширина последней выведенной секции
        self.section_width = 0 
        
        #Длина последней выведенной секции
        self.section_height = 0
        
        #Координата по оси X ячейки, с которой выводилась последняя секция
        self.x = 0
        
        #Координата по оси Y ячейки, с которой выводилась последняя секция
        self.y = 0
        
        #Номера колонок, ширина которых уже была задана
        self.defined_width_columns = []
        
        #Номера рядов, высота которых уже была задана
        self.defined_height_rows = []
        
        self.desktop = OORunner.get_desktop()         
        template_path = os.path.join(DEFAULT_REPORT_TEMPLATE_PATH, template_name)
        self.document = create_document(self.desktop, template_path)
        self.context = OORunner.CONTEXT
        # Первый лист шаблона, в котором должны быть заданы секции
        template_sheet = self.document.getSheets().getByIndex(0)
        #Находим все секции в шаблоне
        parser = OOParser()
        self.sections = parser.create_sections(template_sheet, self)
        #Вставляем новый лист с таким же названием, как лист шаблона, на вторую
        # позицию
        template_sheet_name = template_sheet.getName()
        template_sheet.setName(TEMPORARY_SHEET_NAME)
        self.document.getSheets().insertNewByName(template_sheet_name, 1)

    def get_section(self, section_name):
        '''
        Возвращает объект класса Section по значению атрибута name
        '''  
        try:
            return self.sections[section_name]
        except KeyError:
            raise ReportGeneratorException, "Секция с именем %s не найдена. Список \
            доступных секций: %s" %(section_name, self.sections.keys())
            
    def show(self, result_name, filter=None):    
        '''        
        Допустимые популярные значения фильтра (по умолчанию используется .ods): 
        "writer_pdf_Export" - pdf
        "MS Excel 97" - xls
        "HTML (StarCalc)" - html
        "calc8" - ods
        '''
        if not result_name:
            raise ReportGeneratorException, "Не указан путь до файла с отчетом"
        properties = []
        if filter:
            filter_property = PropertyValue()
            filter_property.Name = "FilterName"
            filter_property.Value = filter
            properties.append(filter_property)
        result_path = os.path.join(DEFAULT_REPORT_TEMPLATE_PATH, result_name)
        if self.document.getSheets().hasByName(TEMPORARY_SHEET_NAME):
            self.document.getSheets().removeByName(TEMPORARY_SHEET_NAME)
        save_document_as(self.document, result_path, tuple(properties))
        
        
    def find_section_position(self, vertical, section_width, section_height):
        '''
        Возвращает координаты позиции в листе, с которой должна выводиться секция. 
        '''
        # Определяем новые координаты на основе текущего состояния автомата
        if self.vertical:
            if vertical:
                x = self.x
                y = self.y + self.section_height
            else:
                x = self.section_width 
                y = self.y
        else:
            if vertical:
                x = 0
                y = self.section_height
            else:
                x = self.x + self.section_width 
                y = self.y
              
        #Меняем состояние
        self.x = x
        self.y = y
        self.vertical = vertical
        self.section_width = section_width 
        self.section_height = section_height
        return (x,y)              
         