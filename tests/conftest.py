import json
from typing import NamedTuple

import pytest
from click.testing import CliRunner

from bocadillo import App, API, Templates, Recipe


# Tests that use the `app` fixture will run once for each of these
# application classes.
APP_CLASSES = [App, API, lambda: Recipe("tacos")]


@pytest.fixture(params=APP_CLASSES)
def app(request):
    cls = request.param
    return cls()


@pytest.fixture
def templates(app: App):
    return Templates(app)


class TemplateWrapper(NamedTuple):
    name: str
    context: dict
    rendered: str
    root: str


def create_template(
    templates: Templates, tmpdir_factory, dirname: str
) -> TemplateWrapper:
    templates_dir = tmpdir_factory.mktemp(dirname)

    template = templates_dir.join("hello.html")
    template.write("<h1>Hello, {{ name }}!</h1>")

    templates.directory = str(templates_dir)

    return TemplateWrapper(
        name="hello.html",
        context={"name": "Bocadillo"},
        rendered="<h1>Hello, Bocadillo!</h1>",
        root=str(templates_dir),
    )


@pytest.fixture
def template_file(templates: Templates, tmpdir_factory) -> TemplateWrapper:
    return create_template(templates, tmpdir_factory, dirname="templates")


@pytest.fixture
def runner():
    return CliRunner()
