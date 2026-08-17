"""FFMitra FAQ corpus for the RAG chatbot.

Each entry: {category, question, answer, keywords}.
Category strings are the exact three used across the platform.
Answers are written in clear, friendly English (Hinglish-tolerant),
short lines/bullets, with empathetic, non-judgmental tone.
"""

CATEGORY_PAYMENT = "Payment / Transaction Fraud"
CATEGORY_PHISHING = "Phishing & Social Engineering"
CATEGORY_INVESTMENT = "Investment & Misleading Payments"

FAQ_CORPUS: list[dict] = [
    # ------------------------------------------------------------------
    # Category 1: Payment / Transaction Fraud
    # ------------------------------------------------------------------
    {
        "category": CATEGORY_PAYMENT,
        "question": "I sent money in a UPI scam. What should I do right now?",
        "answer": (
            "First, don't panic — acting fast helps. Follow the 10-minute rule: "
            "call your bank immediately and ask them to block/freeze the transaction, "
            "and dial the cybercrime helpline 1930 within 10 minutes of the loss. "
            "- Note the exact time, amount, UPI reference (UTR/transaction ID), and the "
            "UPI ID / phone number / account you sent money to. "
            "- Take screenshots of the payment confirmation and any chat/messages with the scammer. "
            "- After calling 1930, file a complaint on cybercrime.gov.in (NCRP portal) with all "
            "details and evidence. "
            "The sooner you report, the better the chance that the receiving account is frozen "
            "before the money is moved out."
        ),
        "keywords": (
            "upi scam, upi fraud, sent money, transferred, gpay, google pay, phonepe, paytm, "
            "lost money, money stolen, payment, transaction, urgent, 10 minute rule, recover"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "How do I report cyber fraud on the 1930 helpline?",
        "answer": (
            "Dial 1930 from any phone — it's the national cybercrime helpline, available 24x7, "
            "and it works across India. Explain calmly that you lost money to online fraud, and "
            "tell them the amount, the bank, and when it happened. "
            "- Have your bank account details and the UPI/txn reference number ready. "
            "- The operator will log an urgent complaint and pass it to your bank and police. "
            "- You will get a complaint reference number — write it down, you need it later. "
            "If your money was sent within the last few hours, call before doing anything else; "
            "every minute matters for freezing the receiving account."
        ),
        "keywords": (
            "1930, helpline, cybercrime helpline, report call, call 1930, toll free, "
            "complain, register complaint, how to report, who to call"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "How do I file a complaint on the NCRP portal (cybercrime.gov.in)?",
        "answer": (
            "Go to cybercrime.gov.in (the National Cyber Crime Reporting Portal, NCRP) and click "
            "'Report Cybercrime'. "
            "- Click 'File a Complaint' and select the right type — for money loss choose "
            "'Financial Fraud' or 'Online Financial Fraud' as it appears. "
            "- Fill in your details and describe the incident: date, time, amount, payment app, "
            "and the bank/UPI IDs involved. "
            "- Attach evidence: screenshots, transaction receipts, call/SMS records. "
            "- Submit and save the acknowledgement/reference number you receive. "
            "The complaint is routed to the state cybercrime cell and your bank automatically "
            "(through the Citizen Financial Cyber Fraud Reporting and Management System)."
        ),
        "keywords": (
            "ncpr, ncrp, cybercrime.gov.in, national cyber crime reporting portal, "
            "file complaint online, report cybercrime website, portal steps, online complaint"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "What evidence should I collect and keep after a fraud?",
        "answer": (
            "Evidence is what makes your complaint strong and helps freeze funds. Collect: "
            "- Transaction references: UTR number, UPI/transaction ID, bank statement showing the debit. "
            "- Screenshots of payment confirmations and of the scammer's messages/chat/phone number. "
            "- Call recordings or a log of calls (date, time, number) if someone called you. "
            "- SMS and emails from the scammer — do not delete anything. "
            "- The scammer's account details: UPI ID, bank account number/IFSC, wallet ID, website or "
            "app name. "
            "Keep everything in a folder (and a backup) — you will need it for 1930, the NCRP "
            "complaint, and the police FIR."
        ),
        "keywords": (
            "evidence, checklist, what to collect, utr number, transaction id, screenshots, "
            "call recording, sms, bank statement, save proof, documents, proof of payment"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "Will I get my money back after a UPI fraud?",
        "answer": (
            "Be honest with yourself: recovery is not guaranteed, but reporting quickly gives a "
            "real chance. Banks are expected to credit back eligible fraudulent amounts within "
            "90 days of the complaint when the receiving bank confirms the money went to a "
            "fraud account. "
            "- If you reported within 10 minutes (1930 + bank), freezing chances are highest. "
            "- Follow up: banks must close refund requests within 90 days; if they don't, escalate "
            "to the RBI Banking Ombudsman. "
            "- If the refund is rejected, you still have a police case reference that can help in "
            "legal recovery. "
            "I can't promise your money will come back, but every report filed properly improves "
            "the odds and helps catch the fraudsters."
        ),
        "keywords": (
            "get money back, refund, chargeback, will i recover, money return, refund process, "
            "90 days, rbi ombudsman, compensation, refund reality, refund possible"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "Can the scammer be traced and caught?",
        "answer": (
            "Yes — fraud leaves a digital trail. Every UPI/bank transfer goes through accounts, "
            "SIM cards, devices and IP addresses, and cybercrime investigators follow that trail "
            "through account holder records, KYC data and telecom records. "
            "Many scams use mule accounts (accounts of innocent people who unknowingly lent their "
            "bank details), so tracing can take time and multiple accounts. "
            "That's why your complaint with exact transaction references is important — it is the "
            "starting point of the trace. "
            "You may not hear an update for weeks, but registered cases do lead to arrests and "
            "recoveries. Keep your complaint reference number safe."
        ),
        "keywords": (
            "trace scammer, catch scammer, track fraudster, digital trail, investigation, "
            "police case, will they be caught, arrest, find the scammer, ip address"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "Someone asked for my OTP to 'reverse' a wrong transfer. Should I share it?",
        "answer": (
            "Never share your OTP with anyone — no bank, no app, no 'executive', no police "
            "officer will ever ask for it. An OTP is the key to your money, and anyone who has "
            "your OTP can empty your account in seconds. "
            "- Real banks never ask for OTP, PIN, CVV or card details over call/SMS. "
            "- If someone claims they sent money by mistake and needs an OTP to 'return' it, it's "
            "a scam — tell them to use the official reverse transfer feature in the bank app. "
            "- If you already shared an OTP and money left your account, report to 1930 and your "
            "bank immediately. "
            "The moment you suspect you've been tricked, report first, then block the number."
        ),
        "keywords": (
            "otp, share otp, otp share, one time password, otp scam, otp fraud, wrong transfer, "
            "reverse transfer, refund otp, never share otp"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "I scanned a QR code and money got deducted. What happened?",
        "answer": (
            "Scanning a QR code is like signing a cheque — when you scan a scammer's QR and "
            "enter your PIN, you have approved a payment TO them. Unlike sending money to a "
            "number, a QR scan doesn't always show you the exact payee clearly, which is exactly "
            "what scammers exploit. "
            "If money was deducted after a QR scan: call your bank and 1930 immediately, note the "
            "time/amount, and save the payment confirmation. "
            "Remember the golden rule: a QR code is only for receiving money — if someone tells "
            "you 'scan this to receive a payment', it is a scam."
        ),
        "keywords": (
            "qr code, qr scam, scan qr, qr fraud, qr payment, scanned qr, qr card, qr photo, "
            "cashback qr, receive money qr"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "Someone promised to double my money (money doubling scheme). Is it real?",
        "answer": (
            "No — no one can legally double your money, and anyone who promises that is running "
            "a fraud. Money-doubling scams ask you to 'invest' and transfer money to random "
            "accounts; you may see a fake profit number on a fake app to tempt you to invest more, "
            "and then the account disappears. "
            "These are rarely covered by banks or regulators, so recovery is very hard. "
            "If you've already paid: stop all further payments immediately, report to 1930 and "
            "cybercrime.gov.in, and save every chat and transaction record. "
            "If you were about to pay: don't. Real investments grow slowly and never double in "
            "hours."
        ),
        "keywords": (
            "money doubling, double money, get rich quick, guaranteed returns, invest double, "
            "double scheme, quick profit, investment scheme, savings scheme scam"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "My credit/debit card was used fraudulently. What should I do?",
        "answer": (
            "- Immediately call your card issuer's 24x7 helpline and get the card blocked "
            "(permanently, not just 'on hold'). "
            "- Dispute the fraudulent charges in writing (email/app) and note the complaint "
            "number. "
            "- Report to 1930 and file a complaint on cybercrime.gov.in with the transaction "
            "details. "
            "- Check your card statement for other small test charges and ask the bank to reissue "
            "a fresh card. "
            "If your card details were stolen from a skimmer or a phishing site, also change the "
            "passwords of the email and phone accounts linked to it."
        ),
        "keywords": (
            "credit card, debit card, card fraud, card used, unauthorized charge, card blocked, "
            "skimming, card scam, card details stolen, international transaction, dispute"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "What is ATM skimming and how do I protect myself?",
        "answer": (
            "Skimming is when criminals fit a fake card reader (and a hidden camera) over an ATM's "
            "slot to copy your card's magnetic strip and capture your PIN. They then clone your "
            "card and withdraw cash. "
            "Before inserting your card: wiggle the card slot and check the keypad for overlays; "
            "cover the keypad with your hand while typing your PIN; and check the machine for "
            "loose parts or odd cameras. "
            "Prefer cardless cash and contactless payments where possible. "
            "If you see a suspicious charge on your statement, block the card and report to your "
            "bank and 1930."
        ),
        "keywords": (
            "atm, skimming, atm card, atm fraud, card reader, cloned card, cash withdrawn, "
            "atm machine, pin capture, atm scam"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "I paid to the wrong UPI ID / wrong person. Can I get it back?",
        "answer": (
            "First check the difference between paying to a wallet and to a bank account: "
            "- Paying a wallet UPI ID (e.g., @paytm, @ybl with a wallet link) sends money into a "
            "wallet balance; if it's another person's wallet, they can simply withdraw it. "
            "- Paying to a bank-linked UPI ID can sometimes be reversed if the recipient "
            "co-operates. "
            "If it was a genuine mistake, contact the recipient once and keep proof of that "
            "message; if they refuse, approach your bank (they can contact the receiving bank as "
            "a 'chargeback/transaction reversal' request) and file a complaint. "
            "If you were tricked into paying the wrong ID (fake payment link, impersonation), "
            "treat it as fraud — call 1930 and your bank immediately."
        ),
        "keywords": (
            "wrong upi id, wrong person, wrong transfer, wrong payee, paid wrong account, "
            "wallet upi, @paytm, @ybl, payment mistake, mistaken payment, reverse"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "What is a mule account? Someone wants to 'borrow' my account. Should I say yes?",
        "answer": (
            "A mule account is a bank account used by criminals to receive and move stolen money — "
            "and it's often an innocent person's account, borrowed or sold for a small fee. "
            "If someone offers you money to 'receive a transfer' and forward it, or asks to use "
            "your account/UPI for their 'business', they are making you a mule. "
            "This is illegal: your account gets flagged, frozen, and linked to the original "
            "victim's complaint — you can face police questioning and legal trouble, and banks can "
            "blacklist you. "
            "Never share your account number, UPI PIN, debit card, or sign up apps in someone "
            "else's name. If you already allowed someone to use your account, contact your bank "
            "and explain the situation immediately."
        ),
        "keywords": (
            "mule account, lend account, borrow account, use my account, receive money for "
            "someone, money mule, account freeze risk, forward money, kyc share, sell account"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "I got a call saying I will get a cashback/refund and need to pay a small fee first.",
        "answer": (
            "That's a classic refund scam: nobody charges a 'processing fee' to give you a "
            "refund or cashback. The scammer's goal is to make you pay first and then vanish "
            "with the money. "
            "Genuine refunds from companies go back to the original payment method automatically, "
            "with no extra step and no OTP/PIN requirement. "
            "If you've already paid: report to 1930 and cybercrime.gov.in, keep the chat and "
            "transaction proof, and inform your bank. "
            "If you haven't paid: stop the conversation, block the number, and don't click any "
            "'refund' links sent in SMS or WhatsApp."
        ),
        "keywords": (
            "cashback scam, refund scam, cashback call, fake refund, processing fee, "
            "refund first, pay fee get money, reward scam, lucky draw cashback"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "My bank account is frozen because of a fraud complaint. What should I do?",
        "answer": (
            "A freeze usually happens when a fraud complaint names your account (or a mule "
            "account linked to it). It is not a punishment by itself — banks freeze accounts to "
            "protect funds during investigation. "
            "- Contact your branch and ask in writing why the account is frozen and which agency "
            "directed it (police, cyber cell, bank's fraud department). "
            "- Share your side of the story with evidence, especially if you were also a victim "
            "of the fraud. "
            "If you lent your account knowingly, be transparent — hiding it makes things worse. "
            "If the freeze is from a cybercrime complaint you yourself filed, it is usually "
            "temporary and is lifted after the investigation checks the disputed transaction."
        ),
        "keywords": (
            "account frozen, freeze account, account blocked, cyber cell freeze, bank freeze, "
            "unfreeze, account under investigation, can't use account, fraud hold"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "I paid for something online and the seller vanished / goods never arrived. Is it fraud?",
        "answer": (
            "Yes, paying for goods/services that never arrive from a fake or disappearing seller "
            "is an online fraud (advance-fee / e-commerce fraud). This also covers sellers who "
            "ask you to pay 'outside the app' to avoid platform charges. "
            "Report on cybercrime.gov.in with the seller's number, payment receipt, and chat "
            "history, and call 1930 if the amount is significant. "
            "Also complain to the platform (Amazon, Flipkart, etc.) through their official "
            "seller-reporting process. "
            "For small amounts, the platform often refunds once you show proof of the scam — "
            "do that first, and file the NCRP complaint as your record."
        ),
        "keywords": (
            "online shopping fraud, seller disappeared, goods not delivered, advance payment, "
            "e-commerce scam, paid no delivery, fake website, shop online scam, fake seller"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "Is sharing my UPI PIN with my bank on a call ever required?",
        "answer": (
            "Never. Your UPI PIN is the final password for every payment, and no bank, app, or "
            "regulator will ever ask for it — not on a call, chat, or email. Same goes for card "
            "CVV, expiry, OTP, and online banking passwords. "
            "Anyone asking for these is a fraudster, and giving them out is like handing over "
            "your account key. "
            "If you shared your PIN or OTP by mistake, immediately change your UPI PIN in the "
            "app, block the card if relevant, and report to 1930 and your bank. "
            "Keep this as a family rule too — scammers specifically target elders with fake "
            "'bank verification' calls."
        ),
        "keywords": (
            "upi pin, share pin, pin safe, bank verification call, verify account, upi pin "
            "change, keep pin secret, password share, security rule"
        ),
    },

    # ------------------------------------------------------------------
    # Category 2: Phishing & Social Engineering
    # ------------------------------------------------------------------
    {
        "category": CATEGORY_PHISHING,
        "question": "Someone called saying I am under 'digital arrest'. Is this real?",
        "answer": (
            "This is a scam, full stop. 'Digital arrest' is not a legal concept in India — "
            "police/CBI/ED officers never call you, put you on video call, and ask you to stay "
            "online 'under house arrest' until you pay money. They arrest in person, with "
            "documents, at your address. "
            "Typical script: 'Your Aadhaar was used for money laundering / a parcel with drugs "
            "was found in your name — you are under digital arrest, connect with us on a video "
            "call, keep your camera on, don't tell anyone, and transfer funds to a 'security "
            "account' to prove innocence.' "
            "What to do: stay calm, tell them you're disconnecting and calling the police "
            "yourself, and immediately report the number to 1930 and cybercrime.gov.in. "
            "Never keep the call going, never share your screen, and never transfer 'verification' "
            "money. If someone in your family is on such a call right now, tell them to hang up "
            "and call you immediately."
        ),
        "keywords": (
            "digital arrest, digital arrest scam, arrest, police call, cbi, ed, enforcement "
            "directorate, money laundering, courier parcel, drugs parcel, video call arrest, "
            "security account, skype call"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "I got a call from 'customer care' asking to fix an issue in my bank/app account.",
        "answer": (
            "Banks and apps never call customers to 'fix' accounts. Fake customer care calls "
            "usually say: 'your KYC is expiring / your account is at risk / we will help you "
            "enable high-value payments' — and then guide you through steps that actually "
            "transfer money from your account, or ask for OTP/PIN. "
            "If you need support, always call the official number printed on your bank card or "
            "on the official app/website — never a number found on Google search ads or "
            "WhatsApp. "
            "If you already followed such instructions and lost money: call your bank and 1930 "
            "now, and save the number and time of the call. "
            "Remember: legitimate support can wait; an urgent scammer cannot."
        ),
        "keywords": (
            "fake customer care, customer care scam, support call, bank call, app support, "
            "fix account, update issue, fake helpline, google number scam, technical support"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "What is vishing? I got a scary call from 'Income Tax'/'Electricity Board'.",
        "answer": (
            "Vishing = voice phishing: fraudsters call impersonating authority figures (Income "
            "Tax, electricity board, TRAI, gas company, police) and create panic — 'your "
            "electricity will be cut in 30 minutes', 'you have tax arrears and will be jailed' — "
            "and then demand an 'urgent payment'. "
            "Official bodies do not take payments over the phone, and they do not threaten "
            "disconnection while on a call. "
            "Stay calm, note the caller's number, and verify independently by calling the "
            "official helpline or checking your actual bill online. "
            "Report the number to 1930 and cybercrime.gov.in, and warn elderly family members — "
            "they are the main target of these calls."
        ),
        "keywords": (
            "vishing, voice phishing, fake call, income tax call, electricity cut, trai call, "
            "gas bill call, government impersonation, authority call, threatening call"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "I got an SMS with a link saying my parcel/shipment is blocked or my KYC is due.",
        "answer": (
            "This is SMS phishing (smishing). Official alerts from banks or couriers never ask "
            "you to click a random short link and 'verify within 5 minutes'. The link leads to a "
            "fake page that looks real and steals your card details, login, or OTP. "
            "Do not click the link — instead open the official app/website yourself (courier "
            "tracking, bank app) and check there. "
            "Also learn the SMS header trick: official bank messages come from registered "
            "headers (like 'AD-BANKNAME'), while scam SMS often arrive from normal mobile "
            "numbers. "
            "If you already clicked and entered details, change your passwords, block your card, "
            "and report to 1930 immediately."
        ),
        "keywords": (
            "fake sms, sms scam, link scam, smishing, parcel blocked, courier sms, kyc link, "
            "verify link, sms header, ad-bank, bank alert sms, don't click link"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "Someone on WhatsApp is impersonating my relative/friend asking for money.",
        "answer": (
            "Scammers hack or copy WhatsApp profiles — same photo, same name — and message "
            "'I lost my phone / this is my new number / emergency, need money now'. They may "
            "also send a voice note created to sound like your relative. "
            "Never send money based on a chat. Call your relative on their original known "
            "number and verify — if they're 'unreachable', call another family member. "
            "Ask a personal question only they would know, or demand a live video call. "
            "If money was sent, call your bank + 1930 immediately and report the WhatsApp "
            "profile to WhatsApp (long-press > Report). "
            "Tell your family to enable two-step verification on WhatsApp so their own profile "
            "can't be hijacked."
        ),
        "keywords": (
            "whatsapp impersonation, fake whatsapp, relative in trouble, friend asking money, "
            "hacked whatsapp, new number scam, emergency money, verify identity, family scam"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "I got a message that my KYC is blocked and my account will stop working.",
        "answer": (
            "KYC-block messages are one of the most common scams. The real KYC (Know Your "
            "Customer) update is always done inside your official bank/broker/mobile wallet app — "
            "never through a link in an SMS or email, and never by a caller taking 'remote "
            "access' of your phone. "
            "If the message has a link, don't click it. Open your official app, check "
            "'KYC status', and call the official helpline if anything looks off. "
            "If you already clicked the link and entered your details, change passwords, block "
            "your card, and report to 1930 — the scammer can use your KYC details to open "
            "accounts or take loans in your name."
        ),
        "keywords": (
            "kyc, kyc update, kyc blocked, kyc scam, pan card scam, aadhaar update, bank kyc, "
            "sim kyc, verify kyc, kyc link"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "I received an email from 'my bank' asking me to update details urgently.",
        "answer": (
            "That is email phishing. Look for red flags: a strange sender address "
            "(@bank-update.com instead of the real bank domain), urgency ('24 hours or account "
            "closed'), generic greeting, and a login link. "
            "Hover over the link (without clicking) to see the real address, and never download "
            "attachments from such emails. "
            "Legitimate banks email for information but never ask you to enter your full card "
            "number, password, or OTP through a link. "
            "When in doubt, log in to your bank's official website directly by typing the "
            "address yourself. "
            "If you entered credentials on a fake page, change your net banking password and "
            "contact the bank's fraud team immediately."
        ),
        "keywords": (
            "phishing email, fake email, bank email, email link, account closed email, "
            "update details email, attachment email, spam, suspicious email, email scam"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "What is OTP phishing? Someone asked me to 'confirm' by sharing an OTP.",
        "answer": (
            "OTP phishing is when a fraudster triggers a real transaction on your account and "
            "then calls you pretending to be from the bank/app: 'We detected an unusual "
            "transaction, confirm it by telling me the OTP you just received.' The OTP they "
            "want is exactly what will complete the scammer's own payment. "
            "No one except you should ever see your OTP — never repeat it to anyone, even if "
            "the caller seems to know your name, account number, or recent purchases. "
            "If you shared an OTP: call your bank and 1930 immediately, and check for "
            "unauthorized transactions in your app. "
            "Also report the caller's number to cybercrime.gov.in. Set your app's "
            "transaction limits low so one leak can't empty your account."
        ),
        "keywords": (
            "otp phishing, otp fraud, confirm otp, verify otp, tell me otp, otp leak, "
            "otp given, unusual transaction call, otp share mistake, bank otp"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "A 'bank official' offered me a high-interest FD / investment over the phone.",
        "answer": (
            "No bank sells investment products through unsolicited calls. If a caller claims to "
            "be from your bank with a special FD or 'employee-only' plan and asks you to 'park' "
            "money in a different account 'for higher returns', it's a fraud. "
            "Real deposits stay in your own bank account and appear in your own app/statement. "
            "If you transferred money for such a scheme, report to 1930 and your bank and note "
            "the receiving account. "
            "Always verify offers by visiting your bank branch or official app — and remember "
            "that legitimate FDs never move your money to another account."
        ),
        "keywords": (
            "fake investment call, fd call, high return fd, bank offer call, special scheme, "
            "deposit scam, sip call, investment call, nri scheme"
        ),
    },

    # ------------------------------------------------------------------
    # Category 3: Investment & Misleading Payments
    # ------------------------------------------------------------------
    {
        "category": CATEGORY_INVESTMENT,
        "question": "I invested in a trading app that now asks for more money to 'withdraw' profits.",
        "answer": (
            "You are in a fake trading-app scam. The app is not real — profits shown on screen "
            "are just numbers, and withdrawals are always 'blocked' until you pay more (for "
            "'tax', 'margin', 'withdrawal fee'). That is the scam's core loop. "
            "Do not send one more rupee. Screenshot the app, the chats, your transaction "
            "records, and the app's APK/download link. "
            "Report to 1930 and cybercrime.gov.in immediately and tell your bank the receiving "
            "accounts. "
            "Check SEBI's official list of permitted trading apps/platforms at sebi.gov.in — any "
            "app pushing 'guaranteed returns' or trading outside a licensed broker is a fraud. "
            "These apps often operate from abroad, so recovery is hard — but reporting helps "
            "freeze mule accounts and can prevent others from being scammed."
        ),
        "keywords": (
            "trading app, fake trading, sebi, stock market app, withdrawal fee, pay more to "
            "withdraw, trading profit, share trading, intraday, broker app, ipxo, fyers fake"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "I was asked to invest in crypto/forex with guaranteed profits. Is it safe?",
        "answer": (
            "No investment offers guaranteed profits — and in India, crypto is not regulated, "
            "so there is little protection if you are cheated. Fake crypto/forex platforms show "
            "growing balances to tempt bigger deposits, then freeze withdrawals or disappear. "
            "If you've already invested, stop immediately and gather: platform name, links, "
            "wallet addresses/account numbers you paid to, chat screenshots. "
            "Report to 1930 and cybercrime.gov.in, and inform your bank. "
            "Be extra careful with 'investment mentors' on Telegram/Instagram who promise "
            "weekly returns — they earn by pushing you into scam platforms. "
            "Only invest through regulated channels (SEBI-registered mutual funds, banks, "
            "brokers), and start small enough that you can afford to lose it."
        ),
        "keywords": (
            "crypto, bitcoin, ethereum, usdt, forex, guaranteed profit, investment mentor, "
            "telegram trading, crypto scam, wallet address, cryptocurrency fraud"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "A loan app is harassing me and my contacts over repayment. What do I do?",
        "answer": (
            "Harassing borrowers or their contacts is illegal. Legitimate lenders follow the "
            "RBI's fair practice code — they cannot use abusive language, call at odd hours, or "
            "contact your family/friends/employer, and they must not threaten arrest for a loan "
            "dispute (it's a civil matter). "
            "- Record every call, save every threatening message. "
            "- Complain to the app's RBI-licensed entity (the NBFC behind it) in writing; if the "
            "app has no valid NBFC, it is an illegal lending app — report it. "
            "- Report harassment and illegal recovery on cybercrime.gov.in and to 1930, and "
            "complain to the RBI Sachet portal (sachet.rbi.org.in). "
            "Check if the app has unauthorised access to your contacts/phone — if yes, uninstall "
            "it and change your app permissions; the same app is likely a data-seller too."
        ),
        "keywords": (
            "loan app, loan harassment, recovery agent, loan call, sachet rbi, nbsc, illegal "
            "lender, payday loan, personal loan app, harassment call, threatening borrower"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "I won a lottery/prize and need to pay a fee to receive it. Is this real?",
        "answer": (
            "No lottery or prize you didn't enter is real. The pattern is always the same: "
            "'You won ₹25 lakh / an iPhone!' — then a 'processing fee', 'tax', or 'refundable "
            "deposit' before you can collect. You pay, and the prize never comes. "
            "Real lotteries (state-run) deduct taxes from winnings; nobody asks you to pay "
            "first. "
            "If you already paid, report to 1930 and cybercrime.gov.in with the chats and "
            "payment proof. "
            "If you haven't paid: stop replying, block the number, and remember the golden rule — "
            "you never pay money to receive money."
        ),
        "keywords": (
            "lottery, prize, won money, lucky draw, prize fee, kbc call, kbc scam, lottery "
            "tax, prize claim, never paid fee, prize money"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "I got a Telegram 'task' job — liking videos and earning money. Is it legitimate?",
        "answer": (
            "These 'task' jobs (like YouTube videos, follow Instagram pages, or 'pre-task' "
            "jobs on Telegram/WhatsApp) are scams. The first few tasks pay small real amounts "
            "to build trust, then they push you into 'paid tasks' or 'premium tasks' where you "
            "invest more and more — and finally the group disappears with your money. "
            "You may also be 'assigned' tasks involving receiving and forwarding money — that "
            "makes you a mule account holder. "
            "If you have paid already, stop and report to 1930 and cybercrime.gov.in with the "
            "group name, chats and payments. "
            "If you haven't paid, leave the group and block the account. Legitimate work never "
            "asks you to pay to start earning."
        ),
        "keywords": (
            "task job, part time job, telegram job, whatsapp job, liking videos job, "
            "prepaid task, work from home scam, fake job, task scam, earn money online job, "
            "pre-task"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "I met someone online who is 'in love' and now asks for money. Is this romance fraud?",
        "answer": (
            "Yes — this is romance fraud. Scammers build weeks or months of emotional closeness "
            "on dating apps, Instagram, or WhatsApp, then hit a 'crisis': a sick parent, a "
            "blocked visa, a business emergency, or 'I'm sending you a gift but customs needs "
            "a fee'. They may even do video calls with pre-recorded clips. "
            "Real relationships don't come with payment deadlines, and someone who genuinely "
            "cares will never pressure you to empty your savings. "
            "Stop sending money, do not share account details, and save all chats. "
            "Report to 1930 and cybercrime.gov.in — and talk to a trusted friend or family "
            "member; you have nothing to be ashamed of, the deception was deliberate and "
            "professional."
        ),
        "keywords": (
            "romance scam, love scam, dating app fraud, online boyfriend, online girlfriend, "
            "marriage scam, widower scam, gift customs fee, ship money to lover, catfishing"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "My NRI relative wants to buy property in India and a 'broker' demands advance money.",
        "answer": (
            "NRIs are a favourite target for real-estate fraud: fake brokers show photos and "
            "documents of properties they don't own and collect 'token amounts', 'registration "
            "fees', or 'NRI taxes' in personal accounts, then disappear. "
            "Never pay a broker directly for a property — money should go to the seller's "
            "account only after title verification by a lawyer. "
            "Verify the property documents through the state's official land records site "
            "(e.g., 'Bhoomi'/'iLand' portals) and check the broker's registration. "
            "If money was sent, report to 1930 and cybercrime.gov.in immediately and alert the "
            "bank to freeze the receiving account. "
            "A rule for all real-estate deals: no advance without lawyer-verified title, and "
            "always visit or video-verify the property."
        ),
        "keywords": (
            "nri fraud, real estate fraud, property scam, broker scam, token amount, land "
            "documents, property advance, nri property, plot scam, builder fraud"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "A company asked me to pay for a 'salary verification' or job offer. Is that normal?",
        "answer": (
            "No legitimate employer ever charges you — not for salary verification, not for "
            "'offer letter processing', 'training', 'visa sponsorship', or 'security deposit'. "
            "Salary-verification scams target job seekers after fake interviews; you pay the "
            "'verification fee', and no job ever starts. "
            "Verify the company independently: call their official number from their real "
            "website (not the one in the email), and check on LinkedIn whether the recruiter "
            "actually works there. "
            "If you already paid, report to 1930 and cybercrime.gov.in with the offer letter, "
            "chats, and payment proof. "
            "Remember: money should always flow from the employer to you, never the reverse."
        ),
        "keywords": (
            "salary verification, job scam, fake job offer, offer letter fee, placement fee, "
            "training fee job, hr scam, recruitment fraud, interview scam, visa sponsorship"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "A door-to-door agent sold me a policy/health card and took cash. Is it valid?",
        "answer": (
            "Doorstep-selling frauds push fake policies, health cards, solar schemes, or "
            "'government schemes' to elders, take cash, and leave a receipt with a number that "
            "stops working. "
            "Verify immediately: call the company's official helpline and the IRDAI/regulator "
            "website (for insurance) or the official scheme portal — a genuine policy gets "
            "documented and shows up in the company's records within days. "
            "If it's fake, you will often find the same agent has visited multiple homes in "
            "your area — collect neighbours' details and report together. "
            "Report to cybercrime.gov.in and the police with the agent's photo (if available), "
            "phone number, and receipt. "
            "Rule for elders: never pay cash to an agent at the door; always insist on a "
            "written, verified policy and payment through official channels."
        ),
        "keywords": (
            "doorstep scam, door to door, fake policy, health card scam, insurance agent, "
            "cash payment, solar scheme scam, government scheme scam, elder target, fake "
            "receipt"
        ),
    },
    {
        "category": CATEGORY_INVESTMENT,
        "question": "My insurance/health card stopped working and I don't know the company.",
        "answer": (
            "If you bought a 'health card' or policy from an unknown agent and now can't reach "
            "them, it was likely a fake. First, find the policy document and check the insurer's "
            "name and policy number. "
            "Search the insurer on IRDAI's official site (irdai.gov.in) and call their official "
            "helpline to check if the policy exists. "
            "If the company itself is not registered, you were sold a fraud — report to the "
            "police and cybercrime.gov.in, and complain to IRDAI's consumer helpline. "
            "Also check your SMS/email records for the premium payment receipt — if you paid a "
            "person directly instead of the company, that's a strong fraud signal. "
            "For genuine plans, insurers maintain records and a valid policy is never "
            "'unfindable'."
        ),
        "keywords": (
            "insurance fraud, health card fraud, fake insurance, policy not working, irdai "
            "complaint, unregistered insurer, mediclaim scam, policy verification"
        ),
    },

    # ------------------------------------------------------------------
    # Cross-cutting: protection, process, and support
    # ------------------------------------------------------------------
    {
        "category": CATEGORY_PAYMENT,
        "question": "How can I protect my UPI and bank accounts from fraud?",
        "answer": (
            "- Set a low daily UPI/UPI AutoPay limit and card limit in your banking app — even "
            "if your phone is compromised, damage is capped. "
            "- Use two-factor/extra authentication (App PIN, fingerprint) and never share OTP "
            "or UPI PIN with anyone. "
            "- Keep the UPI app locked behind an app lock, and switch 'ON' only the payment "
            "apps you actually use. "
            "- Don't install APKs sent via WhatsApp/Telegram, and update the phone OS and apps "
            "regularly. "
            "- Use separate emails/passwords for banking and use a secure password manager for "
            "social media. "
            "The rule of thumb: the scammer needs your PIN or OTP to move money — make sure "
            "they can never get it."
        ),
        "keywords": (
            "protection, safety tips, prevent fraud, upi limit, set limits, two factor, 2fa, "
            "security tips, safe banking, app lock, auto pay, how to stay safe"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "What is the complaint escalation timeline if my bank doesn't resolve my fraud case?",
        "answer": (
            "Here is the usual ladder, keep each complaint reference handy: "
            "- Day 0: Report to 1930 + your bank (freeze), then file on cybercrime.gov.in. "
            "- Within 30 days: the bank must send a provisional 'transaction status' via NCRP "
            "and its own channels. "
            "- Within 90 days: the receiving bank must credit back eligible fraudulent amounts; "
            "if not, ask for the rejection reason in writing. "
            "- If the bank rejects or is silent: complain to the bank's nodal officer, then "
            "escalate to the RBI Banking Ombudsman (free, online at cms.rbi.org.in) within 1 "
            "year of the transaction. "
            "You can also approach the local cybercrime police station and your MP's grievance "
            "desk for delayed NCRP cases. "
            "Keep a timeline file with every complaint number — it makes escalation fast and "
            "formal."
        ),
        "keywords": (
            "timeline, escalation, follow up, bank not responding, ombudsman, rbi complaint, "
            "nodal officer, 90 days, 30 days, cms.rbi.org.in, refund deadline"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "I feel ashamed and embarrassed about being scammed. Is this my fault?",
        "answer": (
            "Please hear this: being scammed is never your fault. Professional fraudsters "
            "rehearse scripts, use real-looking numbers and apps, and weaponise fear and trust — "
            "they trick lakhs of educated, smart people every year. "
            "The best thing you can do now is take care of yourself: talk to a friend or family "
            "member, and don't scroll alone at 2am replaying it. "
            "Filing the complaint is your act of strength, not shame — every report helps "
            "freeze accounts and stops the next victim. "
            "If you are feeling panic, helplessness, or can't sleep, that's a normal reaction "
            "to a real violation — consider talking to a counsellor; in India you can call "
            "Tele-MANAS (14416) or 1-800-891-4416, free and confidential. "
            "You did the right thing by reaching out. One step at a time — and we're here with "
            "you."
        ),
        "keywords": (
            "emotional, guilt, shame, embarrassed, depressed, anxious, stress, mental health, "
            "counselling, tele-manas, support, feel bad, scared, hopeless, kya karun"
        ),
    },
    {
        "category": CATEGORY_PHISHING,
        "question": "How do I protect my elderly parents from fraud calls and messages?",
        "answer": (
            "Elders are the most targeted group, so prevention is a family routine: "
            "- Set up call/name spoofing awareness: tell them government agencies never call "
            "for money, and a 'yes' to any 'confirmation' question is not needed. "
            "- Keep their bank app limits low, enable SMS alerts for every transaction, and "
            "review statements with them monthly. "
            "- Teach them one rule: never share OTP/PIN with anyone, even if the caller says "
            "'from the bank' or 'your son asked'. "
            "- Help them enable 'report spam' on their phone and add family numbers to "
            "'Trusted Contacts'. "
            "If a call seems suspicious, tell them to say 'I will call you back' and call you "
            "first — the extra minute of human verification stops most scams. "
            "If something already happened, call 1930 and report immediately; reassure them "
            "it's not their fault."
        ),
        "keywords": (
            "elderly, parents, senior citizens, elders, grandparent, older people, protect "
            "family, family safety, teach parents, senior scam"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "My company paid an invoice to a fraudster pretending to be a vendor. What now?",
        "answer": (
            "This is invoice/CEO fraud (business email compromise). Act immediately: "
            "- Alert your bank's corporate desk and dial 1930 to freeze the receiving account. "
            "- Preserve the original vendor email (headers included) and the payment proof — "
            "don't edit or delete anything. "
            "- Tell the real vendor so they can warn their other customers. "
            "- File a complaint on cybercrime.gov.in and consider a formal police complaint; "
            "insurance may cover part of the loss. "
            "For the future, implement a two-person verification rule for any change of bank "
            "details and payments above a threshold — most such frauds succeed through a single "
            "approval. "
            "Also scan your email for similar pending invoices, because scammers often try "
            "twice."
        ),
        "keywords": (
            "invoice fraud, business email compromise, bec, vendor fraud, fake invoice, "
            "ceo fraud, corporate fraud, supplier payment, changed bank details, accounts "
            "payable"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "What should I do if I am on a suspicious call RIGHT NOW or about to pay?",
        "answer": (
            "Act fast — every second counts. If a caller is pressuring you to 'stay on the "
            "line', 'not tell anyone', or 'act before the deadline', that is the scammer's "
            "trap: they need you online and alone. "
            "- Disconnect the call immediately and switch off the video. "
            "- Do NOT pay anything, do NOT share OTP/PIN, do NOT install any app, do NOT show "
            "your screen. "
            "- Dial 1930 now to report the number, and inform your bank that a fraud attempt "
            "happened. "
            "If money has already been taken, follow the 10-minute rule: bank call + 1930 "
            "first, evidence second, NCRP complaint after. "
            "Take a deep breath — you are in control, and the fraudster only has power while "
            "you keep the call going."
        ),
        "keywords": (
            "right now, on call now, urgent, about to pay, just got call, current fraud, "
            "live scam, in progress, help immediately, emergency, danger"
        ),
    },
    {
        "category": CATEGORY_PAYMENT,
        "question": "Where can I file an FIR offline if online reporting isn't working?",
        "answer": (
            "You can always visit your local police station in person — under the law, every "
            "police station must register an FIR or a Zero FIR (a complaint that is forwarded "
            "to the right jurisdiction) for cyber fraud. "
            "Carry a printout of your NCRP complaint, transaction proofs, and the scammer's "
            "details. "
            "If the station refuses to register, you can complain in writing to the "
            "Superintendent of Police / Commissioner of Police, or approach the court under "
            "Section 156(3) CrPC (now BNSS) for a direction. "
            "Keep copies of everything you submit and note the person who received your "
            "complaint. "
            "Your 1930/NCRP reference and the FIR together form the strongest legal basis for "
            "your refund request and any recovery proceedings."
        ),
        "keywords": (
            "fir, police station, zero fir, offline complaint, court, bnss, 156 3, sp office, "
            "police complaint, file case"
        ),
    },
]

assert len(FAQ_CORPUS) >= 36, "FAQ corpus must have at least 36 entries"

if __name__ == "__main__":
    from collections import Counter

    counts = Counter(entry["category"] for entry in FAQ_CORPUS)
    for cat, n in counts.items():
        print(f"{n:>2}  {cat}")
    print(f"TOTAL: {len(FAQ_CORPUS)} entries")
