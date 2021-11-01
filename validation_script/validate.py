import xml.etree.ElementTree as ET
from pyparsing import *

integer = pyparsing_common.signed_integer
varname = pyparsing_common.identifier
FILENAME = 'validation_script/diagram_samples_drawio/sample_diagram.xml'
MODIFIED_FILENAME = 'validation_script/modified.xml'
globalErrorList = []

arith_expr = infixNotation(integer | varname,
    [
    ('-', 1, opAssoc.RIGHT),
    (oneOf('> < == <= >='), 2, opAssoc.LEFT),
    (oneOf('+ - * /'), 2, opAssoc.LEFT),
    ])

operatorTypes = ['DataWarehouse', 'DataMart', 'DataLake', 'DataSet', 'TempDataSet', 'FailDataSet', 'Filter', 'SumGroup']
operadores = []

class IntuitiveError():
    def __init__(self, id, errorType, idOpSource = None, idOpTarget = None):
       self.id = id
       self.errorType = errorType
       if errorType == 'Condição Relacionamento':
           self.idOpSource = idOpSource
           self.idOpTarget = idOpTarget

    def markXML(self):
        tree = ET.parse(MODIFIED_FILENAME)
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
        return arith_expr.runTests(self.condicao, printResults = False)[0] and self.target is not None

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

def getIntTypeById(id):
    for operador in operadores:
        if operador.id == id:
            return operador.tipo

def addErrorList():
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


def readXML(filename):
    objects = []
    connections = []
    tree = ET.parse(filename)
    root = tree.getroot()[0]
    tree.write(MODIFIED_FILENAME)

    for child in root:
        if child.tag == 'object':
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
    for object in objects:
        for connection in connections:
            if connection.attrib['source'] == object.attrib['id']:
                if 'value' in connection.attrib:
                    value = connection.attrib['value']
                else:
                    value = ''
                object.attrib['saidas'].append(Relationship(connection.attrib['id'], value, object.attrib['id'], connection.attrib.get('target')))
            if connection.attrib.get('target', '') == object.attrib['id']:
                if 'value' in connection.attrib:
                    value = connection.attrib['value']
                else:
                    value = ''
                object.attrib['entradas'].append(Relationship(connection.attrib['id'], value, connection.attrib['source'], object.attrib['id']))

    for object in objects:
        constructor = globals()[object.attrib['INTType']]
        print(object.attrib['parametros'])
        instance = constructor(object.attrib['id'], object.attrib['parametros'], object.attrib['INTType'], object.attrib['entradas'], object.attrib['saidas'])
        operadores.append(instance)

if __name__ == "__main__":
    readXML(FILENAME)
    for operador in operadores:
        operador.validate()
    for operador in operadores:
        for error in operador.errorList:
           error.markXML()
    addErrorList()

