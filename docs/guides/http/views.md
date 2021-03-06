# Views

Once that a route is defined with a well-designed URL pattern (see [Routes and URL design]), you'll need to write the **view** to handle the request and shape up the response.

In Bocadillo, views are functions that take at least a request and a response
as arguments, and mutate those objects as necessary.

Views can be asynchronous or synchronous, function-based or class-based.

## A simple view

Here's a view that returns the current date and time in a JSON object:

```python
import datetime

async def current_datetime(req, res):
    now = datetime.datetime.now()
    res.media = {'now': now.isoformat()}
```

Let's break this code down:

- First, we import the `datetime` module.
- Then, we define an `async` function called `current_datetime` — this is the view function. A view function takes a [`Request`][Request] and a [`Response`][Response] (in this order) as its first two arguments, which are typically called `req` and `res` respectively.

::: tip
The view function's name is used by Bocadillo when the view is associated to the route. See [naming routes].
:::

- Next, we grab the current date and time and build a dictionary out of it.
- Finally, we assign this dictionary to `res.media`, which results in returning a JSON response.

Note that **the view function does not return the response object**. Indeed, in Bocadillo, you shape up the response by mutating the `res` object directly, like we did here by assigning `res.media`.

For more information on working with requests and responses, check out our [Request] and [Response] API guides.

## Mapping URLs to views

As you have seen above, a view is merely just a Python function. To attach it to an URL pattern, you'll need to decorate it with a route. See [Routes and URL design] for more information.

## Returning HTTP errors

Returning an HTTP error response in reaction to an exception or something that went wrong is a common pattern for which Bocadillo provides a special `HTTPError` exception.

If you raise an `HTTPError` inside a view, Bocadillo will catch it and
return an appropriate response.

As an example, consider the following route:

```python
from bocadillo import HTTPError

@app.route('/fail/{status_code:d}')
def fail(req, res, status_code: int):
    raise HTTPError(status_code, detail="You asked for it!")
```

Let's call `/fail/403`, to see what it returns:

```bash
curl -SD - "http://localhost:8000/fail/403"
```

```http
HTTP/1.1 403 Forbidden
server: uvicorn
date: Wed, 07 Nov 2018 19:55:56 GMT
content-type: text/plain
transfer-encoding: chunked

Forbidden
You asked for it!
```

As you can see, it returned a `403 Forbidden` response — this is the HTTP error handler in action.

We will go through how `HTTPError` and error handling in general works in the next section.

## Types of views

Views can be asynchronous or synchronous, function-based or class-based.

### Asynchronous views

The recommended way to define views in Bocadillo is using the async/await syntax. This allows you to call arbitrary asynchronous Python code:

```python
from asyncio import sleep
from bocadillo import view

async def find_post_content(slug: str):
    await sleep(1)  # perhaps query a database here?
    return 'My awesome post'

@view()
async def retrieve_post(req, res, slug: str):
    res.text = await find_post_content(slug)
```

::: tip

> Is `view()` necessary here?

TL;DR: **no**.

The role of the `view()` decorator is to build a class-based view out of a function-based view. This is because internally, Bocadillo only deals with class-based views.

Lucky you! We hide this implementation detail from you by automatically decorating function-based views when registering them via `@app.route()`.
:::

### Synchronous views

While Bocadillo is asynchronous at its core, you can also use plain Python functions to define synchronous views:

```python
@view()
def index(req, res):
    res.html = '<h1>My website</h1>'
```

**Note**: it is generally more
efficient to use asynchronous views rather than synchronous ones.
This is because, when given a synchronous view, Bocadillo needs to perform
a sync-to-async conversion, which might add extra overhead.

### Class-based views

The previous examples were function-based views, but Bocadillo also supports
class-based views.

Class-based views are regular Python classes (there is no base `View` class).
Each HTTP method gets mapped to the corresponding method on the
class. For example, `GET` gets mapped to `.get()`,
`POST` gets mapped to `.post()`, etc.

Other than that, class-based view methods are just regular views:

```python
class Index:

    async def get(self, req, res):
        res.text = 'Classes, oh my!'
       
    def post(self, req, res):
        res.text = 'Roger that'
```

A catch-all `.handle()` method can also be implemented to process all incoming
requests — resulting in other methods being ignored.

```python
class Index:

    async def handle(self, req, res):
        res.text = 'Post it, get it, put it, delete it.'
```

## About type annotations

You may have seen in the previous examples that we sometimes use type hints to annotate view arguments, such as the request, the response or route parameters.

However, **type annotations are not used at all by Bocadillo**.

Future features may rely on type annotations if we think they improve the user experience. But for now, you can safely omit type annotations on your views — although we recommend you do use them, especially for route parameters.

[Routes and URL design]: routing.md
[naming routes]: routing.md#naming-routes
[Request]: requests.md
[Response]: responses.md
