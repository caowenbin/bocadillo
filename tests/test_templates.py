import pytest
from bocadillo import App
from jinja2.exceptions import TemplateNotFound

from bocadillo import Templates

from .conftest import TemplateWrapper, create_template


@pytest.mark.asyncio
async def test_render(template_file: TemplateWrapper, templates: Templates):
    html = await templates.render(template_file.name, **template_file.context)
    assert html == template_file.rendered


@pytest.mark.asyncio
async def test_render_using_dict(
    template_file: TemplateWrapper, templates: Templates
):
    html = await templates.render(template_file.name, template_file.context)
    assert html == template_file.rendered


def test_render_sync(template_file: TemplateWrapper, templates: Templates):
    html = templates.render_sync(template_file.name, **template_file.context)
    assert html == template_file.rendered


def test_render_string(templates: Templates):
    html = templates.render_string("<h1>{{ title }}</h1>", title="Hello")
    assert html == "<h1>Hello</h1>"


@pytest.mark.asyncio
async def test_modify_templates_dir(templates: Templates, tmpdir_factory):
    template = create_template(templates, tmpdir_factory, dirname="elsewhere")
    html = await templates.render(template.name, **template.context)
    assert html == template.rendered


@pytest.mark.asyncio
async def test_if_template_does_not_exist_then_not_found_raised(
    templates: Templates
):
    with pytest.raises(TemplateNotFound):
        await templates.render("doesnotexist.html")


def test_url_for(app: App, templates: Templates):
    @app.route("/about/{who}")
    async def about(req, res, who):
        pass

    @app.route("/")
    async def index(req, res):
        template = "{{ url_for('about', who=who) }}"
        res.html = templates.render_string(template, who="me")

    response = app.client.get("/")
    assert response.status_code == 200
    assert response.text == "/about/me"


def test_use_without_app():
    templates = Templates()
    assert templates.render_string("foo") == "foo"
