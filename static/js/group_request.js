// Универсальный обработчик для добавления и удаления пользователей из группы
$(document).on('click', '.add-user-btn', function () {
    const groupId = $(this).data('group-id');

    // Устанавливаем groupId и действие в модальное окно
    $('#add-user-modal').data('group-id', groupId);
    $('#add-user-modal').data('action', 'add_users');

    // Обновляем заголовок модального окна для добавления
    $('#add-user-modal .modal-title').text('Добавить пользователей в группу');

    // Открываем модальное окно
    $('#add-user-modal').modal('show');

    // Отправляем запрос на сервер для получения списка пользователей
    $.ajax({
        url: '/get_users_for_group',
        method: 'GET',
        data: { group_id: groupId },
        success: function (response) {
            if (response.success) {
                // Заполняем список пользователей
                const usersList = $('#users-list');
                usersList.empty();
                response.users.forEach(user => {
                    usersList.append(`
                        <li>
                            <input type="checkbox" name="user" value="${user.id}" /> ${user.username}
                        </li>
                    `);
                });
            } else {
                alert('Ошибка при загрузке списка пользователей');
            }
        },
        error: function () {
            alert('Ошибка при выполнении запроса к серверу');
        }
    });
});

// Обработчик переключения на режим удаления пользователей -
$('#remove-users').click(function (event) {
    const groupId = $('#add-user-modal').data('group-id');
    // Предотвращаем стандартное поведение кнопки
    event.preventDefault();
    event.stopPropagation();
    
    // Меняем действие на "удалить пользователей"
    $('#add-user-modal').data('action', 'remove_users');

    // Обновляем заголовок модального окна
    $('#add-user-modal .modal-title').text('Удалить пользователей из группы');

    // Скрываем кнопку "Добавить" и показываем кнопку "Удалить"
    $('#add-users').removeClass('d-none');
    $('#remove-users').addClass('d-none');
    if (!confirm("При удалений себя из группы группа со всеми участниками будет удалена. Продолжить?")){
        return
    }

    // Отправляем запрос на сервер для получения списка пользователей, которых можно удалить
    $.ajax({
        url: '/get_users_in_group',
        method: 'GET',
        data: { group_id: groupId },
        success: function (response) {
            console.log(response);
            if (response.success) {
                // Заполняем список пользователей для удаления
                const usersList = $('#users-list');
                usersList.empty();
                response.users.forEach(user => {
                    usersList.append(`
                        <li>
                            <input type="checkbox" name="user" value="${user.id}" /> ${user.username}
                        </li>
                    `);
                });
            } else {
                alert('Ошибка при загрузке списка пользователей для удаления');
            }
        },
        error: function () {
            alert('Ошибка при выполнении запроса к серверу');
        }
    });
});

// Обработчик переключения на режим добавления пользователей +
$('#add-users').click(function (event) {
    // Предотвращаем стандартное поведение кнопки
    event.preventDefault();
    event.stopPropagation();
    // Возвращаем режим добавления
    $('#add-user-modal').data('action', 'add_users');
    
    // Обновляем заголовок
    $('#add-user-modal .modal-title').text('Добавить пользователей в группу');

    // Скрываем кнопку "Удалить" и показываем кнопку "Добавить"
    $('#add-users').addClass('d-none');
    $('#remove-users').removeClass('d-none');
    
    // Отправляем запрос для получения списка пользователей для добавления
    const groupId = $('#add-user-modal').data('group-id');
    $.ajax({
        url: '/get_users_for_group',
        method: 'GET',
        
        data: { group_id: groupId },
        success: function (response) {
            if (response.success) {
                // Заполняем список пользователей для добавления
                const usersList = $('#users-list');
                usersList.empty();
                response.users.forEach(user => {
                    usersList.append(`
                        <li>
                            <input type="checkbox" name="user" value="${user.id}" /> ${user.username}
                        </li>
                    `);
                });
            } else {
                alert('Ошибка при загрузке списка пользователей для добавления');
            }
        },
        error: function () {
            alert('Ошибка при выполнении запроса к серверу');
        }
    });
});

// Обработчик кнопки "Выполнить" (для добавления или удаления пользователей)
$('#add-users-button').click(function () {
    const groupId = $('#add-user-modal').data('group-id');  // ID группы
    const action = $('#add-user-modal').data('action');     // Режим работы: добавление или удаление

    // Собираем ID выбранных пользователей как числа
    const selectedUserIds = [];
    $('#users-list input[name="user"]:checked').each(function () {
        selectedUserIds.push(parseInt($(this).val(), 10));  // Преобразуем в числа
    });

    if (selectedUserIds.length === 0) {
        alert('Выберите хотя бы одного пользователя!');
        return;
    }

    if (action === 'add_users') {
        // Отправляем запрос на присоединение для каждого выбранного пользователя
        selectedUserIds.forEach(userId => {
            $.ajax({
                url: '/send_group_join_request',
                method: 'POST',
                data: {
                    group_id: groupId,
                    user_id: userId
                },
                success: function (response) {
                    if (response.success) {
                        alert(`Запрос на добавление пользователя успешно отправлен`);
                    } else {
                        alert(`Ошибка при отправке запроса: ${response.message}`);
                    }
                },
                error: function () {
                    alert('Ошибка при выполнении запроса на сервер');
                }
            });
        });
    } else if (action === 'remove_users') {
        // Удаление пользователей (происходит сразу)
        $.ajax({
            url: '/remove_users_from_group',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                group_id: groupId,
                users: selectedUserIds
            }),
            success: function (response) {
                if (response.success) {
                    alert(response.message);
                } else {
                    alert('Ошибка при удалении пользователей: ' + response.error);
                }
            },
            error: function () {
                alert('Ошибка при выполнении запроса на сервер');
            }
        });
    }

    // Закрытие модального окна после выполнения действия
    $('#add-user-modal').modal('hide');
});

