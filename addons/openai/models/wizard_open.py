from odoo import models, fields, api

from openai import OpenAI 
from odoo.exceptions import UserError

class wizard_open(models.TransientModel):
    _name = 'openai.wizard_open'
    _description = 'openai.wizard_open'

    name = fields.Char(string="Producto", readonly=True)
    key = fields.Char(compute='api_openai')
    model = fields.Char(compute='api_openai')
    id_product = fields.Char(string="ID", readonly=True)
    attributes = fields.Text(string="Atributos", compute='compute_attributes')
    attributes_values = fields.Many2many("product.template.attribute.line", string=("Atributos"), domain="[('product_tmpl_id', '=', name)]")
    answer_title = fields.Many2one('openai.title', string="titulos", domain="[('id_title', '=', id_product)]")
    answer_description = fields.Many2one('openai.description', string="Descripciones", domain="[('id_description', '=', id_product)]")
    answer_chat = fields.Text(string="Chat", compute="chat")
    description = fields.Text(string="Descripcion", readonly=True)
    question_title = fields.Char(compute='api_openai')
    question_description = fields.Char(compute='api_openai')
    question = fields.Char(string="Pregunta")
    generation = fields.Selection(
        [
            ('titulo','Titulo'),
            ('descripcion','Descripcion'),
            ('preguntas','Preguntas')
        ],
        string="Generar",
        default="titulo",
        required=True
    )


    @api.depends('name')
    def compute_attributes(self):
        for data in self:
            # Obtiene los atributos asociados al producto actual
            attributes = self.env['product.template.attribute.line'].with_context(active_test=False).search([('product_tmpl_id.product_variant_ids.name', '=', data.name)])
            # Construye una cadena con los nombres de los atributos y sus valores
            # utilizando una comprensión de lista
            data.attributes = '\n'.join(['{}: {}'.format(attribute.attribute_id.name, ', '.join([valor.name for valor in attribute.value_ids])) for attribute in attributes])


    @api.model
    def api_openai(self):
        Param = self.env['ir.config_parameter']#Creo una instancia del modelo de los parametros del sistema
        api_key = Param.get_param('OpenAI_key', default='')#Obtengo la api key de la instancia anterior
        self.key = api_key
        api_model = Param.get_param('OpenAI_model', default='')#Obtengo el modelo de la instancia anterior
        self.model = api_model
        api_question_title = Param.get_param('openai.question_title', default='')#Obtengo el mensaje que se le mandara al api  de la instancia anterior
        self.question_title = api_question_title
        api_question_description = Param.get_param('openai.question_description', default='')#Obtengo el mensaje que se le mandara al api de la instancia anterior
        self.question_description = api_question_description


    def structure_api(self, question_api):
        client = OpenAI(api_key=self.key)  # Se crea un cliente de OpenAI utilizando la clave de la API proporcionada
        # Se solicita una respuesta a partir de un mensaje de chat utilizando el cliente de OpenAI
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",  # Se especifica el rol del mensaje como usuario
                    "content": question_api,  # Se proporciona el contenido del mensaje, que es una pregunta
                }
            ],
            model=self.model,  # Se especifica el modelo de lenguaje a utilizar
        )
        list_answer = chat_completion.choices[0].message.content  # Se obtiene la respuesta generada por el modelo de OpenAI
        return list_answer


    def wizard_return(self):
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return {
            'name': 'Generar Datos',
            'type': 'ir.actions.act_window',
            'res_model': 'openai.wizard_open',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_generation': self.generation,  # Establecer el valor de 'generation' en el contexto
                'default_attributes_values': [(6, 0, self.attributes_values.ids)],  # Pasar los valores de los atributos al contexto
            },  
        }


    def generate_titles(self):
        for openai_data in self:
            attributes_values = openai_data.attributes_values
            atributos_con_valores = []  # Se crea una lista vacía para almacenar los atributos con sus valores
            for attribute in attributes_values:  # Se itera sobre cada elemento en attributes_values
                nombre_atributo = attribute.attribute_id.name  # Se obtiene el nombre del atributo
                valores = " ".join(attribute.value_ids.mapped('name'))  # Se obtienen los valores del atributo y se concatenan en una cadena separados por espacio
                atributos_con_valores.append(f"{nombre_atributo}: {valores}\n")  # Se agrega el nombre del atributo y sus valores a la lista atributos_con_valores

            question_api = f"{self.question_title} de {self.name} tomando en cuenta los siguentes atributos: {' '.join(atributos_con_valores)}. separado los titulos por comas, sin números, sin comillas, sin saltos de línea, todo en un párrafo y que no sea una lista"
            list_answer = self.structure_api(question_api).split(',')

            new_answer = []

            for respuest_data in list_answer:  # Itera sobre los datos de los titulos
                responses = self.env['openai.title'].search([('name', '=', respuest_data), ('id_title', '=', self.id_product)], limit=1)  # Busca si el titulo ya existe
                if not responses:  # Si el titulo no existe
                    new_answer.append({  # Agrega el nuevo titulo a la lista
                        'name': respuest_data,
                        'id_title': self.id_product,
                    })
            if new_answer:  # Si hay nuevos titulos
                with self.env.cr.savepoint():  # Crea un punto de guardado en la transacción de base de datos actual
                    self.env['openai.title'].create(new_answer)  # Crea nuevos titulos
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return self.wizard_return()


    def generate_description(self):
        attributes_values = self.attributes_values
        atributos_con_valores = []  # Se crea una lista vacía para almacenar los atributos con sus valores
        for attribute in attributes_values:  # Se itera sobre cada elemento en attributes_values
            nombre_atributo = attribute.attribute_id.name  # Se obtiene el nombre del atributo
            valores = " ".join(attribute.value_ids.mapped('name'))  # Se obtienen los valores del atributo y se concatenan en una cadena separados por espacio
            atributos_con_valores.append(f"{nombre_atributo}: {valores}\n")  # Se agrega el nombre del atributo y sus valores a la lista atributos_con_valores

        question_api = f"{self.question_description} del producto {self.name} con esta información {' '.join(atributos_con_valores)}, sin colocar “dos puntos” al inicio."
        list_answer = self.structure_api(question_api)

        new_answer = []

        responses = self.env['openai.description'].search([('name', '=', list_answer), ('id_description', '=', self.id_product)], limit=1)  # Busca si la descripción ya existe
        if not responses:  # Si la descripción no existe
            new_answer.append({  # Agrega la nueva descripción a la lista
                'name': list_answer,
                'id_description': self.id_product,
            })
        if new_answer:  # Si hay nuevas descripciones
            with self.env.cr.savepoint():  # Crea un punto de guardado en la transacción de la base de datos actual
                self.env['openai.description'].create(new_answer)  # Crea nuevas descripciones
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return self.wizard_return()


    @api.onchange("answer_chat")
    def chat(self):
        responses = self.env['openai.question'].search([('id_question', '=', self.id_product)])  # Busca todas las respuestas relacionadas con el producto actual
        number_of_responses = self.env['openai.question'].search_count([('id_question', '=', self.id_product)])  # Cuenta cuántas respuestas se encontraron
        
        lista = []  # Lista para almacenar los nombres de las respuestas
        
        if number_of_responses > 1:
            # Itera sobre todas las respuestas y agrega sus nombres a la lista
            for i in responses:
                lista.append(i.name + "\n\n")
            string = ' '.join(lista)  # Une todos los nombres en una cadena
            self.answer_chat = string  # Asigna la cadena de respuestas al campo "answer_chat"
        else:
            self.answer_chat = responses.name  # Si solo se encontró una respuesta, asigna su nombre al campo "answer_chat"


    def generate_question(self):
        if not self.question:
            raise UserError("Por favor agregue una pregunta antes de generar.")  # Muestra una alerta si el campo de pregunta está vacío
        question_api = f"{self.question} el producto {self.name} con los siguientes datos {self.attributes}"
        list_answer = self.question+"\n"+self.structure_api(question_api)
        
        new_answer = []
        
        responses = self.env['openai.question'].search([('name', '=', list_answer), ('id_question', '=', self.id_product)], limit=1)  # Busca si la descripcion ya existe
        if not responses:  # Si la descripcion no existe
            new_answer.append({  # Agrega la nueva descripcion a la lista
                'name': list_answer,
                'id_question': self.id_product,
            })
        if new_answer:  # Si hay nuevas descripcions
            with self.env.cr.savepoint():  # Crea un punto de guardado en la transacción de base de datos actual
                self.env['openai.question'].create(new_answer)  # Crea nuevas descripciones
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return self.wizard_return()


    @api.onchange("answer_title")
    def update_name(self):
        if self.answer_title:
            self.write({'name': self.answer_title.name})  # Actualizar el campo 'name' del asistente


    def save_name(self):
        if not self.answer_title:
            raise UserError("Por favor seleccione un título antes de guardar.")  # Muestra una alerta si no se ha seleccionado un título
        self.env['product.template'].browse(self.env.context.get('product_id')).write({'name': self.answer_title.name})  # Actualizar el campo 'name' del producto
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return self.wizard_return()


    @api.onchange("answer_description")
    def update_description(self):
        if self.answer_description:
            self.write({'description': self.answer_description.name})  # Actualizar el campo 'description' del asistente


    def save_description(self):
        if not self.answer_description:
            raise UserError("Por favor seleccione una descripcion antes de guardar.")  # Muestra una alerta si no se ha seleccionado una descripcion
        self.env['product.template'].browse(self.env.context.get('product_id')).write({'description_sale': self.answer_description.name})  # Actualizar el campo 'description_sale' del producto
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return self.wizard_return()


    def delete_generated_titles(self):
        # Eliminar los títulos generados para un producto
        generated_titles = self.env['openai.title'].search([
            ('id_title', '=', self.id_product)
        ])
        generated_titles.unlink()
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return self.wizard_return()


    def delete_generated_description(self):
        # Eliminar las descripciones generados para un producto
        generated_description = self.env['openai.description'].search([
            ('id_description', '=', self.id_product)
        ])
        generated_description.unlink()
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return self.wizard_return()


    def delete_generated_question(self):
        # Eliminar las preguntas generados para un producto
        generated_question = self.env['openai.question'].search([
            ('id_question', '=', self.id_product)
        ])
        generated_question.unlink()
        # Devuelve una acción para mantener abierta la ventana del wizard en el mismo paso
        return self.wizard_return()


    @api.model
    def default_get(self, fields):
        res = super(wizard_open, self).default_get(fields)
        # Filtrar los atributos asociados al producto seleccionado
        res['name'] = self.env.context.get('product_name', '')  # Establecer el valor del campo 'name' con el nombre del producto
        res['description'] = self.env.context.get('product_description', '') # Establecer el valor del campo 'descripcion' con el nombre del producto
        res['id_product'] = self.env.context.get('product_id', '')  # Establecer el valor del campo 'id_product' con el id del producto del producto
        return res