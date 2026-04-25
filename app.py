from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'suryam-sustainable-secret-2026'

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50))
    details = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return render_template('index.html', name=current_user.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/search', methods=['POST'])
@login_required
def search_brand():
    try:
        data = request.get_json()
        query = data.get('brand', '').lower().strip()
        brand = Brand.query.filter_by(name=query).first()
        
        if brand:
            ai_tip = f"✅ Great choice! This brand aligns with circular economy goals." if brand.rating > 3 else f"⚠️ Warning: High environmental impact detected."
            return jsonify({
                "found": True, 
                "name": brand.name.capitalize(), 
                "rating": brand.rating, 
                "status": brand.status, 
                "details": brand.details, 
                "ai_tip": ai_tip
            })
        
        return jsonify({
            "found": False, 
            "message": f"Brand '{query}' not in local database.", 
            "link": f"https://goodonyou.eco/search/{query}"
        })
    except Exception as e:
        return jsonify({"found": False, "message": "Server Error"}), 500

def seed():
    with app.app_context():
        db.create_all()
        # Create Lead Developer Account
        if not User.query.filter_by(username='Suryam').first():
            db.session.add(User(username='Suryam', password='password123'))
        
        # Seed Global Brand Database
        if not Brand.query.first():
            brands = [
                # --- SUSTAINABILITY LEADERS (4-5/5) ---
                Brand(name="patagonia", rating=5, status="Elite", details="Gold standard for transparency. Uses 87% recycled materials and offers a lifetime 'Worn Wear' repair service."),
                Brand(name="veja", rating=5, status="Elite", details="Pioneer in ecological sneakers. Sources Amazonian rubber and organic cotton directly from farmers with no middlemen."),
                Brand(name="stella mccartney", rating=4, status="Superior", details="Luxury leader in animal welfare. Completely leather and fur-free, using innovative 'Mylo' mushroom leather."),
                Brand(name="levis", rating=4, status="Superior", details="Leading water conservation through 'Water<Less' techniques and promoting denim circularity."),
                Brand(name="adidas", rating=4, status="Superior", details="Committed to ending plastic waste. Massive production of footwear made from 'Parley Ocean Plastic'."),

                # --- MASS MARKET / TRANSITIONING (3/5) ---
                Brand(name="nike", rating=3, status="Average", details="Aggressive climate targets, but significant labor transparency gaps remain in the lower tiers of the supply chain."),
                Brand(name="h&m", rating=3, status="Average", details="Leads in textile recycling, but the high-volume business model remains a significant sustainability challenge."),
                Brand(name="puma", rating=3, status="Average", details="Strong biodiversity and climate targets, though transparency in worker empowerment needs improvement."),
                Brand(name="gap", rating=3, status="Average", details="Improving cotton sourcing, but still rooted in a resource-heavy production model with high waste."),

                # --- HIGH RISK / FAST FASHION (1-2/5) ---
                Brand(name="zara", rating=2, status="Warning", details="Owned by Inditex. Business model relies on extreme fast fashion turnover, creating immense pressure on resources."),
                Brand(name="uniqlo", rating=2, status="Warning", details="Lacks transparency in environmental reporting and faces scrutiny regarding ethical sourcing in certain regions."),
                Brand(name="shein", rating=1, status="Critical", details="Ultra-fast fashion. Evidence of hazardous chemical use and fundamentally unsustainable production volumes."),
                Brand(name="fashion nova", rating=1, status="Critical", details="Almost zero transparency. Does not disclose factory locations or environmental protection policies."),
                Brand(name="forever 21", rating=1, status="Critical", details="Regularly fails ethical audits. Provides no public data regarding its carbon footprint or chemical management.")
           
           
            ]

            db.session.bulk_save_objects(brands)
            db.session.commit()
            print("Global Brand Database Initialized Successfully.")


    # --- FINAL FIX FOR DEPLOYMENT ---
# This section ensures the database and initial data are ready on the server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Physically creates the .db file and tables
        seed()           # Fills the tables with your brands and user
    app.run()