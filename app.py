// single-backend-web-sdk.js
const express = require('express');
const bodyParser = require('body-parser');
const fetch = require('node-fetch');
const { initializeApp } = require('firebase/app');
const { getFirestore, doc, getDoc, setDoc, updateDoc, query, collection, orderBy, limit, getDocs, Timestamp } = require('firebase/firestore');

// --------------------- FIREBASE WEB CONFIG ---------------------
const firebaseConfig = {
    apiKey: "AIzaSyA79lkNe6Bx4NwlLhyxdlfTxKd3rnwoXhI",
    authDomain: "movie-website-5cbeb.firebaseapp.com",
    projectId: "movie-website-5cbeb",
    storageBucket: "movie-website-5cbeb.firebasestorage.app",
    messagingSenderId: "553314999655",
    appId: "1:553314999655:web:c96e91f788d55608f8e3c2"
};

// Initialize Firebase
const appFirebase = initializeApp(firebaseConfig);
const db = getFirestore(appFirebase);

// --------------------- TELEGRAM SETUP ---------------------
const TELEGRAM_TOKEN = '8529856161:AAFg3N3R1uwNcuaHds-rUJeZFFgA7kVTECM';
const TELEGRAM_API = `https://api.telegram.org/bot${TELEGRAM_TOKEN}`;

// --------------------- EXPRESS SETUP ---------------------
const app = express();
app.use(bodyParser.json());

// --------------------- TELEGRAM WEBHOOK ---------------------
app.post('/webhook', async (req, res) => {
    const message = req.body.message;
    if (!message) return res.sendStatus(200);

    const chatId = message.chat.id;
    const text = message.text;

    // Extract referral code from /start
    const referralCode = text && text.startsWith('/start ') ? text.split(' ')[1] : null;

    const userRef = doc(db, 'users', chatId.toString());
    const userSnap = await getDoc(userRef);

    if (!userSnap.exists()) {
        // Create user
        await setDoc(userRef, {
            chatId: chatId,
            referral: referralCode || null,
            referrals: 0,
            createdAt: Timestamp.now()
        });

        // Update referrer
        if (referralCode) {
            const refUserRef = doc(db, 'users', referralCode);
            const refUserSnap = await getDoc(refUserRef);
            if (refUserSnap.exists()) {
                const currentCount = refUserSnap.data().referrals || 0;
                await updateDoc(refUserRef, { referrals: currentCount + 1 });

                // Notify referrer
                await fetch(`${TELEGRAM_API}/sendMessage`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chat_id: referralCode,
                        text: `🎉 Someone used your referral link! Total referrals: ${currentCount + 1}`
                    })
                });
            }
        }
    }

    // Reply to user with referral code
    await fetch(`${TELEGRAM_API}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chat_id: chatId,
            text: `Welcome! Your referral code is: ${chatId}\nShare /start ${chatId} to invite others!`
        })
    });

    res.sendStatus(200);
});

// --------------------- REFERRAL LEADERBOARD ---------------------
app.get('/leaderboard', async (req, res) => {
    const q = query(collection(db, 'users'), orderBy('referrals', 'desc'), limit(10));
    const querySnapshot = await getDocs(q);
    const leaderboard = [];
    querySnapshot.forEach(docSnap => {
        const data = docSnap.data();
        leaderboard.push({ chatId: data.chatId, referrals: data.referrals });
    });
    res.json(leaderboard);
});

// --------------------- START SERVER ---------------------
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
