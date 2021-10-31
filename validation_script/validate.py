import xml.etree.ElementTree as ET
from pyparsing import *

integer = pyparsing_common.signed_integer
varname = pyparsing_common.identifier
FILENAME = 'sample_diagram_error.xml'

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
        if child.tag == 'object':
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

if __name__ == "__main__":
    readXML(FILENAME)
    for operador in operadores:
        operador.validate()
    for operador in operadores:
        for error in operador.errorList:
           error.markXML()

