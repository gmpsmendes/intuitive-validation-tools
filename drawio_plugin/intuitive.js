Draw.loadPlugin(function (ui) {
    var sidebar_id = 'Intuitive';
    var sidebar_title = 'Intuitive Operators';
    var verticies = [];
    IntDW = function () {
    };
    IntDW.prototype.create = function () {
        var IntDW = new mxCell('', new mxGeometry(0, 70, 160, 140), 'shape=image;image=https://github.com/obarafernando/intuitive_local_tool/blob/main/operators_images/DW.png?raw=true;resizable=0;movable=1;rotatable=1');
        IntDW.geometry.width = 100;
        IntDW.geometry.height= 100;
        IntDW.setVertex(true);
        IntDW.setValue(mxUtils.createXmlDocument().createElement('object'));
        IntDW.setAttribute('label', '');
        IntDW.setAttribute('placeholders', '1');
        IntDW.setAttribute('INTType', 'DataWarehouse');
        return IntDW;
    };
    verticies.push(IntDW);
    IntDataMart = function () {
    };
    IntDataMart.prototype.create = function () {
        var IntDataMart = new mxCell('', new mxGeometry(0, 70, 160, 140), 'shape=image;image=https://github.com/obarafernando/intuitive_local_tool/blob/main/operators_images/DataMart.png?raw=true;resizable=0;movable=1;rotatable=1');
        IntDataMart.geometry.width = 100;
        IntDataMart.geometry.height= 100;
        IntDataMart.setVertex(true);
        IntDataMart.setValue(mxUtils.createXmlDocument().createElement('object'));
        IntDataMart.setAttribute('label', '');
        IntDataMart.setAttribute('placeholders', '1');
        IntDataMart.setAttribute('INTType', 'DataMart');
        return IntDataMart;
    };
    verticies.push(IntDataMart);
    IntDataLake = function () {
    };
    IntDataLake.prototype.create = function () {
        var IntDataLake = new mxCell('', new mxGeometry(0, 70, 160, 140), 'shape=image;image=https://github.com/obarafernando/intuitive_local_tool/blob/main/operators_images/DataLake.png?raw=true;resizable=0;movable=1;rotatable=1');
        IntDataLake.geometry.width = 100;
        IntDataLake.geometry.height= 100;
        IntDataLake.setVertex(true);
        IntDataLake.setValue(mxUtils.createXmlDocument().createElement('object'));
        IntDataLake.setAttribute('label', '');
        IntDataLake.setAttribute('placeholders', '1');
        IntDataLake.setAttribute('INTType', 'DataLake');
        return IntDataLake;
    };
    verticies.push(IntDataLake);
    IntDataSet = function () {
    };
    IntDataSet.prototype.create = function () {
        var IntDataSet = new mxCell('', new mxGeometry(0, 70, 160, 140), 'shape=image;image=https://github.com/obarafernando/intuitive_local_tool/blob/main/operators_images/DataSet.png?raw=true;resizable=0;movable=1;rotatable=1');
        IntDataSet.geometry.width = 100;
        IntDataSet.geometry.height= 100;
        IntDataSet.setVertex(true);
        IntDataSet.setValue(mxUtils.createXmlDocument().createElement('object'));
        IntDataSet.setAttribute('label', '');
        IntDataSet.setAttribute('placeholders', '1');
        IntDataSet.setAttribute('INTType', 'DataSet');
        return IntDataSet;
    };
    verticies.push(IntDataSet);
    IntTempDataSet = function () {
    };
    IntTempDataSet.prototype.create = function () {
        var IntTempDataSet = new mxCell('', new mxGeometry(0, 70, 160, 140), 'shape=image;image=https://github.com/obarafernando/intuitive_local_tool/blob/main/operators_images/TempDataSet.png?raw=true;resizable=0;movable=1;rotatable=1');
        IntTempDataSet.geometry.width = 100;
        IntTempDataSet.geometry.height= 100;
        IntTempDataSet.setVertex(true);
        IntTempDataSet.setValue(mxUtils.createXmlDocument().createElement('object'));
        IntTempDataSet.setAttribute('label', '');
        IntTempDataSet.setAttribute('placeholders', '1');
        IntTempDataSet.setAttribute('INTType', 'TempDataSet');
        return IntTempDataSet;
    };
    verticies.push(IntTempDataSet);
    IntFailDataSet = function () {
    };
    IntFailDataSet.prototype.create = function () {
        var IntFailDataSet = new mxCell('', new mxGeometry(0, 70, 160, 140), 'shape=image;image=https://github.com/obarafernando/intuitive_local_tool/blob/main/operators_images/FailDataSet.png?raw=true;resizable=0;movable=1;rotatable=1');
        IntFailDataSet.geometry.width = 100;
        IntFailDataSet.geometry.height= 100;
        IntFailDataSet.setVertex(true);
        IntFailDataSet.setValue(mxUtils.createXmlDocument().createElement('object'));
        IntFailDataSet.setAttribute('label', '');
        IntFailDataSet.setAttribute('placeholders', '1');
        IntFailDataSet.setAttribute('INTType', 'FailDataSet');
        return IntFailDataSet;
    };
    verticies.push(IntFailDataSet);
    IntFilter = function () {
    };
    IntFilter.prototype.create = function () {
        var IntFilter = new mxCell('', new mxGeometry(0, 70, 160, 140), 'shape=image;image=https://github.com/obarafernando/intuitive_local_tool/blob/main/operators_images/Filter.png?raw=true;resizable=0;movable=1;rotatable=1');
        IntFilter.geometry.width = 100;
        IntFilter.geometry.height= 100;
        IntFilter.setVertex(true);
        IntFilter.setValue(mxUtils.createXmlDocument().createElement('object'));
        IntFilter.setAttribute('label', '');
        IntFilter.setAttribute('placeholders', '1');
        IntFilter.setAttribute('INTType', 'Filter');
        return IntFilter;
    };
    verticies.push(IntFilter);
    IntSumGroup = function () {
    };
    IntSumGroup.prototype.create = function () {
        var IntSumGroup = new mxCell('', new mxGeometry(0, 70, 160, 140), 'shape=image;image=https://github.com/obarafernando/intuitive_local_tool/blob/main/operators_images/SumGroup.png?raw=true;resizable=0;movable=1;rotatable=1');
        IntSumGroup.geometry.width = 100;
        IntSumGroup.geometry.height= 100;
        IntSumGroup.setVertex(true);
        IntSumGroup.setValue(mxUtils.createXmlDocument().createElement('object'));
        IntSumGroup.setAttribute('label', '%AtributoAgrupamento%\n%AtributoSoma%\n%CondicaoFiltro%');
        IntSumGroup.setAttribute('AtributoAgrupamento', '');
        IntSumGroup.setAttribute('AtributoSoma', '');
        IntSumGroup.setAttribute('CondicaoFiltro', '');
        IntSumGroup.setAttribute('placeholders', '1');
        IntSumGroup.setAttribute('INTType', 'SumGroup');
        return IntSumGroup;
    };
    verticies.push(IntSumGroup);
    ui.sidebar.addPalette(sidebar_id, sidebar_title, true, function (content) {
        for (var i in verticies) {
            var cell = verticies[i].prototype.create();
            content.appendChild(ui.sidebar.createVertexTemplateFromCells([cell], cell.geometry.width, cell.geometry.height, cell.label));
        }
    });
});