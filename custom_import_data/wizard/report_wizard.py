# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from xlrd import open_workbook
import logging
import tempfile
import base64
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Get_Dict():

    def get_list_dict(self, file, *args):
        book = open_workbook(file)
        sheet = book.sheet_by_index(0)
        keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
        dict_list = []
        for row_index in range(1, sheet.nrows):
            d = {keys[col_index]: sheet.cell(row_index, col_index).value for col_index in range(sheet.ncols)}
            dict_list.append(d)
        return dict_list

class ImportAllData(models.TransientModel):
    _name = "import.all.data"

    name = fields.Char("File Name")
    file = fields.Binary("Upload file", required=True)
    selection_type = fields.Selection(string='Selection', selection=[('partner', 'Partner'),
                                             ('product', 'Product')], default='partner')



    def save_as_temp_file(self, data):
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=".xlsx") as f:
            f.write(base64.decodestring(data))
            return f.name

    @api.multi
    def import_data(self):
        partner_obj = self.env['res.partner']
        product_obj = self.env['product.product']
        product_uom_obj = self.env['uom.uom']
        product_category_obj = self.env['product.category']

        if self.file:
            file_name = self.save_as_temp_file(self.file)
            reader = Get_Dict().get_list_dict(file_name)
            for rec in reader:
                if self.selection_type == 'partner':
                    print("partner rec>>>>>>>>>", rec)
                    if rec['Name']:
                        partner_id = partner_obj.create({
                            'name': rec['Name'],
                            'phone': rec['Telephone No.']
                        })
                    if rec['Contact Person']:
                        partner_obj.create({
                            'name': rec['Contact Person'],
                            'parent_id': partner_id.id
                        })
                if self.selection_type == 'product':
                    print("Product rec>>>>>>>>>", rec)
                    if rec['Name']:
                        product_id = product_obj.create({
                            'name': rec['Name'],
                            'type': 'product',
                        })
                    if rec['UOM']:
                        uom_id = product_uom_obj.search([('name', '=', rec['UOM'])])
                        uom_category_id = self.env['uom.category'].search([('name', '=', 'Length / Distance')])
                        if not uom_id:
                            uom_id = product_uom_obj.create({
                              'name': rec['UOM'],
                               'category_id': uom_category_id.id,
                              'uom_type': 'bigger',
                                'factor_inv': 1.0
                            })
                        product_id.write({
                            'uom_id': uom_id.id,
                            'uom_po_id': uom_id.id,
                        })

                    if rec['Sales Price']:
                        product_id.write({
                            'list_price': rec['Sales Price']
                        })
                    if rec['product category']:
                        category = rec['product category'].split(' / ')

                        parent_id = product_category_obj.search([('name', '=', 'All')])
                        if parent_id:
                            parent_id1 = product_category_obj.search([
                                ('name', '=', category[1]),
                                ('parent_id', '=', parent_id.id)
                            ])
                            if not parent_id1:
                                parent_id1 = product_category_obj.create({
                                    'name': category[1],
                                    'parent_id': parent_id.id,
                                })
                            if parent_id1 and category[2]:
                                category_id = product_category_obj.search([
                                    ('name', '=', category[2]),
                                    ('parent_id', '=', parent_id1.id)
                                ])
                                if not category_id:
                                    category_id = product_category_obj.create({
                                        'name': category[2],
                                        'parent_id': parent_id1.id,
                                    })
                        product_id.write({
                            'categ_id': category_id.id,
                        })


                        # category_id1 = product_category_obj.search([('name', '=', category[1]),
                        #                                            ('parent_id.name', '=', category[0])
                        #                                            ])
                        # product_category_obj





        return True

