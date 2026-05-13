from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from threading import Lock

app = Flask(__name__)

# Статус одной кнопки (по умолчанию ВЫКЛ)
button_status = False
lock = Lock()

# HTML шаблон в темном рисованном стиле
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Knopka Control</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Quicksand:wght@400;600&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Quicksand', sans-serif;
            background: #1a1a2e;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Рисованный фон */
        body::before {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: 
                repeating-linear-gradient(90deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 2px, transparent 2px, transparent 8px),
                repeating-linear-gradient(0deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 2px, transparent 2px, transparent 8px);
            pointer-events: none;
        }
        
        /* Рисованные каракули */
        body::after {
            content: '~ ✦ ~ ✦ ~ ✦ ~ ✦ ~ ✦ ~ ✦ ~';
            position: absolute;
            bottom: 20px;
            left: 0;
            right: 0;
            text-align: center;
            color: rgba(255,255,255,0.1);
            font-size: 12px;
            font-family: monospace;
            pointer-events: none;
        }
        
        .container {
            background: #0f0f1a;
            border-radius: 48px;
            padding: 50px 40px;
            box-shadow: 
                0 20px 40px rgba(0,0,0,0.5),
                inset 0 1px 0 rgba(255,255,255,0.05);
            text-align: center;
            max-width: 500px;
            width: 90%;
            position: relative;
            border: 2px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }
        
        /* Рисованная рамка */
        .container::before {
            content: '';
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            border: 1px dashed rgba(255,255,255,0.15);
            border-radius: 40px;
            pointer-events: none;
        }
        
        h1 {
            font-family: 'Press Start 2P', monospace;
            font-size: 1.5em;
            color: #e0e0e0;
            margin-bottom: 10px;
            letter-spacing: 2px;
            text-shadow: 0 2px 5px rgba(0,0,0,0.5);
        }
        
        .subtitle {
            color: #888;
            font-size: 0.8em;
            margin-bottom: 30px;
            font-style: italic;
        }
        
        /* Рисованный индикатор */
        .indicator {
            width: 140px;
            height: 140px;
            margin: 30px auto;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            transition: all 0.3s ease;
        }
        
        .indicator-on {
            background: radial-gradient(circle at 30% 30%, #00ff88, #00aa55);
            box-shadow: 0 0 40px rgba(0,255,136,0.5), inset 0 -5px 0 rgba(0,0,0,0.2);
            animation: glitch 3s infinite;
        }
        
        .indicator-off {
            background: radial-gradient(circle at 30% 30%, #ff4444, #aa2222);
            box-shadow: 0 0 20px rgba(255,68,68,0.3), inset 0 -5px 0 rgba(0,0,0,0.2);
        }
        
        .indicator span {
            font-size: 3em;
            filter: drop-shadow(0 2px 5px rgba(0,0,0,0.5));
        }
        
        @keyframes glitch {
            0%, 100% { transform: scale(1); }
            95% { transform: scale(1); }
            96% { transform: scale(0.98); }
            97% { transform: scale(1.02); }
            98% { transform: scale(0.99); }
        }
        
        /* Рисованный статус */
        .status {
            font-size: 1.5em;
            padding: 15px;
            border-radius: 20px;
            margin: 20px 0;
            font-weight: bold;
            letter-spacing: 1px;
            position: relative;
            background: rgba(0,0,0,0.3);
        }
        
        .status-on {
            color: #00ff88;
            border-left: 4px solid #00ff88;
            border-right: 4px solid #00ff88;
            text-shadow: 0 0 10px rgba(0,255,136,0.5);
        }
        
        .status-off {
            color: #ff4444;
            border-left: 4px solid #ff4444;
            border-right: 4px solid #ff4444;
            text-shadow: 0 0 10px rgba(255,68,68,0.3);
        }
        
        /* Рисованные кнопки */
        .button-group {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        
        .btn {
            font-family: 'Press Start 2P', monospace;
            font-size: 0.9em;
            padding: 15px 25px;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: bold;
            letter-spacing: 1px;
            position: relative;
            background: #1a1a2e;
            color: #e0e0e0;
            border: 2px solid;
        }
        
        .btn-on {
            border-color: #00ff88;
            box-shadow: 0 0 15px rgba(0,255,136,0.3);
        }
        
        .btn-on:hover {
            background: #00ff88;
            color: #0f0f1a;
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(0,255,136,0.5);
        }
        
        .btn-off {
            border-color: #ff4444;
            box-shadow: 0 0 15px rgba(255,68,68,0.3);
        }
        
        .btn-off:hover {
            background: #ff4444;
            color: #0f0f1a;
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(255,68,68,0.5);
        }
        
        .btn-toggle {
            border-color: #ffaa44;
            box-shadow: 0 0 15px rgba(255,170,68,0.3);
        }
        
        .btn-toggle:hover {
            background: #ffaa44;
            color: #0f0f1a;
            transform: translateY(-3px);
        }
        
        .btn:active {
            transform: translateY(1px);
        }
        
        /* API секция в рисованном стиле */
        .api-info {
            margin-top: 30px;
            padding: 20px;
            background: rgba(0,0,0,0.4);
            border-radius: 20px;
            text-align: left;
            border: 1px dashed rgba(255,255,255,0.2);
            font-size: 0.85em;
        }
        
        .api-info h3 {
            color: #ffaa44;
            margin-bottom: 15px;
            font-family: 'Press Start 2P', monospace;
            font-size: 0.8em;
            text-align: center;
        }
        
        .api-endpoint {
            background: #0a0a0f;
            padding: 8px 12px;
            margin: 8px 0;
            border-radius: 10px;
            font-family: monospace;
            font-size: 0.8em;
            border-left: 3px solid #ffaa44;
        }
        
        .api-endpoint a {
            color: #00ff88;
            text-decoration: none;
        }
        
        .api-endpoint a:hover {
            text-decoration: underline;
            color: #ffaa44;
        }
        
        .method {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 5px;
            font-size: 0.7em;
            margin-right: 10px;
            font-weight: bold;
        }
        
        .method-get { background: #2196F3; color: white; }
        .method-post { background: #4CAF50; color: white; }
        
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            margin: 15px 0;
        }
        
        .url-bar {
            background: #0a0a0f;
            padding: 10px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 0.75em;
            color: #888;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .url-bar span {
            color: #00ff88;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ KNOPKA CTRL ⚡</h1>
        <div class="subtitle">~ рисованный контроллер ~</div>
        
        <div class="url-bar">
            📍 localhost:5000/knopka_<span>on/off</span>
        </div>
        
        <div class="indicator {% if status %}indicator-on{% else %}indicator-off{% endif %}">
            <span>{% if status %}🔘{% else %}⭕{% endif %}</span>
        </div>
        
        <div class="status {% if status %}status-on{% else %}status-off{% endif %}">
            {% if status %}
            ██▓▓░░ КНОПКА ВКЛ ░░░▓▓██
            {% else %}
            ██▓▓░░ КНОПКА ВЫКЛ ░░▓▓██
            {% endif %}
        </div>
        
        <div class="button-group">
            <button class="btn btn-on" onclick="turnOn()">🔘 ВКЛ</button>
            <button class="btn btn-off" onclick="turnOff()">⭕ ВЫКЛ</button>
            <button class="btn btn-toggle" onclick="toggle()">🔄 ИНВЕРТ</button>
        </div>
        
        <div class="api-info">
            <h3>🎯 УПРАВЛЕНИЕ ЧЕРЕЗ URL</h3>
            <div class="api-endpoint">
                <span class="method method-post">POST</span>
                <a href="/knopka_on" target="_blank">/knopka_on</a> → <span style="color:#00ff88">ВКЛЮЧИТЬ</span>
            </div>
            <div class="api-endpoint">
                <span class="method method-post">POST</span>
                <a href="/knopka_off" target="_blank">/knopka_off</a> → <span style="color:#ff4444">ВЫКЛЮЧИТЬ</span>
            </div>
            <div class="api-endpoint">
                <span class="method method-get">GET</span>
                <a href="/knopka_status" target="_blank">/knopka_status</a> → <span style="color:#ffaa44">ПРОВЕРИТЬ</span>
            </div>
            <div class="api-endpoint">
                <span class="method method-post">POST</span>
                <a href="/knopka_toggle" target="_blank">/knopka_toggle</a> → <span style="color:#ffaa44">ПЕРЕКЛЮЧИТЬ</span>
            </div>
            <hr>
            <div style="text-align: center; font-size: 0.7em; color: #666">
                💡 просто введите в адресной строке: /knopka_on
            </div>
        </div>
    </div>

    <script>
        async function turnOn() {
            try {
                const response = await fetch('/knopka_on', { method: 'POST' });
                if (response.ok) location.reload();
                else alert('Ошибка при включении');
            } catch (error) {
                alert('Ошибка сети: ' + error.message);
            }
        }

        async function turnOff() {
            try {
                const response = await fetch('/knopka_off', { method: 'POST' });
                if (response.ok) location.reload();
                else alert('Ошибка при выключении');
            } catch (error) {
                alert('Ошибка сети: ' + error.message);
            }
        }
        
        async function toggle() {
            try {
                const response = await fetch('/knopka_toggle', { method: 'POST' });
                if (response.ok) location.reload();
                else alert('Ошибка при переключении');
            } catch (error) {
                alert('Ошибка сети: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Главная страница"""
    with lock:
        return render_template_string(HTML_TEMPLATE, status=button_status)

@app.route('/knopka_status', methods=['GET'])
def get_status():
    """Получить статус кнопки"""
    with lock:
        return jsonify({
            'status': button_status,
            'message': 'ON' if button_status else 'OFF'
        })

@app.route('/knopka_on', methods=['GET', 'POST'])
def turn_on():
    """Включить кнопку - работает через GET и POST"""
    global button_status
    with lock:
        button_status = True
        # Если запрос из браузера (GET) - перенаправляем на главную
        if request.method == 'GET' and 'text/html' in request.headers.get('Accept', ''):
            return redirect(url_for('index'))
        return jsonify({
            'status': True,
            'message': 'Кнопка ВКЛЮЧЕНА'
        })

@app.route('/knopka_off', methods=['GET', 'POST'])
def turn_off():
    """Выключить кнопку - работает через GET и POST"""
    global button_status
    with lock:
        button_status = False
        # Если запрос из браузера (GET) - перенаправляем на главную
        if request.method == 'GET' and 'text/html' in request.headers.get('Accept', ''):
            return redirect(url_for('index'))
        return jsonify({
            'status': False,
            'message': 'Кнопка ВЫКЛЮЧЕНА'
        })

@app.route('/knopka_toggle', methods=['GET', 'POST'])
def toggle():
    """Инвертировать статус кнопки"""
    global button_status
    with lock:
        button_status = not button_status
        if request.method == 'GET' and 'text/html' in request.headers.get('Accept', ''):
            return redirect(url_for('index'))
        return jsonify({
            'status': button_status,
            'message': 'ON' if button_status else 'OFF'
        }) 

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🎨 KNOPKA CTRL - рисованный контроллер")
    print("="*50)
    print("📱 Веб-интерфейс: http://localhost:5000")
    print("\n🎯 УПРАВЛЕНИЕ ЧЕРЕЗ URL:")
    print("   http://localhost:5000/knopka_on  → ВКЛЮЧИТЬ")
    print("   http://localhost:5000/knopka_off → ВЫКЛЮЧИТЬ")
    print("   http://localhost:5000/knopka_status → ПРОВЕРИТЬ")
    print("="*50)
    print("\n🔥 Просто введите /knopka_on в адресной строке!")
    print("💡 Нажмите Ctrl+C для остановки\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)