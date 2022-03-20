from fileinput import filename
from genericpath import isdir
from flask import Flask, render_template, request, redirect, flash,session
from cs50 import SQL
from flask_session import Session
import os

app = Flask(__name__) 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DB = SQL("sqlite:///database.db")
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)

sections = DB.execute("SELECT section_name from sections order by section_name desc")


@app.route("/")
def index():
    if not session.get("user_id", None):
        return redirect("/login")
    else:
        brands = DB.execute("""
        select a.brandname, a.img_path, a.desc, s.section_name
        from brands a, sections s
        where a.id in (select b.id from brands b where a.section_id = b.section_id order by review limit 1 )
        and a.section_id = s.id;
        """)
        sections = DB.execute("SELECT section_name from sections order by section_name desc limit 5")
        top_brands = DB.execute("""
        select a.brandname, a.img_path, a.desc, s.section_name
        from brands a, sections s
        where a.id in (select b.id from brands b where a.section_id = b.section_id limit 4 )
        and a.section_id = s.id
        """)
        top_pixel = DB.execute("""       
        select brands.desc, brands.img_path
        from brands 
        order by review 
        limit 12
        """)
        top_pixel_visiting = DB.execute("""       
        select brands.desc, brands.img_path
        from brands 
        order by visiting 
        limit 8
        """)
        top_pixel_likes = DB.execute("""       
        select brands.desc, brands.img_path
        from brands 
        order by likes 
        limit 3
        """)
        print(sections)
        print(top_brands)
        print(top_pixel)
        render_template("buy-Pixel.html", sections = sections)
        return render_template("index.html", 
        brands = brands, 
        sections = sections, 
        top_brands = top_brands, 
        top_pixel = top_pixel,
        likes = top_pixel_likes,
        visits = top_pixel_visiting
        )


@app.route("/login", methods=['GET','POST'])
def login():
    if session.get("user_id", None):
        return redirect("/")

    if request.method == 'POST':
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if not email or not password:
            flash("Please fill all Fields", "danger")
            return redirect("/login")

        row = DB.execute("select * from users where email= ?", email)
        if len(row) < 1:
            flash("Users does not exist", "danger")
            return redirect("/login")
        
        if password != row[0]['password']:
            flash("Check Your info", "danger")
            return redirect("/login")

        session['user_id'] = row[0]['id']
        return redirect("/")

    else:
        return render_template("/signin.html")


@app.route("/register" , methods=['GET','POST'])
def register():
    if session.get("user_id", None):
        return redirect("/")

    if request.method == 'POST':
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        confirm_password = request.form.get("confirm_password", None)
        name = request.form.get("name", None)

        if not email or not password or not confirm_password or not name:
            flash("Please Fill all Filds", "danger")
            return redirect("/signin.html")

        if password != confirm_password:
            flash("password not matching!!", "danger")
            return redirect("/signin.html")            

        row = DB.execute("select * from users where email = ?", email)
        if len(row) > 1:
            flash("User alradey exist LOGIN please", "danger")
            return redirect("/signin.html")

        row = DB.execute("insert into users (name, email, password) VALUES (?,?,?)", name, email, password)
        session['user_id'] = row
        return redirect("/")

    else:
        return render_template("/signin.html") 


@app.route("/logout")
def logout():
    if not session.get("user_id", None):
        return redirect("/login")
    del session['user_id']
    return redirect("/login")

# at this time you can access this end point manualy only
@app.route("/buy_pixel" , methods=['GET','POST'])
def buy_pixel():
    if not session.get("user_id", None):
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name", None)
        column = request.form.get("column", None)
        row1 = request.form.get("row", None)
        section = request.form.get("section", None)
        desc = request.form.get("desc", None)

        row = DB.execute("select * from sections where section_name = ?", section)
        if len(row) < 1:
            flash("This Section Is Unvaild", "danger")
            return render_template("/buy-Pixel.html", sections = sections)

        section_id = row[0]['id']
        img_path = ""
        target = os.path.join(APP_ROOT, 'static/brands_covers/')
        if not os.path.isdir(target):
            os.mkdir(target)


        for upload in request.files.getlist("img_brand"):
            img_path = "/".join(['static/brands_covers/', name + '.jpg'])
            upload.save(img_path)
            print(img_path)
        print(session["user_id"])

        DB.execute('insert into brands (user_id, brandname, "column", "row", img_path, section_id, desc) VALUES (?, ?, ?, ?, ?, ?, ?)', session["user_id"], name, column, row1, img_path, section_id, desc)
        return redirect("/")

    else:
        return render_template("/buy-Pixel.html", sections = sections)    

    

@app.route("/review")
def review():
    if not session.get("user_id", None):
        return redirect("/lognin")

@app.route("/delete")
def delete():
    if not session.get("user_id", None):
        return redirect("/lognin")

    # id = request.args.get('id')
    # SELECT * FROM blogs where id=?",id
    # DELETE FROM blogs where id =
    


@app.route("/category")
def category():
    return render_template("/category.html")


@app.route("/services")
def services():
    return render_template("/services.html")


@app.route("/contact", methods=['GET','POST'])
def contact():
    if not session.get("user_id", None):
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name", None)
        email = request.form.get("email", None)
        phone_number = request.form.get("phone_number", None)
        subject = request.form.get("subject", None)
        message = request.form.get("mess", None)

    else:
        return render_template("/contact.html")


@app.route("/pixels")
def pixels():
    return render_template("/pixels.html")


@app.route("/single")    
def single():
    return render_template("/single.html")
    

if __name__ == '__main__':
    app.run(debug=True)