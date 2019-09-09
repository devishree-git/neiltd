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

    def save_as_temp_file(self, data):
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=".xlsx") as f:
            f.write(base64.decodestring(data))
            return f.name

    @api.multi
    def import_data(self):
        partner_obj = self.env['res.partner']
        if self.file:
            file_name = self.save_as_temp_file(self.file)
            reader = Get_Dict().get_list_dict(file_name)
            for rec in reader:
                print("rec>>>>>>>>>", rec)
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
        return True

