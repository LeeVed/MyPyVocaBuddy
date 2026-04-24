importScripts('https://www.gstatic.com/firebasejs/9.6.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.0/firebase-messaging-compat.js');


firebase.initializeApp({
    apiKey: "AIzaSyDzl27PgyWfG8lNZcxUjo4ceD8bIMmfwtg",
    authDomain: "mypyvocabuddy.firebaseapp.com",
    projectId: "mypyvocabuddy",
    storageBucket: "mypyvocabuddy.firebasestorage.app",
    messagingSenderId: "874445385138",
    appId: "1:874445385138:web:a0d9174b056b83f017c8ab"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    console.log("Получено фоновое сообщение:", payload);
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: "/static/images/icon.png"
    };
    self.registration.showNotification(notificationTitle, notificationOptions);
});
