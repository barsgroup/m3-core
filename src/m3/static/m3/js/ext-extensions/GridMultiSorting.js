Ext3.ns('Ext3.ux.grid');

Ext3.ux.grid.MultiSorting = Ext3.extend(Ext3.util.Observable,{
    constructor: function(config){
        if (config) Ext3.apply(this, config);
        Ext3.ux.grid.MultiSorting.superclass.constructor.call(this);
    }
    ,init: function(grid){
        if (grid instanceof Ext3.grid.GridPanel){
            this.grid = grid;
            this.grid.on('headerclick', this.onHeaderClick, this);
            this.grid.on('afterrender', this.onAfterRender, this);
            this.grid.getStore().multiSort = Ext3.createDelegate(this.realMultiSort, this.grid.getStore(), this, true);
        }
    }
    ,onAfterRender: function(grid){
        // отключим старый обработчик
        this.grid.un('headerclick', this.grid.getView().onHeaderClick, this.grid.getView());
        this.grid.getView().updateHeaderSortState = Ext3.createDelegate(this.realUpdateHeaderSortState, this.grid.getView());
        this.grid.getView().updateSortIcon = Ext3.createDelegate(this.realUpdateSortIcon, this.grid.getView());
    }
    ,onHeaderClick: function(grid, index, event){
        var cm = grid.getColumnModel();
        if (grid.getView().headersDisabled || !cm.isSortable(index)) {
            return;
        }
        grid.stopEditing(true);
        var store = grid.getStore();
        if (event.ctrlKey) {
            // множественная сортировка
            // получим текущую сортировку
            var field = cm.getDataIndex(index);
            if (store.hasMultiSort) {
                // если уже мульти
                var sortInfo = store.multiSortInfo;
                var found = false;
                for (var i=0, j = sortInfo.sorters.length; i < j; i++) {
                    // если текущее поле уже есть в сортировке
                    if (sortInfo.sorters[i].field == field) {
                        // меняем направление
                        sortInfo.sorters[i].direction = sortInfo.sorters[i].direction.toggle("ASC", "DESC");
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    sortInfo.sorters.push({direction: "ASC", field: field});
                }
                store.multiSort(sortInfo.sorters);
            } else {
                // если еще не мульти
                // если текущее поле уже есть в сортировке
                if (!store.sortInfo || store.sortInfo.field == field) {
                    store.sort(cm.getDataIndex(index));
                } else {
                    var sorters = [{direction: store.sortInfo.direction, field: store.sortInfo.field}, {direction: "ASC", field: field}];
                    store.multiSort(sorters);
                }
            }
        } else {
            // обычная сортировка
            store.sort(cm.getDataIndex(index));
        }
    }
    ,beforeLoad: function(store, options){
        // отправка параметров множественной сортировки
        if (store.hasMultiSort) {
            options.params['multisort'] = Ext3.util.JSON.encode(store.multiSortInfo.sorters);
        }
    }
    ,realMultiSort: function(sorters, multisortplugin) {
        this.hasMultiSort = true;
        var direction = "ASC";

        /**
         * Object containing overall sort direction and an ordered array of sorter configs used when sorting on multiple fields
         * @property multiSortInfo
         * @type Object
         */
        this.multiSortInfo = {
            sorters  : sorters,
            direction: direction
        };

        if (this.remoteSort) {
            //this.singleSort(sorters[0].field, sorters[0].direction);
            // подготовить параметры для отправки на сервер
            this.on('beforeload', multisortplugin.beforeLoad, this, {'single': true});
            if (!this.load(this.lastOptions)) {

            }
        } else {
            this.applySort();
            this.fireEvent('datachanged', this);
        }
    }
    ,realUpdateHeaderSortState : function() {
        var state = this.ds.hasMultiSort ? this.ds.multiSortInfo : this.ds.sortInfo;
        if (!state) {
            return;
        }

        // если обновилась сортировка
        if ((!this.hasMultiSort && this.ds.hasMultiSort)||(this.hasMultiSort && !this.ds.hasMultiSort)) {
            this.grid.fireEvent('sortchange', this.grid, state);
        } else if (this.ds.hasMultiSort ) {
            var changed = false, founded = 0;
            for (var i=0, j = state.sorters.length; i < j; i++) {
                for (var k=0, l = this.sortState.sorters.length; k < l; k++) {
                    if (this.sortState.sorters[k].field == state.sorters[i].field) {
                        founded = founded+1;
                        if (this.sortState.sorters[k].direction != state.sorters[i].direction) {
                            changed = true;
                        }
                        break;
                    }
                }
                if (changed) {
                    break;
                }
            }
            // если нашли изменения, или не совпало количество
            if (changed || this.sortState.length != founded) {
                this.grid.fireEvent('sortchange', this.grid, state);
            }
        } else if (!this.sortState || (this.sortState.field != state.field || this.sortState.direction != state.direction)) {
            this.grid.fireEvent('sortchange', this.grid, state);
        }

        this.sortState = state;
        this.hasMultiSort = this.ds.hasMultiSort;


        if (this.hasMultiSort) {
            this.mainHd.select(this.cellSelector || 'td').removeClass(this.sortClasses);
            for (var i=0, j = this.sortState.sorters.length; i < j; i++) {
                var sortColumn = this.cm.findColumnIndex(this.sortState.sorters[i].field);
                if (sortColumn != -1) {
                    var sortDir = this.sortState.sorters[i].direction;
                    this.updateSortIcon(sortColumn, sortDir);
                }
            }
        } else {
            var sortColumn = this.cm.findColumnIndex(state.field);
            if (sortColumn != -1) {
                var sortDir = state.direction;
                this.mainHd.select(this.cellSelector || 'td').removeClass(this.sortClasses);
                this.updateSortIcon(sortColumn, sortDir);
            }
        }
    }
    ,realUpdateSortIcon: function(col, dir) {
        var sortClasses = this.sortClasses,
            sortClass   = sortClasses[dir == "DESC" ? 1 : 0],
            //headers     = this.mainHd.select('td').removeClass(sortClasses);
            headers     = this.mainHd.select(this.cellSelector || 'td');

        headers.item(col).addClass(sortClass);
    }
});