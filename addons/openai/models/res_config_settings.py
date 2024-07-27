from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    question_title = fields.Char(string="Pregunta para titulos", config_parameter='openai.question_title')
    question_description = fields.Char(string="Pregunta para descripcion", config_parameter='openai.question_description')
