# Ableonion
Ableonion without the logging and captcha.
The Links page has also been adjusted for legal reasons.

Logging has been fully removed.
And yes, the original site *does* log all of your messages, even in the One-to-One chat, that's no secret.

![Ableonion](https://i.ibb.co/8DZDBDYx/Ableonion.png)

## Features
- **Homepage (`/`)** - Displays the Ableonion home page.
- **Contact Page (`/contact/`)** - Allows users to submit messages (saved in `feedback.txt`).
- **Links Page (`/links`)** - Displays useful links.
- **Random Chat Captcha (`/rchat`)** - Implements a time-based captcha system before entering the chat.
- **Help Page (`/captcha-help`)** - Displays information on captcha functionality.

## Installation
### 1. Clone this repository:
```sh
git clone https://github.com/yourrepo/ableonion-clone.git
cd ableonion-clone
```

### 2. Install dependencies:
```sh
pip install flask
```

### 3. Run the Flask application:
```sh
python app.py
```

### 4. Open the web application:
- Navigate to `http://127.0.0.1:5000/` in your browser.

## Project Structure
```
/ableonion-clone
│── templates/           # HTML templates
│   ├── home.html        # Homepage
│   ├── contact.html     # Contact form
│   ├── links.html       # Links page
│   ├── captcha.html     # Captcha system (before entering chat)
│   ├── rchat.html       # Random chat page (after captcha)
│   ├── captcha-help.html # Help page for captcha
│── feedback.txt         # Stores user-submitted messages
│── app.py               # Main Flask backend
│── README.md            # This documentation
```

## License
This project is for **educational purposes only**. Use at your own risk.


