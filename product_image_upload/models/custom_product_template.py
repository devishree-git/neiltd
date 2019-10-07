# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
import os.path
import base64


class ProductTemplate(models.Model):
    _inherit = "product.template"

    custom_main_image = fields.Char(String='Custom Main Images')
    custom_product_image_ids = fields.Char(String='Custom Product Image Ids')

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if res.custom_product_image_ids:
            product_image_ids = list(res.custom_product_image_ids.split(','))
            for ids in product_image_ids:
                if ids:
                    prod_img_obj = self.env['product.image'].search([('id', '=', int(ids))])
                    prod_img_obj.write({'product_tmpl_id': res.id})
            res.custom_product_image_ids = None
        if 'product_image_ids' in vals:
            self.env['product.image']._get_image_values(
                res.name, res.id, vals.get('product_image_ids'))
        if 'custom_main_image' in vals:
            self._get_main_image(vals.get('custom_main_image'))
        return res

    @api.multi
    def write(self, vals):

        res = super(ProductTemplate, self).write(vals)
        if self.custom_product_image_ids:
            product_image_ids = list(self.custom_product_image_ids.split(','))
            for ids in product_image_ids:
                if ids:
                    prod_img_obj = self.env['product.image'].search([('id', '=', int(ids))])
                    prod_img_obj.write({'product_tmpl_id': self.id})
            self.custom_product_image_ids = None
        if 'product_image_ids' in vals:
            self.env['product.image']._get_image_values(
                self.name, self.id, vals.get('product_image_ids'))
        if 'custom_main_image' in vals:
            self._get_main_image(vals.get('custom_main_image'))
        return res

    def _get_main_image(self, vals):
        default_path = '/static/src/img'
        abspath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if vals:
            file_name = os.path.join(abspath + default_path + vals)
            try:
                with open(file_name, "rb") as imageFile:
                    if imageFile:
                        image = base64.b64encode(imageFile.read())
                        super(ProductTemplate, self).write({'image': image, 'id': id})
            except (OSError, IOError):
                pass
        return True


class ProductImage(models.Model):
    _inherit = 'product.image'

    custom_product_images = fields.Char(String='Custom Product Images')
    custom_product_images_names = fields.Char(String='Custom Product Images')

    def _get_image_values(self, name, id, vals):
        default_path = '/static/src/img'
        abspath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if vals:
            if isinstance(vals[0][2], dict):
                if 'custom_product_images' in vals[0][2] or 'custom_product_images_names' in vals[0][2]:
                    image_lst = []
                    images_names_lst = []
                    image_names = []

                    if vals[0][2].get('custom_product_images'):
                        images = vals[0][2].get('custom_product_images')
                        image_lst = images.split(',')

                    if vals[0][2].get('custom_product_images_names'):
                        images_name = vals[0][2].get('custom_product_images_names')
                        images_names_lst = images_name.split(',')

                    if images_names_lst and image_lst:
                        if len(images_names_lst) < len(image_lst):
                            temp = 0
                            for x in image_lst:
                                if len(images_names_lst) <= temp:
                                    image_names.append(name)
                                else:
                                    image_names.append(images_names_lst[temp])
                                temp += 1

                            for image, image_name in zip(image_lst, image_names):
                                file_name = os.path.join(abspath + default_path + image)
                                if file_name:
                                    try:
                                        with open(file_name, "rb") as imageFile:
                                            if imageFile:
                                                image = base64.b64encode(imageFile.read())
                                                super(ProductImage, self).create(
                                                    {'name': image_name, 'image': image, 'product_tmpl_id': id})
                                    except (OSError, IOError):
                                        pass

                        else:
                            for image, image_name in zip(image_lst, images_names_lst):
                                file_name = os.path.join(abspath + default_path + image)
                                if file_name:
                                    try:
                                        with open(file_name, "rb") as imageFile:
                                            if imageFile:
                                                image = base64.b64encode(imageFile.read())
                                                super(ProductImage, self).create(
                                                    {'name': image_name, 'image': image, 'product_tmpl_id': id})
                                    except (OSError, IOError):
                                        pass

                    elif image_lst:
                        for image in image_lst:
                            file_name = os.path.join(abspath + default_path + image)
                            if file_name:
                                try:
                                    with open(file_name, "rb") as imageFile:
                                        if imageFile:
                                            image = base64.b64encode(imageFile.read())
                                            super(ProductImage, self).create(
                                                {'name': name, 'image': image, 'product_tmpl_id': id})
                                except (OSError, IOError):
                                    pass
        return True

    @api.model
    def create(self, vals):
        ress = super(ProductImage, self).create(vals)
        for res in ress:
            if res.name == False or res.image == False:
                obj = super(ProductImage, self).search([('id', '=', res.id)])
                obj.unlink()
        return res


