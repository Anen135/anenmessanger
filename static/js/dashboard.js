$(document).ready(function() {
    // Обработчик клика на кнопку "Создать группу"
    $('#create-group-button').on('click', function() {
        // Открытие модального окна для создания группы
        $('#createGroupModal').modal('show');
    });
    // Обработчик события для кнопки создания группы
    $('#confirmCreateGroup').click(function() {
        // Получаем имя группы из поля ввода
        var groupName = $('#groupName').val().trim();

        // Если имя группы пустое, показываем ошибку
        if (!groupName) {
            $('#createGroupError').text('Пожалуйста, введите имя группы.').removeClass('d-none');
            return;
        }

        // Отправляем запрос на сервер через сокеты
        socket.emit('create_group', { name: groupName });

        // Очистка поля ввода и скрытие ошибки
        $('#createGroupError').addClass('d-none');
        $('#groupName').val('');
    });

    // Обработчик ответа от сервера
    socket.on('create_group_response', function(data) {
        if (data.error) {
            // Если произошла ошибка, выводим сообщение об ошибке
            $('#createGroupError').text(data.error).removeClass('d-none');
        } else if (data.success) {
            // Если группа была успешно создана, закрываем модальное окно
            $('#createGroupModal').modal('hide');

            // Выводим уведомление об успешном создании
            alert(data.message);

            // Здесь можно добавить логику для обновления UI или перехода в чат группы
        }
    });
});

$(document).ready(function() {
    // Обработчики переключения вкладок
    $('#friend-requests-tab').click(function() {
        loadFriendRequests(); // Загружаем запросы на дружбу
    });

    $('#group-requests-tab').click(function() {
        loadGroupRequests(); // Загружаем запросы на присоединение к группе
    });

    // Обработчик кнопки "Запросы"
    $('#show-requests-button').click(function() {
        $('#requestsModal').modal('show');
        loadFriendRequests(); // Загружаем запросы на дружбу по умолчанию при открытии модального окна
    });

    // Функция для загрузки запросов на дружбу
    function loadFriendRequests() {
        $.ajax({
            url: '/get_friend_requests',  // Эндпоинт для получения запросов на дружбу
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    $('#requests-list').empty(); // Очистка предыдущих запросов
                    
                    // Добавление входящих запросов
                    response.incoming_requests.forEach(function(request) {
                        $('#requests-list').append(
                            `<li>${request.sender_username} 
                            <button class="btn btn-sm btn-success" onclick="respondFriendRequest(${request.id}, 'accept')">Принять</button>
                            <button class="btn btn-sm btn-danger" onclick="respondFriendRequest(${request.id}, 'decline')">Отклонить</button></li>`
                        );
                    });

                    // Добавление исходящих запросов
                    response.outgoing_requests.forEach(function(request) {
                        $('#requests-list').append(
                            `<li>${request.receiver_username} 
                            <button class="btn btn-sm btn-danger" onclick="respondFriendRequest(${request.id}, 'cancel')">Отменить</button></li>`
                        );
                    });
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Ошибка при получении запросов на дружбу.');
            }
        });
    }

    // Функция для отклика на запросы на дружбу
    window.respondFriendRequest = function(requestId, action) {
        $.ajax({
            url: `/respond_friend_request/${requestId}/${action}`,
            type: 'GET',
            success: function(response) {
                if (response.success) {
                    loadFriendRequests(); // Перезагружаем запросы на дружбу
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Ошибка при обработке запроса на дружбу.');
            }
        });
    };

// Функция для загрузки запросов на присоединение к группе
function loadGroupRequests() {
    $.ajax({
        url: '/get_group_requests',  // Эндпоинт для получения запросов на присоединение (согласуем с сервером)
        type: 'GET',
        success: function(response) {
            if (response.success) {
                $('#requests-list').empty(); // Очистка предыдущих запросов

                // Добавление входящих запросов на присоединение к группе
                response.incoming_requests.forEach(function(request) {
                    $('#requests-list').append(
                        `<li>${request.group_name} 
                        <button class="btn btn-sm btn-success" onclick="respondGroupRequest(${request.id}, 'accept')">Принять</button>
                        <button class="btn btn-sm btn-danger" onclick="respondGroupRequest(${request.id}, 'decline')">Отклонить</button></li>`
                    );
                });

                // Добавление исходящих запросов на присоединение к группе
                response.outgoing_requests.forEach(function(request) {
                    $('#requests-list').append(
                        `<li>${request.group_name} 
                        <button class="btn btn-sm btn-danger" onclick="respondGroupRequest(${request.id}, 'cancel')">Отменить</button></li>`
                    );
                });
            } else {
                alert(response.message);
            }
        },
        error: function() {
            alert('Ошибка при получении запросов на присоединение к группе.');
        }
    });
}

// Функция для отклика на запросы на присоединение к группе
window.respondGroupRequest = function(requestId, action) {
    $.ajax({
        url: `/respond_group_request/${requestId}/${action}`, // Используем POST для изменения статуса запроса
        type: 'POST',  // Изменил на POST, чтобы соответствовать серверному коду
        success: function(response) {
            if (response.success) {
                loadGroupRequests(); // Перезагружаем запросы на присоединение
            } else {
                alert(response.message);
            }
        },
        error: function() {
            alert('Ошибка при обработке запроса на присоединение к группе.');
        }
    });
};

});
