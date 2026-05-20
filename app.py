import math
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='./templates')

SAFE_ENV = {
    'x': 0,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'exp': math.exp,
    'log': math.log,
    'sqrt': math.sqrt,
    'pi': math.pi,
    'e': math.e,
}

def safe_eval(expr, x_val):
    clean_expr = expr.replace('^', '**')
    SAFE_ENV['x'] = x_val
    try:
        return float(eval(clean_expr, {"__builtins__": None}, SAFE_ENV))
    except Exception:
        raise ValueError(f"Math Error: Could not evaluate your expression at x={x_val}.")

def secant_method(expr, x_a, x_b, tol=1e-6, max_iter=50):
    """
    Secant Method using requested structural layout parameters:
    Formula: x_c = x_b - (f(x_b) * (x_a - x_b)) / (f(x_a) - f(x_b))
    Error Formula: e = abs((x_c - x_b) / x_c)
    """
    steps = []
    
    try:
        f_xa = safe_eval(expr, x_a)
        f_xb = safe_eval(expr, x_b)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    for i in range(1, max_iter + 1):
        if abs(f_xa - f_xb) < 1e-15:
            return {
                "success": False, 
                "error": "Division by zero! The value of [f(x_a) - f(x_b)] approached zero."
            }
        
        # Computed using requested mathematical adjustments
        x_c = x_b - (f_xb * (x_a - x_b)) / (f_xa - f_xb)
        
        try:
            f_xc = safe_eval(expr, x_c)
        except ValueError as e:
            return {"success": False, "error": str(e)}
            
        # Error tracking using your exact configuration setup: x_new = x_c, x_old = x_b
        e_val = abs((x_c - x_b) / x_c) if x_c != 0 else 0
        
        steps.append({
            "iteration": i,
            "xa": round(x_a, 6),
            "xb": round(x_b, 6),
            "f_xa": round(f_xa, 6),
            "f_xb": round(f_xb, 6),
            "xc": round(x_c, 6),
            "f_xc": round(f_xc, 6),
            "error_val": round(e_val, 6),
            "error_pct": round(e_val * 100, 4)
        })
        
        # Terminate loop if criteria falls beneath specified target bounds
        if e_val <= tol:
            return {"success": True, "steps": steps, "root": round(x_c, 6)}
            
        # Cascade state mutations to advance iteration steps
        x_a, f_xa = x_b, f_xb
        x_b, f_xb = x_c, f_xc

    return {"success": True, "steps": steps, "root": round(x_b, 6)}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        expr = request.form.get('expr', '')
        try:
            x_a = float(request.form.get('x_a', 0))
            x_b = float(request.form.get('x_b', 1))
            tol = float(request.form.get('tol', 1e-6))
            max_iter = int(request.form.get('max_iter', 50))
            
            result = secant_method(expr, x_a, x_b, tol, max_iter)
            result['inputs'] = {'expr': expr, 'x_a': x_a, 'x_b': x_b, 'tol': tol, 'max_iter': max_iter}
        except ValueError:
            result = {"success": False, "error": "Invalid numerical parameters supplied."}
            result['inputs'] = {'expr': expr, 'x_a': 0, 'x_b': 1, 'tol': 1e-6, 'max_iter': 50}

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)