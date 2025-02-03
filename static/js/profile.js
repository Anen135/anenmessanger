document.getElementById('profileImage').addEventListener('change', function(event) {
    const file = event.target.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('avatar', file); // Ключ должен совпадать с тем, что ожидает сервер

        fetch('/profile/avatar/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при загрузке аватара');
            }
            return response.text(); // Или response.json()
        })
        .then(data => {
            console.log('Успешно загружено:', data);

            // Обновляем аватар на странице без перезагрузки
            document.getElementById("profileImage").src = data;
            location.reload();
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    }
});


// Функция для отправки данных на сервер
async function sendData(url, method, data) {
    try {
        const response = await fetch(url, {
            method: method,
            body: data,
        });

        // Если ответ - изображение, обрабатываем как blob
        if (response.headers.get("Content-Type").startsWith("image/")) {
            const blob = await response.blob();
            const imgURL = URL.createObjectURL(blob);
            // Тут вы можете обновить изображение на странице, например:
            document.getElementById("profileImage").src = imgURL;
            alert('Изображение успешно загружено!');
        } else {
            const result = await response.json();
            if (result.success) {
                alert('Изменения успешно сохранены!');
            } else {
                alert(result.error || 'Произошла ошибка!');
            }
        }

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка сети!');
    }
}


// Загрузка аватара
document.getElementById('profileImage').addEventListener('change', function () {
    const formData = new FormData();
    formData.append('avatar', this.files[0]);

    sendData('/profile/avatar/upload', 'POST', formData);
});

// Сохранение личных данных
document.querySelector('#list-personal form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append('fullName', document.getElementById('fullName').value);
    formData.append('email', document.getElementById('email').value);
    formData.append('about', document.getElementById('about').value);

    sendData('/profile/update', 'POST', formData);
});

// Обновление пароля
document.querySelector('#list-security form').addEventListener('submit', function (e) {
    e.preventDefault();

    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (newPassword !== confirmPassword) {
        alert('Пароли не совпадают!');
        return;
    }

    const formData = new FormData();
    formData.append('currentPassword', currentPassword);
    formData.append('newPassword', newPassword);

    sendData('/profile/password/update', 'POST', formData);
});

// Настройки уведомлений
document.querySelector('#list-notifications form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append('emailNotifications', document.getElementById('emailNotifications').checked);
    formData.append('pushNotifications', document.getElementById('pushNotifications').checked);

    sendData('/profile/notifications/update', 'POST', formData);
});
