/**
 * Crafted by ZIgi
 */

Ext.apply(ModelTypeLibrary,{
    typesConfig:{
        component:{
            properties:{
                style:{
                    defaultValue:'undefined',
                    propertyType:'object'
                },
                hidden:{
                    defaultValue:false
                },
                disabled:{
                    defaultValue:false
                },
                height:{
                    defaultValue:0
                },
                width:{
                    defaultValue:0
                },
                x:{
                    defaultValue:0
                },
                y:{
                    defaultValue:0
                },
                html:{
                    defaultValue:''
                },
                region:{
                    defaultValue:''
                },
                flex:{
                    defaultValue:''
                },
                maxHeight:{
                    defaultValue:0
                },
                minHeight:{
                    defaultValue:0
                },
                maxWidth:{
                    defaultValue:0
                },
                minWidth:{
                    defaultValue:0
                },
                name:{
                    defaultValue:''
                },
                anchor:{
                    defaultValue:''
                },
                cls:{
                    defaultValue:''
                },
                labelWidth:{
                    defaultValue:0
                },
                labelAlign:{
                    defaultValue:'left',
                    propertyType:'enum'
                },
                labelPad:{
                    defaultValue:''
                },
                autoScroll:{
                    defaultValue:false
                }
            }
        },
        panel:{
            isContainer:true,
            properties:{
                autoScroll:{
                    defaultValue:false
                },
                layout:{
                    defaultValue:'auto',
                    isInitProperty:true,
                    propertyType:'enum'
                },
                layoutConfig :{
                    defaultValue:'undefined',
                    propertyType:'object'
                },
                title:{
                    defaultValue:'New panel',
                    isInitProperty:true
                },
                id:{
                    defaultValue:'New panel',
                    isInitProperty:true
                },
                // ATTENTION:EXT не понимает строки в качестве высоты и ширины панели, поэтому тут число
                height:{
                    defaultValue:0
                },
                width:{
                    defaultValue:0
                },
                flex:{
                    defaultValue:'undefined'
                },
                labelWidth:{
                    defaultValue:100
                },
                labelAlign:{
                    defaultValue:'left',
                    propertyType:'enum'
                },
                padding:{
                    defaultValue:'undefined'
                }
            },
            childTypesRestrictions:{
                disallowed:['arrayStore','gridColumn']
            },
            toolboxData:{
                text:'Panel',
                category:'Containers'
            },
            treeIconCls:'designer-panel'
        },
        fieldSet:{
            isContainer:true,
            properties:{
                layout:{
                    defaultValue:'form',
                    isInitProperty:true,
                    propertyType:'enum'
                },
                title:{
                    defaultValue:'New fieldset',
                    isInitProperty:true
                },
                id:{
                    defaultValue:'New fieldset',
                    isInitProperty:true
                },
                // ATTENTION:EXT не понимает строки в качестве высоты и ширины панели, поэтому тут число
                height:{
                    defaultValue:0
                },
                width:{
                    defaultValue:0
                },
                flex:{
                    defaultValue:'undefined'
                },
                labelWidth:{
                    defaultValue:100
                },
                labelAlign:{
                    defaultValue:'left',
                    propertyType:'enum'
                },
                padding:{
                    defaultValue:'undefined'
                }
            },
            childTypesRestrictions:{
                disallowed:['arrayStore','gridColumn']
            },
            toolboxData:{
                text:'Field set',
                category:'Containers'
            },
            treeIconCls:'designer-icon-fieldset'
        },
        tabPanel:{
            isContainer:true,
            properties:{
                title:{
                    defaultValue:'New tab panel',
                    isInitProperty:true
                },
                id:{
                    defaultValue:'New tab panel',
                    isInitProperty:true
                },
                activeTab:{
                    defaultValue:0,
                    isInitProperty:true
                }
            },
            childTypesRestrictions:{
                allowed:['panel', 'gridPanel']
            },
            toolboxData:{
                text:'Tab panel',
                category:'Containers'
            },
            treeIconCls:'designer-tab-panel'
        },
        /*
        * Поля для ввода
        */
        baseField : {
            parent:'component',
            properties:{
                fieldLabel:{
                    defaultValue:''
                },
                value: {
                    defaultValue:''
                },
                labelStyle:{
                    defaultValue:''
                },
                readOnly:{
                    defaultValue:false
                },
                allowBlank :{
                    defaultValue:true
                },
                hideLabel :{
                    defaultValue:false
                },
                vtype: {
                    defaultValue:''
                },
                emptyText: {
                    defaultValue:''
                },
                minLength:{
                    defaultValue:0
                },
                minLengthText:{
                    defaultValue:''
                },
                maxLength:{
                    defaultValue:0
                },
                maxLengthText:{
                    defaultValue:''
                },
                regex:{
                    defaultValue:''
                },
                regexText:{
                    defaultValue:''
                },
                tabIndex:{
                    defaultValue:0
                },
                invalidClass:{
                    defaultValue:'m3-form-invalid',
                    isInitValue:true
                }
            }
        },
        textArea:{
            parent:'baseField',
            properties:{
                id:{
                    defaultValue:'New text area',
                    isInitProperty:true
                }
            },
            toolboxData:{
                text:'Text area',
                category:'Fields'
            },
            treeIconCls:'designer-textarea'
        },
        checkBox:{
            parent:'baseField',
            properties: {
                id: {
                    defaultValue:'New check box',
                    isInitProperty:true
                },
                checked: {
                    defaultValue:false
                },
                boxLabel: {
                    defaultValue:''
                }
            },
            toolboxData:{
                text:'Checkbox',
                category:'Fields'
            },
            treeIconCls:'designer-checkbox'
        },
        dateField: {
            parent:'baseField',
            properties: {
                id:{
                    defaultValue:'New datetime field',
                    isInitProperty:true
                }
            },
            toolboxData:{
                text:'Datetime field',
                category:'Fields'
            },
            treeIconCls:'designer-icon-datefield'
        },
        textField:{
            parent:'baseField',
            properties:{
                id:{
                    defaultValue:'New string field',
                    isInitProperty:true
                }
            },
            toolboxData:{
                text:'String field',
                category:'Fields'
            },
            treeIconCls:'designer-icon-text'
        },
        numberField:{
            parent:'baseField',
            properties:{
                id:{
                    defaultValue:'New number field',
                    isInitProperty:true
                },
                decimalSeparator:{
                    defaultValue:'.'
                },
                allowDecimal: {
                    defaultValue:true
                },
                allowNegative: {
                    defaultValue:true
                },
                decimalPrecision: {
                    defaultValue:2
                },
                maxValue : {
                    defaultValue:0
                },
                maxText: {
                    defaultValue:''
                },
                minValue : {
                    defaultValue:0
                },
                minText: {
                    defaultValue:''
                },
                selectOnFocus: {
                    defaultValue: false
                }

            },
            toolboxData:{
                text:'Number field',
                category:'Fields'
            },
            treeIconCls:'designer-icon-number'
        },
        comboBox: {
            //FIXME комбобоксеке не работают
            properties: {
                fieldLabel:{
                    defaultValue:''
                },
                id:{
                    defaultValue:'New text field',
                    isInitProperty:true
                },
                anchor:{
                    defaultValue:'auto'
                },
                triggerAction:{
                    defaultValue:'all',
                    isInitProperty:true
                },
                valueField:{
                    defaultValue:'myId',
                    isInitProperty:true
                },
                displayField:{
                    defaultValue:'displayText',
                    isInitProperty:true
                },
                store:{
                    defaultValue: new Ext.data.ArrayStore({
                                id: 0,
                                fields: [
                                    'myId',
                                    'displayText'
                                ],
                                data: [[1, 'item1'], [2, 'item2']]
                            }),
                    isInitProperty:true
                }
            },
            toolboxData:{
                text:'Combo box',
                category:'Fields'
            },
            treeIconCls:'designer-icon-combo'
        },
        displayField: {
            parent:'baseField',
            properties: {
                id : {
                    defaultValue:'New display field',
                    isInitProperty:true
                },
                value : {
                    defaultValue:'New display field',
                    isInitProperty:true
                }
            },
            toolboxData:{
                text:'Display field',
                category:'Fields'
            },
            treeIconCls:'designer-displayfield'
        },
        hiddenField: {
            properties: {
                id : {
                    defaultValue:'New hidden field',
                    isInitProperty:true
                },
                name : {
                    defaultValue:''
                }
            },
            toolboxData:{
                text:'Hidden field',
                category:'Fields'
            }
        },
        gridPanel:{
            isContainer: true,
            properties: {
                id:{
                    defaultValue:'Grid panel',
                    isInitProperty:true
                },
                title: {
                    defaultValue:'New grid',
                    isInitProperty:true
                },
                autoExpandColumn: {
                    defaultValue:''
                }
            },
            childTypesRestrictions:{
                allowed:['gridColumn','arrayStore'],
                single:['arrayStore']
            },
            treeIconCls:'designer-grid-panel',
            toolboxData:{
                text:'Grid panel',
                category:'Grid'
            }

        },
        gridColumn:{
            properties: {
                id:{
                    //ATTENTION - пробелы в id ведут к багу при наведении мышки на хедер
                    defaultValue:'gridColumn',
                    isInitProperty:true
                },
                name:{
                    defaultValue:'New column',
                    isInitProperty:true
                },
                header:{
                    defaultValue:'New column',
                    isInitProperty:true
                },
                dataIndex:{
                    defaultValue:'Foo',
                    isInitProperty:true
                },
                menuDisabled: {
                    defaultValue:true,
                    isInitProperty:true
                }
            },
            treeIconCls:'designer-grid-column',
            toolboxData: {
                text:'Grid column',
                category:'Grid'
            }
        },
        window:{
            properties: {
                id:{
                    defaultValue:'Ext window',
                    isInitProperty:true
                },
                layout:{
                    defaultValue:'fit',
                    isInitProperty:true,
                    propertyType:'enum'
                },
                title: {
                    defaultValue:'New window',
                    isInitProperty:true
                }
            },
            childTypesRestrictions:{
                disallowed:['arrayStore','gridColumn']
            },
            isContainer:true,
            treeIconCls:'designer-icon-page'
        },
        arrayStore:{
            properties : {
                id: {
                    defaultValue:'New array store',
                    isInitProperty:true
                },
                storeId: {
                    defaultValue:'New store',
                    isInitProperty:true
                },
                idIndex : {
                    defaultValue:0,
                    isInitProperty:true
                },
                fields: {
                    defaultValue:'undefined',
                    propertyType:'object'
                },
                data: {
                    defaultValue:'undefined',
                    propertyType:'object'
                }
            },
            treeIconCls:'icon-database',
            toolboxData: {
                text:'Array store',
                category:'Data'
            }
        }
    }
});