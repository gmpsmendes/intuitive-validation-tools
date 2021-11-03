import xml.etree.ElementTree as ET
from pyparsing import *
import ast

integer = pyparsing_common.signed_integer
varname = pyparsing_common.identifier
FILENAME = 'untitled.ows'

arith_expr = infixNotation(integer | varname,
    [
    ('-', 1, opAssoc.RIGHT),
    (oneOf('> < == <= >='), 2, opAssoc.LEFT),
    (oneOf('+ - * /'), 2, opAssoc.LEFT),
    ])

operatorTypes = ['DataWarehouse', 'DataMart', 'DataLake', 'DataSet', 'TempDataSet', 'FailDataSet', 'Filter', 'SumGroup']
operadores = []

class IntuitiveError():
    def __init__(self, id, errorType):
       self.id = id
       self.errorType = errorType

    def markXML(self):
        tree = ET.parse('modified.xml')
        root = tree.getroot()[0]
        for child in root:
            if child.attrib['id'] == self.id:
                if self.errorType in ('Operator', 'OperatorAttr', 'OperatorIO'):
                    for mxcell in child:
                        mxcell.set('style', f"{mxcell.get('style')};imageBorder=#FF0000;strokeWidth=4;")
                elif self.errorType == 'Condition':
                    child.set('style', f"{child.get('style')};strokeColor=#FF0000;strokeWidth=4;")
        tree.write('modified.xml')

class Relationship:
    def __init__(self, id, condicao):
        self.id = id
        self.condicao = condicao

    def substituiSimbolos(self):
        self.condicao = self.condicao.replace('&gt;', '>')
        self.condicao = self.condicao.replace('&gt;', '>')
        self.condicao = self.condicao.replace('&gt;', '>')
        self.condicao = self.condicao.replace('&gt;', '>')

    def validarCondicao(self):
        self.substituiSimbolos()
        return arith_expr.runTests(self.condicao, printResults = False)[0]

class Operator:
    def __init__(self, id, parametros, tipo, entradas, saidas):
        self.id = id
        self.parametros = parametros
        self.tipo = tipo
        self.entradas = entradas
        self.saidas = saidas
        self.errorList = []

    def validate(self):
        if self.tipo not in operatorTypes:
            self.errorList.append(IntuitiveError(self.id, 'Operator'))
            return False

class OperadorArmazenamento(Operator):
    def validate(self):
        if len(self.saidas) == 1 or len(self.entradas) == 1:
            return True
        else:
            self.errorList.append(IntuitiveError(self.id, 'OperatorIO'))
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

class Filter(Operator):
    def validate(self):
        if len(self.entradas) == 1 and len(self.saidas) >= 1:
            for saida in self.saidas:
                    if not saida.validarCondicao():
                        self.errorList.append(IntuitiveError(saida.id, 'Condition'))
                        return False
                    return True
        else:
            self.errorList.append(IntuitiveError(self.id, 'OperatorIO'))
            return False

class SumGroup(Operator):
    def validate(self):
        if len(self.entradas) == 1 and len(self.saidas) == 1 and 'AtributoAgrupamento' in self.parametros.keys() and 'CondicaoFiltro' in self.parametros.keys():
            return True
        else:
            self.errorList.append(IntuitiveError(self.id, 'OperatorAttr'))
            return False

def getIntTypeById(id):
    for operador in operadores:
        if operador.id == id:
            return operador.tipo

def readXML(filename):
    objects = []
    connections = []
    tree = ET.parse(filename)
    root = tree.getroot()[0]
    tree.write('modified.xml')

    for child in root:
        if child.tag in ('object'):
            parametros = {}
            for key in child.attrib.keys():
                if key not in ('label', 'placeholders', 'INTType', 'id'):
                    parametros[key] = child.attrib[key]
            child.attrib['saidas'] = []
            child.attrib['entradas'] = []
            child.attrib['parametros'] = parametros
            objects.append(child)
        if 'source' in child.attrib:
            connections.append(child)

    for object in objects:
        for connection in connections:
            if connection.attrib['source'] == object.attrib['id']:
                if 'value' in connection.attrib:
                    value = connection.attrib['value']
                else:
                    value = ''
                object.attrib['saidas'].append(Relationship(connection.attrib['id'], value))
            if connection.attrib.get('target', '') == object.attrib['id']:
                if 'value' in connection.attrib:
                    value = connection.attrib['value']
                else:
                    value = ''
                object.attrib['entradas'].append(Relationship(connection.attrib['id'], value))

    for object in objects:
        constructor = globals()[object.attrib['INTType']]
        instance = constructor(object.attrib['id'], object.attrib['parametros'], object.attrib['INTType'], object.attrib['entradas'], object.attrib['saidas'])
        operadores.append(instance)

def readXML_orange3(filename):
    objects = []
    connections = []
    connections_ids = {'id':[], 'source':[], 'target':[]}
    values_ids = {'id':[],'value':[]}
    tree = ET.parse(filename)
    nodes = tree.getroot()[0]
    links = tree.getroot()[1]
    node_properties = tree.getroot()[4]

    tree.write('modified.xml')

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

    for node in nodes:
        if node.tag in ('node'):
            parametros_node = {}
            for key in node.attrib.keys():
                if key not in ('name', 'id','qualified_name','project_name','version','title','position'):
                    parametros_node[key] = node.attrib[key]
            node.attrib['saidas'] = []
            node.attrib['entradas'] = []
            node.attrib['parametros'] = parametros_node
            objects.append(node)
        if node.attrib['id'] in values_ids['id']:
            index = (list(values_ids['id']).index(node.attrib['id']))
            value = values_ids['value'][index]
            node.attrib['value'] = value
        if node.attrib['id'] in connections_ids['id']:
            index = (list(connections_ids['id']).index(node.attrib['id']))
            source = connections_ids['source'][index]
            target = connections_ids['target'][index]
            node.attrib['source'] = source
            node.attrib['target'] = target
            connections.append(node)

    for object in objects:
        for connection in connections:
            if connection.attrib['source'] == object.attrib['id']:
                if 'value' in connection.attrib:
                    value = connection.attrib['value']
                else:
                    value = ''
                object.attrib['saidas'].append(Relationship(connection.attrib['id'], value))
            if connection.attrib.get('target', '') == object.attrib['id']:
                if 'value' in connection.attrib:
                    value = connection.attrib['value']
                else:
                    value = ''
                object.attrib['entradas'].append(Relationship(connection.attrib['id'], value))

    for object in objects:
        constructor = globals()[object.attrib['name']]
        instance = constructor(object.attrib['id'], object.attrib['parametros'], object.attrib['name'], object.attrib['entradas'], object.attrib['saidas'])
        operadores.append(instance)

if __name__ == "__main__":
    file_type = input("Enter the file origin (orange3 or drawio: )")
    if file_type == 'drawio':
        readXML(FILENAME)
        for operador in operadores:
            operador.validate()
        for operador in operadores:
            for error in operador.errorList:
                error.markXML()
    else:
        readXML_orange3(FILENAME)
        for operador in operadores:
            operador.validate()
        for operador in operadores:
            for error in operador.errorList:
                error.markXML()
