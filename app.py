import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.secret_key = 'ark3q2kq@kef3ki2bwi32k25$lw'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=b7d5addc12f8a2f247c48f7c32781141"
    r = requests.get(url.format(city)).json()

    return r

@app.route('/')
def index_get():
    weather_data = []
    cities = City.query.all()

    for city in cities:
        r = get_weather_data(city.name);
        weather = {
        'city':city.name,
        'temperature':r['main']['temp'],
        'description':r['weather'][0]['description'],
        'icon': r['weather'][0]['icon'],
        }
        # print(r)
        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data[::-1])



@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod']==200:
                new_city_obj =  City(name=new_city)
                db.session.add_all([new_city_obj])
                db.session.commit()
            else:
                err_msg = 'City does not exist in the world!'
        else:
            err_msg = 'City already exists in the databse!'
    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully!')
    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f'Successfully deleted { name }', 'success')
    return redirect(url_for('index_get'))
