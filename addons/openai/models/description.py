from odoo import models, fields, api

class description(models.Model):
    _name = 'openai.description'
    _description = 'openai.description'

    name = fields.Char(string="Descripciones")
    id_description = fields.Char(string="ID de Descripciones")