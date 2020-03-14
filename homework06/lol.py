from bottle import route, run, template

@route('/')
@route('/hello/<name>')
def index(name="Stranger"):
    return template('<b>Hello {{name}}</b>!', name=name)

run(host='localhost', port=8080)