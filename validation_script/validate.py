import xml.etree.ElementTree as ET
from pyparsing import *
import argh
import os
import ast

integer = pyparsing_common.signed_integer
varname = pyparsing_common.identifier
MODIFIED_FILENAME = 'modified.xml'
globalErrorList = []

arith_expr = infixNotation(integer | varname,
    [
    ('-', 1, opAssoc.RIGHT),
    (oneOf('> < == <= >='), 2, opAssoc.LEFT),
    (oneOf('+ - * /'), 2, opAssoc.LEFT),
    ])

operatorTypes_drawio = ['DataWarehouse', 'DataMart', 'DataLake', 'DataSet', 'TempDataSet', 'FailDataSet', 'Filter', 'SumGroup']
operatorTypes_orange3 = operatorTypes_drawio + ['FilterOrange3','FilterConditionOrange3']
operadores = []


class IntuitiveError():
    def __init__(self, id, errorType, idOpSource = None, idOpTarget = None):
        self.id = id
        self.errorType = errorType
        self.idOpSource = idOpSource
        self.idOpTarget = idOpTarget

    def markXML(self, tool):
        tree = ET.parse(MODIFIED_FILENAME)
        if tool == 'drawio':
            root = tree.getroot()[0]
            for child in root:
                if child.attrib['id'] == self.id:
                    if self.errorType in ('Operador Desconhecido', 'Atributo do Operador', 'Entrada e Saída do Operador'):
                        for mxcell in child:
                            mxcell.set('style', f"{mxcell.get('style')};imageBorder=#FF0000;strokeWidth=4;")
                    elif self.errorType == 'Condição Relacionamento':
                        child.set('style', f"{child.get('style')};strokeColor=#FF0000;strokeWidth=4;")
            globalErrorList.append(self)
            tree.write(MODIFIED_FILENAME)
        elif tool == 'orange3':
            globalErrorList.append(self)
            tree.write(MODIFIED_FILENAME)


class Relationship:
    def __init__(self, id, condicao, source, target = None):
        self.id = id
        self.condicao = condicao
        self.source = source
        self.target = target

    def substituiSimbolos(self):
        self.condicao = self.condicao.replace('&gt;', '>')
        self.condicao = self.condicao.replace('&lt;', '<')

    def validarCondicao(self):
        self.substituiSimbolos()
        return arith_expr.runTests(self.condicao, printResults = False)[0] and self.target is not None and (self.condicao == '' or len(self.condicao.split(' '))>1)

class Operator:
    def __init__(self, id, parametros, tipo, entradas, saidas, tool, title = None):
        self.id = id
        self.parametros = parametros
        self.tipo = tipo
        self.entradas = entradas
        self.saidas = saidas
        self.errorList = []
        self.tool = tool
        self.title = title

    def validate(self):
        if self.tool == 'orange3' and self.tipo in operatorTypes_orange3 or self.tool == 'drawio' and self.tipo in operatorTypes_drawio:
            return True
        self.errorList.append(IntuitiveError(self.id, 'Operador Desconhecido'))
        return False


class OperadorArmazenamento(Operator):
    def validate(self):
        if len(self.saidas) == 1 or len(self.entradas) == 1:
            return True
        else:
            self.errorList.append(IntuitiveError(self.id, 'Entrada e Saída do Operador'))
            return False

class DataWarehouse(OperadorArmazenamento):
    pass

class DataMart(OperadorArmazenamento):
    pass

class DataLake(OperadorArmazenamento):
    pass

class DataSet(OperadorArmazenamento):
    pass

class TempDataSet(OperadorArmazenamento):
    pass

class FailDataSet(OperadorArmazenamento):
    pass

class FilterOrange3(Operator):
    def validate(self):
        if len(self.entradas) == 1 and len (self.saidas) >=1:
            return True
        else:
            self.errorList.append(IntuitiveError(self.id, 'Entrada do Operador e Saída do Operador'))
            return False

class FilterConditionOrange3(Operator):
    def validate(self):
        if len(self.entradas) == 1 and len(self.saidas) == 1:
            for saida in self.saidas:
                if not saida.validarCondicao():
                    self.errorList.append(IntuitiveError(saida.id, 'Condição Relacionamento', saida.source, saida.target))
            for entrada in self.entradas:
                if not entrada.validarCondicao():
                    self.errorList.append(IntuitiveError(entrada.id, 'Condição Relacionamento', entrada.source, entrada.target))
        else:
            self.errorList.append(IntuitiveError(self.id, 'Entrada e Saída do Operador'))
        return not len(self.errorList) > 0

