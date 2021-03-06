# ==================== Cafe Website Main Module ==================== #
#
# Minimalistic implementation.
# Could be improved implementing fancier layout and responsive design

# Import needed modules
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField

# Start Flask Application
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# Create Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create DB Table
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
db.create_all()

# Define Add Cafe form
class AddingForm(FlaskForm):
    name = StringField('Cafe Title: ')
    map_url = StringField('Map URL: ')
    img_url = StringField('Image URL: ')
    location = StringField('Location: ')
    seats = StringField('Seats: ')
    has_toilet = BooleanField('Restroom: ')
    has_wifi = BooleanField('WiFi: ')
    has_sockets = BooleanField('Power Sockets: ')
    can_take_calls = BooleanField('Takes Calls: ')
    coffee_price = StringField('Coffee Price: ')
    submit = SubmitField('Add Cafe')

# Define Filters class (to be used with class variables and static methods)
class Filters:
    # Define and initialize filters
    on_toilet = False
    on_wifi = False
    on_sockets = False
    on_calls = False
    # Define function to check if a cafe respects the applied filters
    @classmethod
    def selected(cls, cafe):
        if Filters.on_toilet and not cafe.has_toilet:
            return False
        if Filters.on_wifi and not cafe.has_wifi:
            return False
        if Filters.on_sockets and not cafe.has_sockets:
            return False
        if Filters.on_calls and not cafe.can_take_calls:
            return False
        return True

# Display Main Page
@app.route('/')
def home():
    all_cafes = db.session.query(Cafe).all()
    #selected_cafes = []
    #for cafe in all_cafes:
    #    if Filters.selected(cafe):
    #        selected_cafes.append(cafe)
    selected_cafes = [cafe for cafe in all_cafes if Filters.selected(cafe)]
    return render_template("index.html",
                           cafes=selected_cafes,
                           filter_on_restroom=Filters.on_toilet,
                           filter_on_network=Filters.on_wifi,
                           filter_on_power=Filters.on_sockets,
                           filter_on_contact=Filters.on_calls)

# Display "Add Cafe" form
@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    adding_form=AddingForm()
    if request.method == "POST":
        #print("Adding Form received")
        if adding_form.validate_on_submit():
            #print("Adding Form validated")
            # Get cafe info from the form compiled in add-html
            cafe_name = adding_form.name.data
            cafe_map = adding_form.map_url.data
            cafe_img = adding_form.img_url.data
            cafe_location = adding_form.location.data
            cafe_seats = adding_form.seats.data
            cafe_toilet = adding_form.has_toilet.data
            cafe_wifi = adding_form.has_wifi.data
            cafe_sockets = adding_form.has_sockets.data
            cafe_calls = adding_form.can_take_calls.data
            cafe_price = adding_form.coffee_price.data
            # Insert new cafe in the Database
            new_cafe = Cafe(name=cafe_name,
                            map_url=cafe_map,
                            img_url=cafe_img,
                            location=cafe_location,
                            seats=cafe_seats,
                            has_toilet=cafe_toilet,
                            has_wifi=cafe_wifi,
                            has_sockets=cafe_sockets,
                            can_take_calls=cafe_calls,
                            coffee_price=cafe_price,
                            )
            db.session.add(new_cafe)
            db.session.commit()
            # Go back to main page
            return redirect(url_for('home'))
        else:
            #print("Adding Form not validated")
            return redirect(url_for('home'))
    else:   # request.method == "GET"
        #print("Presenting Adding Form")
        return render_template('add.html', form=adding_form)

# Implement "Delete Cafe" action
@app.route("/delete/<cafe_id>")
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

# Implement "Filter" action
@app.route("/filter/<filter_id>")
def set_filter(filter_id):
    if filter_id == "Restroom":
        Filters.on_toilet = not Filters.on_toilet
    elif filter_id == "WiFi":
        Filters.on_wifi = not Filters.on_wifi
    elif filter_id == "Sockets":
        Filters.on_sockets = not Filters.on_sockets
    elif filter_id == "Takes_Calls":
        Filters.on_calls = not Filters.on_calls
    elif filter_id == "Reset_All":
        Filters.on_toilet = False
        Filters.on_wifi = False
        Filters.on_sockets = False
        Filters.on_calls = False
    return redirect(url_for('home'))

# Run the Application
if __name__ == "__main__":
    app.run(debug=True)

