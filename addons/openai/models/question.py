from odoo import models, fields, api

class question(models.Model):
    _name = 'openai.question'
    _description = 'openai.question'

    name = fields.Char(string="Preguntas")
    id_question = fields.Char(string="ID de Preguntas")