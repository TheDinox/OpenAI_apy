from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def open_wizard(self):
        return {
            'name': 'Generar Datos', # Título de la ventana del asistente
            'type': 'ir.actions.act_window', # Tipo de acción: ventana emergente
            'res_model': 'openai.wizard_open', # Modelo del asistente
            'view_mode': 'form', # Modo de vista: formulario
            'target': 'new', # Abrir en una nueva ventana
            'context': {
                'product_name': self.name,  # Pasar el nombre del producto
                'product_id': self.id,  # Pasar el ID del producto
                'product_description': self.description_sale,  # Pasar la descripcion del producto
            }
        }