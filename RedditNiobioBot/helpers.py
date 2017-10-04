from jinja2 import Environment, FileSystemLoader


# carrega o arquivo template da pasta templates/
# renderiza e retorna
def render_template(template_name, **kwargs):
    environment = Environment(loader=FileSystemLoader('templates'))
    template = environment.get_template(template_name)
    return template.render(kwargs)
