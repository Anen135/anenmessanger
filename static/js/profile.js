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
            return response.text(); // Или response.json(), если сервер возвращает JSON
        })
        .then(data => {
            console.log('Успешно загружено:', data);

            // Обновляем аватар на странице без перезагрузки
            const avatarImg = document.querySelector('.profile-img');
            const uniqueParam = new Date().getTime(); // Чтобы избежать кеширования
            avatarImg.src = `/static/${data}?v=${uniqueParam}`;
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    }
});