class Filter(Operator):
    def validate(self):
        if len(self.entradas) == 1 and len(self.saidas) >= 1:
            for saida in self.saidas:
                if not saida.validarCondicao():
                    self.errorList.append(IntuitiveError(saida.id, 'Condição Relacionamento', saida.source, saida.target))
            for entrada in self.entradas:
                if not entrada.validarCondicao():
                    self.errorList.append(IntuitiveError(entrada.id, 'Condição Relacionamento', entrada.source, entrada.target))
        else:
            self.errorList.append(IntuitiveError(self.id, 'Entrada e Saída do Operador'))
        return not len(self.errorList) > 0

class SumGroup(Operator):
    def validate(self):
        if len(self.entradas) == 1 and len(self.saidas) == 1 and 'AtributoAgrupamento' in self.parametros.keys() and 'AtributoSoma' in self.parametros.keys():
            return True
        else:
            self.errorList.append(IntuitiveError(self.id, 'Atributo do Operador'))
            return False

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def getIntTypeById(id):
    for operador in operadores:
        if operador.id == id:
            return operador.tipo

def getTitleById(id):
    for operador in operadores:
        if operador.id == id:
            return operador.title

def addErrorList(tool):
    uniqueErrorList = []
    for i in globalErrorList:
        skip = False
        for j in uniqueErrorList:
            if i.id == j.id and i.errorType == j.errorType and i.idOpTarget == j.idOpTarget and i.idOpSource == j.idOpSource:
                skip = True
        if skip:
            continue
        else:
            uniqueErrorList.append(i)

    tree = ET.parse(MODIFIED_FILENAME)
    if tool == 'drawio':
        treeRoot = tree.getroot()[0]
        errorList = ET.Element('mxCell')
        errorList.set('id', 'x')
        errorList.set('style', 'rounded=0;whiteSpace=wrap;html=1;align=left;')
        errorList.set('parent', '1')
        errorList.set('vertex', '1')

        geometry = ET.SubElement(errorList, 'mxGeometry')
        geometry.set('x', '10')
        geometry.set('y', '20')
        geometry.set('width', '300')
        geometry.set('height', f'{50+50*len(uniqueErrorList)}')
        geometry.set('as', 'geometry')
        message = '<b><font style="font-size: 15px">Erros:</font></b><br><br>'
        for error in uniqueErrorList:
            if error.errorType == 'Condição Relacionamento':
                message += f'Erro na condição do relacionamento entre os operadores {getIntTypeById(error.idOpSource)} (id: {error.idOpSource}) e {getIntTypeById(error.idOpTarget)} (id: {error.idOpTarget})<br><br>'
            else:
                message += f'Erro {error.errorType} no operador {getIntTypeById(error.id)} (id:{error.id})<br><br>'
        errorList.set('value', message)
        treeRoot.append(errorList)
        tree.write(MODIFIED_FILENAME)
    elif tool == 'orange3':

        treeRoot = tree.getroot()[2] #Annotations
        #<text font-family="Ubuntu" font-size="16" id="0" rect="(102.0, 514.0, 150.0, 26.0)" type="text/plain" />
        errorList = ET.Element('text')
        errorList.set('font-family','Ubuntu')
        errorList.set('font-size','16')
        errorList.set('id','0')
        errorList.set('rect','(102.0, 514.0, 150.0, 26.0)')
        errorList.set('type', 'text/html')
        message = '<b><font style="font-size: 15px">Erros:</font></b><br><br>'
        for error in uniqueErrorList:
            if error.errorType == 'Condição Relacionamento':
                message += f'Erro na condição do relacionamento entre os operadores {getIntTypeById(error.idOpSource)} (id: {error.idOpSource} ({getTitleById(error.idOpSource)}))  e {getIntTypeById(error.idOpTarget)} (id: {error.idOpTarget} ({getTitleById(error.idOpTarget)}))<br><br>'
            else:
                message += f'Erro {error.errorType} no operador {getIntTypeById(error.id)} (id:{error.id} ({getTitleById(error.id)}))<br><br>'
        errorList.text = message
        indent(treeRoot)
        treeRoot.append(errorList)
        tree.write(MODIFIED_FILENAME, xml_declaration=True, encoding='utf-8')


def create_objects(objects,connections,tool):
    if tool == 'orange3':
        op_field = 'name'
    elif tool == 'drawio':
        op_field = 'INTType'
    for object in objects:
        for connection in connections:
            if connection.attrib['source'] == object.attrib['id']:
                value = connection.attrib.get('value', '')
                object.attrib['saidas'].append(Relationship(connection.attrib['id'], value, object.attrib['id'], connection.attrib.get('target')))
            if connection.attrib.get('target', '') == object.attrib['id']:
                value = connection.attrib.get('value', '')
                object.attrib['entradas'].append(Relationship(connection.attrib['id'], value, connection.attrib.get('source'), object.attrib['id']))
        constructor = globals()[object.attrib[op_field]]
        instance = constructor(object.attrib['id'], object.attrib['parametros'], object.attrib[op_field], object.attrib['entradas'], object.attrib['saidas'],tool, object.attrib.get('title'))
        operadores.append(instance)