class Import(models.TransientModel):
    _inherit = 'base_import.import'

    @api.multi
    def _parse_import_data(self, data, import_fields, options):
        template = super(Import, self)._parse_import_data(data, import_fields, options)
        if 'product_variant_ids/attribute_line_ids/attribute_id' in import_fields:
            index_attr = import_fields.index('product_variant_ids/attribute_line_ids/attribute_id')
            for data_line in data:
                prod_attr_obj = self.env['product.attribute'].search(
                    [('name', '=', data_line[index_attr])])

                if not prod_attr_obj:
                    self.env['product.attribute'].create(
                        {'name': data_line[index_attr], 'create_variant': True})
                    prod_attr_obj = self.env['product.attribute'].search(
                        [('name', '=', data_line[index_attr])])

                if 'product_variant_ids/attribute_line_ids/value_ids' in import_fields:
                    index_attr_val = import_fields.index(
                        'product_variant_ids/attribute_line_ids/attribute_id')
                    attr_values = data_line[index_attr_val].split(',')
                    for value in attr_values:
                        prod_attr_value_obj = self.env['product.attribute.value'].search(
                            [('name', '=', value)])
                        if not prod_attr_value_obj:
                            self.env['product.attribute.value'].create(
                                {'name': value, 'attribute_id': prod_attr_obj.id})
                        else:
                            pass

        if 'custom_main_image' in import_fields:
            index = import_fields.index('custom_main_image')
            for data_line in data:
                default_path = '/static/src/img'
                abspath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if data_line[index]:
                    file_name = os.path.join(abspath + default_path + data_line[index])
                    try:
                        with open(file_name, "rb") as imageFile:
                            if imageFile:
                                image = base64.b64encode(imageFile.read())
                                import_fields[index] = 'image'
                                data_line[index] = image
                    except (OSError, IOError):
                        pass

        if 'product_image_ids/custom_product_images_names' in import_fields and 'product_image_ids/custom_product_images' in import_fields and 'name' in import_fields:
            index_name = import_fields.index('product_image_ids/custom_product_images_names')
            index_image = import_fields.index('product_image_ids/custom_product_images')
            index_product_name = import_fields.index('name')
            for data_line in data:
                if data_line[index_image] or data_line[index_name]:
                    image_lst = []
                    images_names_lst = []
                    image_names = []
                    product_image_ids = ''

                    images = data_line[index_image]
                    image_lst = images.split(',')

                    if data_line[index_name]:
                        images_name = data_line[index_name]
                        images_names_lst = images_name.split(',')

                    name = data_line[index_product_name]

                    default_path = '/static/src/img'
                    abspath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

                    if len(images_names_lst) < len(image_lst):
                        temp = 0
                        for image in image_lst:
                            if len(images_names_lst) <= temp:
                                image_names.append(name)
                            else:
                                image_names.append(images_names_lst[temp])
                            temp += 1

                        for image, image_name in zip(image_lst, image_names):
                            file_name = os.path.join(abspath + default_path + image)

                            if file_name:
                                try:
                                    with open(file_name, "rb") as imageFile:
                                        if imageFile:
                                            image_binary = base64.b64encode(imageFile.read())

                                            self.env['product.image'].create(
                                                {'name': image_name, 'image': image_binary})
                                            prod_img_obj = self.env['product.image'].search(
                                                [], limit=1, order="id desc")
                                            product_image_ids += str(prod_img_obj.id) + ','
                                except (OSError, IOError):
                                    pass
                    else:
                        for image, image_name in zip(image_lst, images_names_lst):
                            file_name = os.path.join(abspath + default_path + image)

                            if file_name:
                                try:
                                    with open(file_name, "rb") as imageFile:
                                        if imageFile:
                                            image_binary = base64.b64encode(imageFile.read())
                                            self.env['product.image'].create(
                                                {'name': image_name, 'image': image_binary})
                                            prod_img_obj = self.env['product.image'].search(
                                                [], limit=1, order="id desc")
                                            product_image_ids += str(prod_img_obj.id) + ','
                                except (OSError, IOError):
                                    pass

                    import_fields[index_name] = 'custom_product_image_ids'
                    data_line[index_name] = product_image_ids
                del data_line[index_image]
            del import_fields[index_image]

        if 'product_image_ids/custom_product_images' in import_fields and 'name' in import_fields and 'product_image_ids/custom_product_images_names' not in import_fields:
            index_image = import_fields.index('product_image_ids/custom_product_images')
            index_product_name = import_fields.index('name')

            for data_line in data:
                if data_line[index_product_name] and data_line[index_image]:
                    image_lst = []
                    product_image_ids = ''

                    images = data_line[index_image]
                    image_lst = images.split(',')

                    image_name = data_line[index_product_name]
                    default_path = '/static/src/img'
                    abspath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

                    if image_lst:
                        for image in image_lst:
                            file_name = os.path.join(abspath + default_path + image)
                            if file_name:
                                try:
                                    with open(file_name, "rb") as imageFile:
                                        if imageFile:
                                            image_binary = base64.b64encode(imageFile.read())
                                            self.env['product.image'].create(
                                                {'name': image_name, 'image': image_binary})
                                            prod_img_obj = self.env['product.image'].search(
                                                [], limit=1, order="id desc")
                                            product_image_ids += str(prod_img_obj.id) + ','
                                except (OSError, IOError):
                                    pass
                    import_fields[index_image] = 'custom_product_image_ids'
                    data_line[index_image] = product_image_ids
        return template
