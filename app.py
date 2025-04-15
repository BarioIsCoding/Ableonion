from flask import Flask, render_template, request, Response, redirect, url_for
from markupsafe import escape
import random
import datetime
import time
import string
import threading
import collections
import queue

app = Flask(__name__)
MAX_MESSAGE_LENGTH = 999  # Limit message length to 999 characters

# Data structures for chat functionality
active_chats = {}  # {client_id: {partner_id, messages, last_active}}
pending_users = {}  # {client_id: timestamp}
chat_messages = {}  # {client_id: [{time, sender, message}]}
recent_ips = collections.deque(maxlen=1000)  # Store recent IPs with timestamps
chat_locks = {}  # Locks for thread safety when modifying chat data
active_connections = {}  # Track active streaming connections

# Helper functions for chat functionality
def generate_client_id():
    """Generate a random client ID."""
    return ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=22))

def generate_random_gradient_css():
    """Generate a random CSS gradient similar to the examples."""
    angle = random.randint(0, 359)
    colors = []
    for _ in range(7):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = round(random.uniform(0.001, 0.999), 3)
        colors.append(f"rgba({r},{g},{b},{a})")
    gradient = f"linear-gradient({angle}deg, {', '.join(colors)})"
    return gradient

def get_utc_time():
    """Get the current UTC time in 24-hour format (HH:MM)."""
    now = datetime.datetime.utcnow()
    return now.strftime("%H:%M")

def count_unique_chatters():
    """Count unique IPs from the last hour."""
    one_hour_ago = time.time() - 3600
    unique_ips = set()
    for ip, timestamp in recent_ips:
        if timestamp >= one_hour_ago:
            unique_ips.add(ip)
    return len(unique_ips)

def find_chat_partner(client_id):
    """Find a chat partner for the client."""
    now = time.time()
    # Remove old pending users (waited > 5 minutes)
    for cid, timestamp in list(pending_users.items()):
        if now - timestamp > 300:
            pending_users.pop(cid, None)
    
    # Find an available partner
    if pending_users:
        partner_id = next(iter(pending_users))
        if partner_id != client_id:  # Don't match with self
            pending_users.pop(partner_id, None)
            # Create chat session for both users
            active_chats[client_id] = {'partner_id': partner_id, 'last_active': now}
            active_chats[partner_id] = {'partner_id': client_id, 'last_active': now}
            # Initialize message lists
            if client_id not in chat_messages:
                chat_messages[client_id] = []
            if partner_id not in chat_messages:
                chat_messages[partner_id] = []
            return True
    
    # No partner found, add to pending
    pending_users[client_id] = now
    return False

def add_message(client_id, message, is_from_partner=False):
    """Add a message to the chat history."""
    if client_id not in chat_messages:
        chat_messages[client_id] = []
    
    time_str = get_utc_time()
    if is_from_partner:
        chat_messages[client_id].append({
            'time': time_str,
            'sender': 'Random',
            'message': message,
            'is_system': False
        })
    else:
        chat_messages[client_id].append({
            'time': time_str,
            'sender': 'You',
            'message': message,
            'is_system': False
        })
        
        # Forward message to partner
        if client_id in active_chats and 'partner_id' in active_chats[client_id]:
            partner_id = active_chats[client_id]['partner_id']
            if partner_id in chat_messages:
                chat_messages[partner_id].append({
                    'time': time_str,
                    'sender': 'Random',
                    'message': message,
                    'is_system': False
                })

def add_system_message(client_id, message):
    """Add a system message to the chat history."""
    if client_id not in chat_messages:
        chat_messages[client_id] = []
    
    chat_messages[client_id].append({
        'time': get_utc_time(),
        'message': message,
        'is_system': True
    })

