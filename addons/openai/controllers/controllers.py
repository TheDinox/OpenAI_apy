# -*- coding: utf-8 -*-
# from odoo import http


# class OpenaiRecommendations(http.Controller):
#     @http.route('/openai_recommendations/openai_recommendations', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/openai_recommendations/openai_recommendations/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('openai_recommendations.listing', {
#             'root': '/openai_recommendations/openai_recommendations',
#             'objects': http.request.env['openai_recommendations.openai_recommendations'].search([]),
#         })

#     @http.route('/openai_recommendations/openai_recommendations/objects/<model("openai_recommendations.openai_recommendations"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('openai_recommendations.object', {
#             'object': obj
#         })

