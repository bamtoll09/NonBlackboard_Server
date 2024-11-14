from flask import Flask, render_template, request, Response

import combine

port = 8080
debug = True

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.post('/')
def login():
    datas = request.form.to_dict()

    id = datas['id'].strip()
    pw = datas['pw'].strip()

    print(datas)

    if id == '' or pw == '':
        return Response("ID or Password can not be empty!", status=202, content_type="text/plain; charset=utf-8")
        
    status_code, message = combine.connect(id, pw)

    print(status_code)

    return Response(message, status=status_code, content_type="text/plain; charset=utf-8")

if __name__ == '__main__':
    app.run('0.0.0.0', port=port, debug=debug)