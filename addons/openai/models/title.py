from odoo import models, fields, api
class title(models.Model):
    _name = 'openai.title'
    _description = 'openai.title'

    
    name = fields.Char(string="Titulo")
    id_title = fields.Char(string="ID de Titulo")