def get_searching_message(elapsed_seconds):
    """Get the searching message with appropriate number of dots."""
    dots = '.' * (1 + (elapsed_seconds // 3) % 3)
    return f"Searching for a random{dots} {count_unique_chatters()} chatters in the last hour."

def check_partner_left(client_id):
    """Check if partner has left the chat."""
    if client_id in active_chats and 'partner_id' in active_chats[client_id]:
        partner_id = active_chats[client_id]['partner_id']
        if partner_id not in active_chats or active_chats[partner_id].get('partner_id') != client_id:
            # Partner left
            active_chats.pop(client_id, None)
            add_system_message(client_id, "The random left.")
            return True
    return False

def initialize_chat_session(client_id, message, start_time):
    """Initialize or update chat session state."""
    # Record IP for unique chatter count
    client_ip = request.remote_addr
    recent_ips.append((client_ip, time.time()))
    
    # Generate or use existing client ID
    if not client_id or client_id not in active_chats and client_id not in pending_users:
        client_id = generate_client_id()
        # Initialize lock for this client
        chat_locks[client_id] = threading.Lock()
        
        # Generate start time for searching animation
        start_time = get_utc_time()
        
        # Clear any old messages
        if client_id in chat_messages:
            chat_messages[client_id] = []
            
        # Add initial system message
        add_system_message(client_id, get_searching_message(0))
        
        # Start looking for a partner
        has_partner = find_chat_partner(client_id)
        if has_partner:
            add_system_message(client_id, "A random was found, say hi!")
    
    # Process message if provided
    if message and len(message) <= MAX_MESSAGE_LENGTH:
        with chat_locks.get(client_id, threading.Lock()):
            # Check if partner left before processing message
            check_partner_left(client_id)
            
            # Add message to chat
            add_message(client_id, escape(message))
            
            # Update last active time
            if client_id in active_chats:
                active_chats[client_id]['last_active'] = time.time()
    
    # Check if we have a partner or still searching
    has_partner = client_id in active_chats and 'partner_id' in active_chats[client_id]
    
    # If we were searching but now have a partner, add the "found" message
    if has_partner and client_id in chat_messages:
        found_message = False
        for msg in chat_messages[client_id]:
            if msg.get('is_system') and "random was found" in msg.get('message', ''):
                found_message = True
                break
        
        if not found_message:
            add_system_message(client_id, "A random was found, say hi!")
    
    # Check if partner left
    if has_partner:
        check_partner_left(client_id)
        has_partner = client_id in active_chats  # Update has_partner status
    
    # Register connection for updates
    active_connections[client_id] = {'timestamp': time.time(), 'queue': queue.Queue()}
    
    return client_id, start_time, has_partner

def get_message_html(client_id):
    """Generate HTML for chat messages."""
    messages_html = ""
    if client_id in chat_messages:
        for msg in chat_messages[client_id]:
            if msg.get('is_system', False):
                messages_html += f"<p><i>{msg['message']}</i></p>\n"
            else:
                time_str = msg['time']
                if msg['sender'] == 'You':
                    messages_html += f"<p><u>{time_str} - </u><s>{msg['sender']}:</s> {msg['message']}</p>\n"
                else:
                    messages_html += f"<p><u>{time_str} - </u><b>{msg['sender']}:</b> {msg['message']}</p>\n"
    return messages_html

def update_search_message(client_id, start_time):
    """Update the searching message with correct dots based on elapsed time."""
    if client_id in pending_users and client_id in chat_messages:
        # Calculate elapsed time
        now = datetime.datetime.utcnow()
        try:
            start_datetime = datetime.datetime.strptime(start_time, "%H:%M")
            start_datetime = start_datetime.replace(year=now.year, month=now.month, day=now.day)
            if start_datetime > now:  # Handle day rollover
                start_datetime = start_datetime - datetime.timedelta(days=1)
            elapsed_seconds = (now - start_datetime).total_seconds()
        except ValueError:
            elapsed_seconds = 0
        
        # Update search message with dots
        for i, msg in enumerate(chat_messages[client_id]):
            if msg.get('is_system') and "Searching for a random" in msg.get('message', ''):
                chat_messages[client_id][i]['message'] = get_searching_message(int(elapsed_seconds))
                return True
    return False

def stream_chat_content(client_id, start_time):
    """Stream chat content in chunks with deliberate loading delays."""
    # Get gradient for this session
    gradient = generate_random_gradient_css()
    
    # Yield initial HTML doctype and head opening - this allows the browser to start parsing
    yield '<!DOCTYPE html>\n'
    yield '<html lang="en">\n'
    yield '<head>\n'
    time.sleep(0.2)  # Small delay to create visible loading effect
    
    # Yield meta tags
    yield '''    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="referrer" content="no-referrer">
    <title>Random Chat</title>
    <link rel="icon" href="data:,">
    <base target="_blank">
'''
    time.sleep(0.3)  # Delay between head elements
    
    # Yield CSS styles
    yield f'''    <style>
        html {{
            background: {gradient};
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: sans-serif;
        }}
        body {{
            width: calc(100% - 10mm);
            height: calc(100% - 10mm);
            margin: 5mm;
            position: relative;
        }}
        h1 {{
            position: absolute;
            margin: 0;
            z-index: -1;
            color: #fff;
            font-family: fantasy;
            text-shadow: -2px 2px 4px #000;
        }}
        h1 + h1 {{
            right: 0;
            text-shadow: 2px 2px 4px #000;
        }}
        nav {{
            display: table;
            margin: auto;
        }}
        nav a {{
            display: table-cell;
            vertical-align: middle;
            text-decoration: none;
            background: #e55;
            color: #fff;
            height: 10mm;
            border: 1px outset #d44;
            padding: 0 4mm;
            text-shadow: 0 0 6px #000;
            box-shadow: 0 2px 8px #000;
        }}
        nav a:hover {{
            background: #d33;
        }}
        main {{
            position: absolute;
            top: 15mm;
            width: 100%;
            height: calc(100% - 15mm);
            background: rgba(255,255,255,.5);
            border: 1px solid #ddd;
            box-sizing: border-box;
        }}
        div {{
            width: 100%;
            max-height: calc(100% - 10mm);
            overflow: auto;
        }}
        section {{
            display: flex;
            flex-direction: column-reverse;
        }}
        p {{
            margin: 0;
            padding: 5px 10px;
        }}
        p:nth-child(2n) {{
            background: rgba(207,207,207,.5);
        }}
        u {{
            text-decoration: none;
            font-size: 75%;
        }}
        s {{
            text-decoration: none;
            font-weight: bold;
            color: #e66;
        }}
        b {{
            color: #26a;
        }}
        iframe {{
            display: block;
            width: 100%;
            height: 10mm;
            border: 1px solid #666;
            box-sizing: border-box;
        }}
    </style>
'''
    yield '</head>\n'
    time.sleep(0.5)  # Longer delay after CSS
    
    # Yield body start and header
    yield '<body>\n'
    yield '    <h1>Random</h1>\n'
    yield '    <h1>Chat</h1>\n'
    time.sleep(0.2)
    
    # Yield navigation
    yield '''    <nav>
        <a href="/rchat" target="_self">Find a new random</a>
        <a href="help">Help</a>
    </nav>
'''
    time.sleep(0.3)
    
    # Yield main container opening
    yield '    <main>\n'
    time.sleep(0.2)
    
    # Yield iframe with form
    yield f'''        <iframe srcdoc='<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="referrer" content="no-referrer">
            <title>t</title>
            <link rel="icon" href="data:,">
            <style>
                html {{ overflow: hidden; margin: 0; font-family: sans-serif; }}
                body {{ margin: 0; }}
                form {{ display: flex; }}
                input {{ outline: none; border: 0; }}
                input[name=m] {{ flex: 1; font-size: 8mm; height: 10mm; }}
                input:hover, input:focus {{ background: #ded; }}
                input[type=submit] {{ font-size: 9mm; height: 11mm; border: 0; padding: 0; margin-top: -3px; background: #782; text-shadow: 2px 2px 4px #000; cursor: pointer; }}
                input[type=submit]:hover {{ background: #9a4; }}
            </style>
        </head>
        <body>
            <form action=".">
                <input name="m" autofocus autocomplete="off" tabindex="1">
                <input type="submit" value="💬">
                <input type="hidden" name="h" value="{client_id}">
                <input type="hidden" name="t" value="{start_time}">
            </form>
        </body>
        </html>'>
        </iframe>
'''
    time.sleep(0.5)
    
    # Yield div and initial script
    yield '''        <div>
            <script>
                d = document.querySelector("div");
                document.querySelector("iframe").onload = function() {
                    d.scrollTo(0, d.scrollHeight);
                    this.contentDocument.querySelector("input").focus();
                }
            </script>
'''
    time.sleep(0.3)
    
    # Yield section with messages
    yield '            <section>\n'
    messages_html = get_message_html(client_id)
    # Yield messages in chunks
    for i in range(0, len(messages_html), 500):
        yield messages_html[i:i+500]
        time.sleep(0.2)
    
    yield '            </section>\n'
    yield '        </div>\n'
    yield '    </main>\n'
    time.sleep(0.3)
    
    # Now continue with an infinite stream of updates
    update_counter = 0
    search_check_counter = 0
    
    # Keep connection alive indefinitely
    while True:
        update_counter += 1
        search_check_counter += 1
        
        # Check if partner left
        if client_id in active_chats:
            with chat_locks.get(client_id, threading.Lock()):
                check_partner_left(client_id)
        
        # Update search animation if still searching (every 3 seconds)
        if search_check_counter >= 3:
            search_check_counter = 0
            if client_id in pending_users:
                # Update search message
                if update_search_message(client_id, start_time):
                    # If message was updated, send a script to update it in the DOM
                    new_message = get_searching_message(int(time.time() - pending_users[client_id]))
                    yield f'''
            <script>
                var messages = document.querySelectorAll("section p i");
                for (var i = 0; i < messages.length; i++) {{
                    if (messages[i].textContent.includes("Searching for a random")) {{
                        messages[i].textContent = "{new_message}";
                        break;
                    }}
                }}
            </script>
'''
        
        # Send a comment to keep the connection alive
        yield f"<!-- keepalive: {update_counter} -->\n"
        
        # Check for any queued updates (messages from partner, etc.)
        if client_id in active_connections and 'queue' in active_connections[client_id]:
            try:
                # Non-blocking queue check
                update = active_connections[client_id]['queue'].get_nowait()
                yield update
            except queue.Empty:
                pass
        
        # Slow down the loop to avoid excessive CPU usage
        time.sleep(1)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/links')
def links():
    return render_template('links.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if len(message) <= MAX_MESSAGE_LENGTH:
            with open('feedback.txt', 'a', encoding='utf-8') as f:
                f.write(f'Message: {escape(message)}\n---\n')
        return render_template('thank_you.html')
    return render_template('contact.html')

@app.route('/rchat')
def rchat():
    # Get parameters
    client_id = request.args.get('h', '')
    message = request.args.get('m', '')
    start_time = request.args.get('t', '')
    
    # Initialize or update chat session
    client_id, start_time, has_partner = initialize_chat_session(client_id, message, start_time)
    
    # Create response that streams updates in chunks with progressive loading
    return Response(
        stream_chat_content(client_id, start_time),
        mimetype='text/html',
        headers={
            # Disable caching to ensure fresh content
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            # Enable chunked transfer encoding
            'Transfer-Encoding': 'chunked'
        }
    )

# Cleanup function to remove inactive chats
def cleanup_inactive_chats():
    """Remove inactive chats (no activity for 10 minutes)."""
    now = time.time()
    for client_id in list(active_chats.keys()):
        if now - active_chats[client_id].get('last_active', 0) > 600:  # 10 minutes
            partner_id = active_chats[client_id].get('partner_id')
            if partner_id and partner_id in active_chats:
                add_system_message(partner_id, "The random left.")
                active_chats.pop(partner_id, None)
            active_chats.pop(client_id, None)
    
    # Also clean up old connections
    for client_id in list(active_connections.keys()):
        if now - active_connections[client_id].get('timestamp', 0) > 1800:  # 30 minutes
            active_connections.pop(client_id, None)

# Run cleanup function periodically
def run_cleanup():
    while True:
        time.sleep(60)  # Run every minute
        cleanup_inactive_chats()

if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()
    
    # Run the Flask app
    # Note: Using threaded=True is essential for streaming responses
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
