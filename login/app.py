from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session


# Create a blueprint so this login UI can be mounted into the main app
login_bp = Blueprint(
    "login",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/login/static",
)


# Use current_app.secret_key if available; fallback to a short default
@login_bp.record_once
def _on_register(state):
    try:
        current_app.secret_key  # just access to ensure it's available
    except Exception:
        # set a default secret on the blueprint module level (not ideal for prod)
        from flask import current_app as _ca
        try:
            _ca.secret_key = _ca.secret_key or "super_secret_key_change_this"
        except Exception:
            pass


@login_bp.route("/")
def home():
    return redirect(url_for("login.login"))


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        # Basic validation
        if not email or not password:
            flash("Please enter both University ID and password.")
            return redirect(url_for("login.login"))

        # Check that email ends with @brainwareuniversity.ac.in
        if not email.lower().endswith("@brainwareuniversity.ac.in"):
            flash("Please use your official Brainware University email ID.")
            return redirect(url_for("login.login"))

        # For now: accept ANY password as long as fields are filled
        username_part = email.split("@")[0]
        # store simple session flag so main app knows user is logged in
        try:
            session['user'] = username_part
        except Exception:
            # session may not be available in some contexts; ignore silently
            pass

        # After login, send student to the main homepage
        return redirect(url_for('home'))

    return render_template("login.html")


@login_bp.route("/dashboard")
def dashboard():
    user = request.args.get("user", "Student")
    return render_template("dashboard.html", user=user)


@login_bp.route('/logout')
def logout():
    """Clear login session and return to login page."""
    try:
        session.pop('user', None)
    except Exception:
        pass
    return redirect(url_for('login.login'))