def readXML_drawio(filename):
    objects = []
    connections = []
    tree = ET.parse(filename)
    root = tree.getroot()[0]
    tree.write(MODIFIED_FILENAME)

    for child in root:
        if child.tag in ('object'):
            parametros = {}
            for key in child.attrib.keys():
                if key not in ('label', 'placeholders', 'INTType', 'id') and child.attrib[key] != '':
                    parametros[key] = child.attrib[key]
            child.attrib['saidas'] = []
            child.attrib['entradas'] = []
            child.attrib['parametros'] = parametros
            objects.append(child)
        if 'source' in child.attrib:
            connections.append(child)
    create_objects(objects,connections,'drawio')

def readXML_orange3(filename):
    objects = []
    connections = []
    connections_ids = {'id':[], 'source':[], 'target':[]}
    values_ids = {'id':[],'value':[]}
    values_ids_att_group = {'id':[],'value':[]}
    values_ids_att_soma = {'id':[],'value':[]}
    values_ids = {'id':[],'value':[]}
    tree = ET.parse(filename)
    nodes = tree.getroot()[0]
    links = tree.getroot()[1]
    node_properties = tree.getroot()[4]

    tree.write(MODIFIED_FILENAME)

    for link in links:
        if 'source_node_id' in link.attrib:
            connections_ids['id'].append(link.attrib['id'])
            connections_ids['source'].append(link.attrib['source_node_id'])
            connections_ids['target'].append(link.attrib['sink_node_id'])

    properties_text = {}
    for properties in node_properties:
        if properties.text[0] == '{':
            properties_text = ast.literal_eval(properties.text)
            if 'filter' in properties_text:
                values_ids['id'].append(properties.attrib['node_id'])
                values_ids['value'].append(properties_text['filter'])
            if 'AtributoAgrupamento' in properties_text and properties_text['AtributoAgrupamento'] != '':
                values_ids_att_group['id'].append(properties.attrib['node_id'])
                values_ids_att_group['value'].append(properties_text['AtributoAgrupamento'])
            if 'AtributoSoma' in properties_text and properties_text['AtributoSoma'] != '':
                values_ids_att_soma['id'].append(properties.attrib['node_id'])
                values_ids_att_soma['value'].append(properties_text['AtributoSoma'])

    for node in nodes:
        if node.tag in ('node'):
            parametros_node = {}
            for key in node.attrib.keys():
                if key not in ('name', 'id','qualified_name','project_name','version','title','position'):
                    parametros_node[key] = node.attrib[key]
            node.attrib['saidas'] = []
            node.attrib['entradas'] = []
            #objects.append(node)
        if node.attrib['id'] in values_ids['id']:
            index = (list(values_ids['id']).index(node.attrib['id']))
            value = values_ids['value'][index]
            parametros_node['value'] = value
        if node.attrib['id'] in values_ids_att_group['id']:
            index = (list(values_ids_att_group['id']).index(node.attrib['id']))
            value = values_ids_att_group['value'][index]
            parametros_node['AtributoAgrupamento'] = value
        if node.attrib['id'] in values_ids_att_soma['id']:
            index = (list(values_ids_att_soma['id']).index(node.attrib['id']))
            value = values_ids_att_soma['value'][index]
            parametros_node['AtributoSoma'] = value
        node.attrib['parametros'] = parametros_node
        objects.append(node)
        if node.attrib['id'] in connections_ids['id']:
            index = (list(connections_ids['id']).index(node.attrib['id']))
            source = connections_ids['source'][index]
            target = connections_ids['target'][index]
            node.attrib['source'] = source
            node.attrib['target'] = target
            connections.append(node)

    create_objects(objects,connections,'orange3')



@argh.arg('-f', '--file', type=str )
def drawio (file = ''):
    global MODIFIED_FILENAME
    MODIFIED_FILENAME = f'{os.path.splitext(file)[0]}_modified.xml'
    readXML_drawio(file)
    for operador in operadores:
        operador.validate()
        for error in operador.errorList:
            error.markXML('drawio')
    addErrorList('drawio')

@argh.arg('-f', '--file', type=str)
def orange3(file = ''):
    global MODIFIED_FILENAME
    MODIFIED_FILENAME = f'{os.path.splitext(file)[0]}_modified.ows'
    readXML_orange3(file)
    for operador in operadores:
        operador.validate()
        for error in operador.errorList:
            error.markXML('orange3')
    addErrorList('orange3')

parser = argh.ArghParser()
parser.add_commands([drawio, orange3])


if __name__ == '__main__':
    parser.dispatch()
