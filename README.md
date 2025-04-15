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
git clone https://github.com/BarioIsCoding/ableonion.git
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
/ableonion
│── templates/            # HTML templates
│   ├── home.html         # Homepage
│   ├── contact.html      # Contact form
│   ├── links.html        # Links page
│   ├── captcha.html      # Captcha system (before entering chat)
│   ├── rchat.html        # Random chat page (after captcha)
│   ├── captcha-help.html # Help page for captcha
│── feedback.txt          # Stores user-submitted messages
│── app.py                # Main Flask backend
│── README.md             # This documentation
```

## License
This project is for **educational purposes only**. Use at your own risk.

## Who made Ableonion?
*The text below does not act as official text, but rather based off of personal theory.*

Well, either it's the law enforcement, the FBI, or a super paranoid owner.
The website is, according to user feedback, up since 2013, which is very unusual for a Tor website. Additionally, the website supports hundreds to thousand simultaneous users, and has little downtimes, which indicates server strength. The website refers to themselves as a non-profit organisation for free speech, and labels the chat as self-moderating and has a few rules intact:
> We are a non-profit organization supporting freedom of speech without limits. However, any kind of spam, scam or commercial posts will not be tolerated.
If they don't significantly filter or ban these messages (although they kind of do), then that means... they log it. So, let's look what Ableonion does for the three roles.
### **Spam**
Ableonion does have mild moderations directed to spam:
1. Ghost messages - when sending the same message several times consecutively, only the 1st message is public; the following messages are hidden from the chat and the rest are not deleted, but **only displayed to the user who has sent them**, which can make the user *think* the message went through, while it has been blocked. 
2. Chat lockdown - Additionally, when a lot of different users spam the same thing, a notification comes up for everyone who sends a message to `All`, but not on private messages:
> [12:34] chat:
> Message sending failed. We are currently under attack.
* Time deals as placeholder and is made up. The message shows up as red and only to the user who has sent them even though it is displayed as a normal message rather than a private message.*
This happens automatically, and one time it has happened was on February 3rd, 2025, 12:56 (Ableonion time), when the chat was down for several minutes.
### **Scam**
There have been cases of scam on Ableonion, such as:
1. The cola spam - begging for donations; including accessing an "Ableonion VIP chat" when donating Bitcoin and giving out the Ableonion username.
> [18:23] Cola 
To entry the Ableonion vip chat pay 8 dollars to btc address: *hidden* pm your btc address and nickname
2. Human trafficking on Ableonion - vast majority or all **scams or honeypots**.
Ableonion, has done little to protect from these, besides putting one sentence on the Group Chat name prompt, which has now been removed:
`It's now **mandatory** to label any links posted.`
Other than that, there is no sufficient evidence of Ableonion acting against broken rules.
### **Commercial posts**
Commercial posts are **very frequent on Ableonion**, and the most relevant one is the [KageNoHitobito](https://www.fortinet.com/blog/threat-research/ransomware-roundup-keganohitobito-and-donex) ransomware, which has been found to have occured in several countries. The randomware required showing up to the public Ableonion chat and sending a private message to a user "Hitobito", which appears to be a group, not an individual.
There are a lot of different commercial posts on Ableonion, yet, **there is no evidence that Ableonion does something against commercial posts**.

The website has a clean GUI with very little updates and the CSS is always inline CSS, and minimal JS is used, particularly for reversing the message order and GUI in the public chat, whereas JS is not required to use. In fact, the description of the website is "Realtime chat. Accessible without JavaScript.". The website has not a single spelling error and very little bugs, but is still updated; just rare. The last significant update was on 2024-7. No log-in is required, and the website loads forever (works like a Websocket), which deliberately or not prevents the Tor circuit from updating.
